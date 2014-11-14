# Standard library
import os
import inspect
import logging
import contextlib

# Pyblish libraries
import pyblish.api

# Integration libraries
import pyblish_maya

# Host libraries
from maya import mel
from maya import cmds

log = logging.getLogger('pyblish')


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context

    Example:
        >>> with maintained_selection():
        ...     # Modify selection
        ...     cmds.select('node', replace=True)
        >>> # Selection restored

    """

    previous_selection = cmds.ls(selection=True)
    try:
        yield
    finally:
        if previous_selection:
            cmds.select(previous_selection,
                        replace=True,
                        noExpand=True)
        else:
            cmds.select(deselect=True,
                        noExpand=True)


def register_plugins():
    # Register accompanying plugins
    package_path = os.path.dirname(pyblish_maya.__file__)
    plugin_path = os.path.join(package_path, 'plugins')

    pyblish.api.register_plugin_path(plugin_path)
    log.info("Registered %s" % plugin_path)


def register_gui(gui):
    """Register GUI

    Inform Maya that there is a GUI for Pyblish.

    Arguments:
        gui (str): Name of callable python package/module

    """

    assert isinstance(gui, basestring)
    pyblish_maya.gui = gui


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

    def filemenu_handler(event):
        import pyblish.main

        if event == "publish":
            pyblish.main.publish_all()

        if event == "gui":
            pyblish_maya.launch_gui()

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

    if pyblish_maya.gui is not None:
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


def launch_gui():
    if not pyblish_maya.gui:
        raise ValueError("No GUI registered")

    if not "ENDPOINT_PORT" in os.environ:
        raise ValueError("Pyblish start-up script doesn't seem to "
                         "have been run, could not find the PORT variable")

    host = "Maya"
    port = os.environ["ENDPOINT_PORT"]
    gui = __import__(pyblish_maya.gui)
    gui.run(host, port, async=True)
