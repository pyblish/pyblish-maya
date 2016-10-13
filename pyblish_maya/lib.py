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
from . import plugins
from .vendor.Qt import QtWidgets, QtGui

self = sys.modules[__name__]
self._has_been_setup = False
self._has_menu = False
self._registered_gui = None
self._dock = None
self._dock_control = None


def setup(menu=True):
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

    if menu:
        add_to_filemenu()
        self._has_menu = True

    self._has_been_setup = True
    print("Pyblish loaded successfully.")


def show():
    """Try showing the most desirable GUI

    This function cycles through the currently registered
    graphical user interfaces, if any, and presents it to
    the user.

    """

    return (_discover_gui() or _show_no_gui)()


def _discover_gui():
    """Return the most desirable of the currently registered GUIs"""

    # Prefer last registered
    guis = reversed(pyblish.api.registered_guis())

    for gui in guis:
        try:
            gui = __import__(gui).show
        except (ImportError, AttributeError):
            continue
        else:
            return gui


def teardown():
    """Remove integration"""
    if not self._has_been_setup:
        return

    deregister_plugins()
    deregister_host()

    if self._has_menu:
        remove_from_filemenu()
        self._has_menu = False

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


def _show_no_gui():
    """Popup with information about how to register a new GUI

    In the event of no GUI being registered or available,
    this information dialog will appear to guide the user
    through how to get set up with one.

    """

    messagebox = QtWidgets.QMessageBox()
    messagebox.setIcon(messagebox.Warning)
    messagebox.setWindowIcon(QtGui.QIcon(os.path.join(
        os.path.dirname(pyblish.__file__),
        "icons",
        "logo-32x32.svg"))
    )

    spacer = QtWidgets.QWidget()
    spacer.setMinimumSize(400, 0)
    spacer.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                         QtWidgets.QSizePolicy.Expanding)

    layout = messagebox.layout()
    layout.addWidget(spacer, layout.rowCount(), 0, 1, layout.columnCount())

    messagebox.setWindowTitle("Uh oh")
    messagebox.setText("No registered GUI found.")

    if not pyblish.api.registered_guis():
        messagebox.setInformativeText(
            "In order to show you a GUI, one must first be registered. "
            "Press \"Show details...\" below for information on how to "
            "do that.")

        messagebox.setDetailedText(
            "Pyblish supports one or more graphical user interfaces "
            "to be registered at once, the next acting as a fallback to "
            "the previous."
            "\n"
            "\n"
            "For example, to use Pyblish Lite, first install it:"
            "\n"
            "\n"
            "$ pip install pyblish-lite"
            "\n"
            "\n"
            "Then register it, like so:"
            "\n"
            "\n"
            ">>> import pyblish.api\n"
            ">>> pyblish.api.register_gui(\"pyblish_lite\")"
            "\n"
            "\n"
            "The next time you try running this, Lite will appear."
            "\n"
            "See http://api.pyblish.com/register_gui.html for "
            "more information.")

    else:
        messagebox.setInformativeText(
            "None of the registered graphical user interfaces "
            "could be found."
            "\n"
            "\n"
            "Press \"Show details\" for more information.")

        messagebox.setDetailedText(
            "These interfaces are currently registered."
            "\n"
            "%s" % "\n".join(pyblish.api.registered_guis()))

    messagebox.setStandardButtons(messagebox.Ok)
    messagebox.exec_()


class Dock(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Dock, self).__init__(parent)
        QtWidgets.QVBoxLayout(self)
        self.setObjectName("pyblish_maya.dock")


def dock(window):

    main_window = None
    for obj in QtWidgets.qApp.topLevelWidgets():
        if obj.objectName() == "MayaWindow":
            main_window = obj

    if not main_window:
        raise ValueError("Could not find the main Maya window.")

    # Deleting existing dock
    print "Deleting existing dock..."
    if self._dock:
        self._dock.setParent(None)
        self._dock.deleteLater()

    if self._dock_control:
        if cmds.dockControl(self._dock_control, query=True, exists=True):
            cmds.deleteUI(self._dock_control)

    # Creating new dock
    print "Creating new dock..."
    dock = Dock(parent=main_window)

    dock_control = cmds.dockControl(label=window.windowTitle(), area="right",
                                    visible=True, content=dock.objectName(),
                                    allowedArea=["right", "left"])
    dock.layout().addWidget(window)

    self._dock = dock
    self._dock_control = dock_control
