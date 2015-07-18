# Standard library
import os
import inspect
import contextlib

# Pyblish libraries
import pyblish.api
import pyblish_integration

# Host libraries
from maya import mel
from maya import cmds
from maya import utils

# Local libraries
import plugins


show = pyblish_integration.show


def setup(console=False):
    """Setup integration

    Registers Pyblish for Maya plug-ins and appends an item to the File-menu

    Attributes:
        preload (bool): Preload the current GUI
        console (bool): Display console with GUI

    """

    def threaded_wrapper(func, *args, **kwargs):
        return utils.executeInMainThreadWithResult(func, *args, **kwargs)

    pyblish_integration.register_dispatch_wrapper(threaded_wrapper)
    pyblish_integration.setup(console)

    register_plugins()
    add_to_filemenu()

    pyblish.api.register_host("mayabatch")
    pyblish.api.register_host("mayapy")
    pyblish.api.register_host("maya")

    pyblish_integration.echo("pyblish: Integration loaded..")


def register_plugins():
    # Register accompanying plugins
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.register_plugin_path(plugin_path)
    pyblish_integration.echo("pyblish: Registered %s" % plugin_path)


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
    import pyblish_maya

    cmds.menuItem('pyblishOpeningDivider',
                  divider=True,
                  insertAfter='saveAsOptions',
                  parent='mainFileMenu')

    cmds.menuItem('pyblishScene',
                  insertAfter='pyblishOpeningDivider',
                  label='Publish',
                  parent='mainFileMenu',
                  command=lambda _: pyblish_maya.show())

    cmds.menuItem('pyblishCloseDivider',
                  insertAfter='pyblishScene',
                  parent='mainFileMenu',
                  divider=True)


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
