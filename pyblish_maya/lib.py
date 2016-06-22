# Standard library
import os
import sys
import inspect
import contextlib

# Pyblish libraries
import pyblish
import pyblish.api

# Host libraries
from maya import mel, cmds

# Local libraries
import plugins
from .vendor.Qt import QtWidgets

self = sys.modules[__name__]
self._has_been_setup = False
self._registered_gui = None


def setup():
    """Setup integration

    Registers Pyblish for Maya plug-ins and appends an item to the File-menu

    Attributes:
        console (bool): Display console with GUI
        port (int, optional): Port from which to start looking for an
            available port to connect with Pyblish QML, default
            provided by Pyblish Integration.

    """

    if self._has_been_setup:
        teardown()

    register_plugins()
    register_host()
    add_to_filemenu()

    self._has_been_setup = True
    print("Pyblish loaded successfully.")


def show():
    # Prefer last registered
    guis = reversed(pyblish.api.registered_guis())
    gui = None

    for gui in guis:
        try:
            gui = __import__(gui)
        except (ImportError, AttributeError):
            continue
        else:
            return gui.show()

    if not gui:
        _show_no_gui()


def _show_no_gui():
    messagebox = QtWidgets.QMessageBox()
    messagebox.setIcon(messagebox.Warning)
    messagebox.setFixedWidth(300)
    messagebox.setWindowTitle("Attention")
    messagebox.setText("No GUI found")

    if not pyblish.api.registered_guis():
        messagebox.setInformativeText(
            "Could not detect a registered graphical "
            "user interface for Pyblish.\n\n"

            "To register one, run `pyblish.api.register_gui` "
            "with the name of the GUI you would like this button "
            "to show.")

        messagebox.setDetailedText(
            "See http://api.pyblish.com/register_gui for more information.")

    else:
        messagebox.setInformativeText(
            "None of the registered graphical user interfaces could "
            "be found\n\n"

            "See details for more information.")

        messagebox.setDetailedText(
            "Currently registered graphical user interfaces.\n\n%s" %
            "- ".join(pyblish.api.registered_guis()))

    messagebox.setStandardButtons(messagebox.Ok)
    messagebox.exec_()


def teardown():
    """Remove integration"""
    if not self._has_been_setup:
        return

    deregister_plugins()
    deregister_host()
    remove_from_filemenu()

    self._has_been_setup = False
    print("pyblish: Integration torn down successfully")


def deregister_plugins():
    # Register accompanying plugins
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.deregister_plugin_path(plugin_path)
    print("pyblish: Deregistered %s" % plugin_path)


def register_host():
    """Register supported hosts"""
    pyblish.api.register_host("mayabatch")
    pyblish.api.register_host("mayapy")
    pyblish.api.register_host("maya")


def deregister_host():
    """Register supported hosts"""
    pyblish.api.deregister_host("mayabatch")
    pyblish.api.deregister_host("mayapy")
    pyblish.api.deregister_host("maya")


def register_plugins():
    # Register accompanying plugins
    plugin_path = os.path.dirname(plugins.__file__)
    pyblish.api.register_plugin_path(plugin_path)
    print("pyblish: Registered %s" % plugin_path)


def add_to_filemenu():
    """Add Pyblish to file-menu

    .. note:: We're going a bit hacky here, probably due to my lack
        of understanding for `evalDeferred` or `executeDeferred`,
        so if you can think of a better solution, feel free to edit.

    """

    if hasattr(cmds, 'about') and not cmds.about(batch=True):
        # As Maya builds its menus dynamically upon being accessed,
        # we force its build here prior to adding our entry using it's
        # native mel function call.
        mel.eval("evalDeferred buildFileMenu")

        # Serialise function into string
        script = inspect.getsource(_add_to_filemenu)
        script += "\n_add_to_filemenu()"

        # If cmds doesn't have any members, we're most likely in an
        # uninitialized batch-mode. It it does exists, ensure we
        # really aren't in batch mode.
        cmds.evalDeferred(script)


def remove_from_filemenu():
    for item in ("pyblishOpeningDivider",
                 "pyblishScene",
                 "pyblishCloseDivider"):
        if cmds.menuItem(item, exists=True):
            cmds.deleteUI(item, menuItem=True)


def _add_to_filemenu():
    """Helper function for the above :func:add_to_filemenu()

    This function is serialised into a string and passed on
    to evalDeferred above.

    """

    import os
    import pyblish
    from maya import cmds

    # This must be duplicated here, due to this function
    # not being available through the above `evalDeferred`
    for item in ("pyblishOpeningDivider",
                 "pyblishScene",
                 "pyblishCloseDivider"):
        if cmds.menuItem(item, exists=True):
            cmds.deleteUI(item, menuItem=True)

    icon = os.path.dirname(pyblish.__file__)
    icon = os.path.join(icon, "icons", "logo-32x32.svg")

    cmds.menuItem("pyblishOpeningDivider",
                  divider=True,
                  insertAfter="saveAsOptions",
                  parent="mainFileMenu")

    cmds.menuItem("pyblishScene",
                  insertAfter="pyblishOpeningDivider",
                  label="Publish",
                  parent="mainFileMenu",
                  image=icon,
                  command="import pyblish_maya;pyblish_maya.show()")

    cmds.menuItem("pyblishCloseDivider",
                  insertAfter="pyblishScene",
                  parent="mainFileMenu",
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


@contextlib.contextmanager
def maintained_time():
    """Maintain current time during context

    Example:
        >>> with maintained_time():
        ...    cmds.playblast()
        >>> # Time restored

    """

    ct = cmds.currentTime(query=True)
    try:
        yield
    finally:
        cmds.currentTime(ct, edit=True)
