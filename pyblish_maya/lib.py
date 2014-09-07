# Standard library
import os
import logging

# Pyblish libraries
import pyblish.backend.plugin

# Integration libraries
import pyblish_maya

# Host libraries
from maya import mel
from maya import cmds

log = logging.getLogger('pyblish')


def register_plugins():
    # Register accompanying plugins
    package_path = os.path.dirname(pyblish_maya.__file__)
    plugin_path = os.path.join(package_path, 'plugins')

    pyblish.backend.plugin.register_plugin_path(plugin_path)
    log.info("Registered %s" % plugin_path)


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

    script = """
import pyblish.main

cmds.menuItem('pyblishOpeningDivider',
            divider=True,
            insertAfter='saveAsOptions',
            parent='mainFileMenu')
cmds.menuItem('pyblishScene',
            label='Publish',
            insertAfter='pyblishOpeningDivider',
            command=lambda _: pyblish.main.publish_all())
cmds.menuItem('validateScene',
            label='Validate',
            insertAfter='pyblishScene',
            command=lambda _: pyblish.main.validate_all())
cmds.menuItem('pyblishCloseDivider',
            divider=True,
            insertAfter='validateScene')

    """

    if hasattr(cmds, 'about') and not cmds.about(batch=True):
        # If cmds doesn't have any members, we're most likely in an
        # uninitialized batch-mode. It it does exists, ensure we
        # really aren't in batch mode.
        cmds.evalDeferred(script)
