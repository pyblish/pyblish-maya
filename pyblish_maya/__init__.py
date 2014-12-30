"""
Pyblish for Maya

Attributes:
    GUI: Which GUI to associate with the option-box within Maya's file-menu.
    log: Current logger

"""

import os
import atexit
import random
import logging
import inspect
import threading
import subprocess

# Pyblish libraries
import pyblish.api

# Host libraries
from maya import mel
from maya import cmds

# Local libraries
from . import plugins

GUI = None
log = logging.getLogger('pyblish')


def show(console=False):
    if not GUI:
        raise ValueError("No GUI registered")

    if not "ENDPOINT_PORT" in os.environ:
        raise ValueError("Pyblish start-up script doesn't seem to "
                         "have been run, could not find the PORT variable")

    host = "Maya"
    port = os.environ["ENDPOINT_PORT"]

    CREATE_NO_WINDOW = 0x08000000
    proc = subprocess.Popen(["python", "-m", "pyblish_qml.app",
                             "--host", host,
                             "--port", str(port)],
                            creationflags=CREATE_NO_WINDOW if not console else 0)

    # Kill child process on Maya exit
    def kill_child():
        proc.kill()

    atexit.register(kill_child)


def setup():
    """Setup integration"""
    # Underscore prevents makes it less visible from within Maya

    if has_endpoint() and has_frontend():
        setup_endpoint()
        setup_frontend()
        print "pyblish: Setting up frontend"
    else:
        pass

    setup_integration()


def has_endpoint():
    try:
        __import__("pyblish_endpoint.server")
        __import__("pyblish_endpoint.service")
    except ImportError:
        return False
    return True


def has_frontend():
    try:
        __import__("pyblish_qml")
    except ImportError:
        return False
    return True


def setup_endpoint():
    from . import service

    import pyblish_endpoint.server
    import pyblish_endpoint.service

    # Listen for externally running interfaces
    port = random.randint(6000, 7000)

    def server():
        pyblish_endpoint.server.start_production_server(
            service=service.MayaService,
            port=port)

    worker = threading.Thread(target=server)
    worker.daemon = True
    worker.start()

    # Store reference to port for frontend(s)
    os.environ["ENDPOINT_PORT"] = str(port)

    print "pyblish: Endpoint running @ %i" % port


def setup_frontend():
    register_gui("pyblish_qml")


def setup_integration():
    register_plugins()

    # If a frontend is installed, it will be added
    # to the menu as an option-box.
    add_to_filemenu()
    print "pyblish: Integration loaded.."


def register_plugins():
    # Register accompanying plugins
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.register_plugin_path(plugin_path)
    log.info("Registered %s" % plugin_path)


def register_gui(gui):
    """Register GUI

    Inform Maya that there is a GUI for Pyblish.

    Arguments:
        gui (str): Name of callable python package/module

    """

    assert isinstance(gui, basestring)
    global GUI
    GUI = gui


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

    from maya import cmds

    # We'll need to re-import here, due to this being called
    # in a deferred call by Maya during idle, it won't have access
    # to other variables declared in this module.
    import pyblish
    import pyblish_maya

    def filemenu_handler(event):
        import pyblish.main

        if event == "publish":
            pyblish.main.publish_all()

        if event == "gui":
            pyblish_maya.show()

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

    if pyblish_maya.GUI is not None:
        cmds.menuItem('pyblishGui',
                      optionBox=True,
                      insertAfter="pyblishScene",
                      command=lambda _: filemenu_handler("gui"))

    cmds.menuItem('validateScene',
                  label='Validate',
                  insertAfter='pyblishScene',
                  command=lambda _: filemenu_handler("validate"))
    cmds.menuItem('pyblishCloseDivider',
                  insertAfter='validateScene',
                  divider=True)
