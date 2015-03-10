"""Pyblish for Maya

Attributes:
    log: Current logger

"""

import os
import logging
import inspect
import subprocess

# Pyblish libraries
import pyblish.api

# Host libraries
from maya import mel
from maya import cmds

# Local libraries
from . import lib
from . import plugins

log = logging.getLogger('pyblish')

cached_process = None


def show(console=False, prefer_cached=True):
    """Show the Pyblish graphical user interface

    An interface may already have been loaded; if that's the
    case, we favour it to launching a new unless `prefer_cached`
    is False.

    """

    if cached_process and prefer_cached:
        return _show_cached()
    return _show_new(console)


def _show_cached():
    """Display cached gui

    A GUI is cached upon first being shown, or when pre-loaded.

    """

    import pyblish_endpoint.client

    pyblish_endpoint.client.request("show")

    return cached_process


def _show_new(console=False):
    """Create and display a new instance of the Pyblish QML GUI"""
    try:
        port = os.environ["ENDPOINT_PORT"]
    except KeyError:
        raise ValueError("Pyblish start-up script doesn't seem to "
                         "have been run, could not find the PORT variable")

    pid = os.getpid()
    kwargs = dict(args=["python", "-m", "pyblish_qml",
                        "--port", port, "--pid", str(pid)])

    if not console and os.name == "nt":
        kwargs["creationflags"] = lib.CREATE_NO_WINDOW

    log.info("Creating a new instance of Pyblish QML")
    proc = subprocess.Popen(**kwargs)

    global cached_process
    cached_process = proc

    return proc


def setup(preload=True):
    """Setup integration

    Registers Pyblish for Maya plug-ins and appends an item to the File-menu

    """

    register_plugins()

    try:
        port = setup_endpoint()

        if preload:
            pid = os.getpid()
            preload_(port, pid)

    except:
        log.info("pyblish: Running headless")

    add_to_filemenu()

    log.info("pyblish: Integration loaded..")


def preload_(port, pid=None):
    pid = os.getpid()

    kwargs = dict(args=["python", "-m", "pyblish_qml",
                        "--port", str(port), "--pid", str(pid),
                        "--preload"])

    if os.name == "nt":
        kwargs["creationflags"] = lib.CREATE_NO_WINDOW

    proc = subprocess.Popen(**kwargs)

    global cached_process
    cached_process = proc

    return proc


def setup_endpoint():
    """Start Endpoint

    Raises:
        ImportError: If Pyblish Endpoint is not available

    """

    from service import MayaService
    from pyblish_endpoint import server

    port = lib.find_next_port()
    server.start_async_production_server(service=MayaService, port=port)
    os.environ["ENDPOINT_PORT"] = str(port)

    log.info("pyblish: Endpoint running @ %i" % port)

    return port


def register_plugins():
    # Register accompanying plugins
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.register_plugin_path(plugin_path)
    log.info("pyblish: Registered %s" % plugin_path)


def add_to_filemenu():
    """Add Pyblish to file-menu

    .. note:: We're going a bit hacky here, probably due to my lack
        of understanding for `evalDeferred` or `executeDeferred`,
        so if you can think of a better solution, feel free to edit.

    """

    # As Maya builds its menus dynamically upon being accessed,
    # we force its build here prior to adding our entry using it's
    # native mel function call.
    mel.eval("evalDeferred buildFileMenu")

    # Serialise function into string
    script = inspect.getsource(_add_to_filemenu)
    script += "\n_add_to_filemenu()"

    if hasattr(cmds, 'about') and not cmds.about(batch=True):
        # If cmds doesn't have any members, we're most likely in an
        # uninitialized batch-mode. It it does exists, ensure we
        # really aren't in batch mode.
        cmds.evalDeferred(script)


def _add_to_filemenu():
    """Helper function for the above :func:add_to_filemenu()

    This function is serialised into a string and passed on
    to evalDeferred above.

    """

    import sys
    from maya import cmds

    # We'll need to re-import here, due to this being called
    # in a deferred call by Maya during idle, it won't have access
    # to other variables declared in this module.
    import pyblish
    import pyblish.main
    import pyblish_maya

    def filemenu_handler(event):

        if event == "publish":
            try:
                pyblish_maya.show()
            except Exception as e:
                sys.stderr.write("Tried launching GUI, but failed.\n")
                sys.stderr.write("Message was: %s\n" % e)
                sys.stderr.write("Publishing in headless mode instead.\n")

                pyblish.main.publish_all()

        if event == "validate":
            pyblish.main.validate_all()

    cmds.menuItem('pyblishOpeningDivider',
                  divider=True,
                  insertAfter='saveAsOptions',
                  parent='mainFileMenu')

    cmds.menuItem('pyblishScene',
                  insertAfter='pyblishOpeningDivider',
                  label='Publish',
                  command=lambda _: filemenu_handler("publish"))

    cmds.menuItem('validateScene',
                  label='Validate',
                  insertAfter='pyblishScene',
                  command=lambda _: filemenu_handler("validate"))

    cmds.menuItem('pyblishCloseDivider',
                  insertAfter='validateScene',
                  divider=True)
