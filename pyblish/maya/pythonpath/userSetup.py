# Standard library
import os

# Pyblish libraries
import pyblish.backend.plugin

# Local libraries
import pyblish.maya

# Host libraries
from maya import mel
from maya import cmds


# Register accompanying plugins
package_path = os.path.dirname(pyblish.maya.__file__)
plugin_path = os.path.join(package_path, 'plugins')

pyblish.backend.plugin.register_plugin_path(plugin_path)
print "Registered %s" % plugin_path


def eval_append_to_filemenu():
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
              label='Pyblish',
              insertAfter='pyblishOpeningDivider',
              command=lambda _: pyblish.main.pyblish_all())
cmds.menuItem('validateScene',
              label='Validate',
              insertAfter='pyblishScene',
              command=lambda _: pyblish.main.validate_all())
cmds.menuItem('pyblishCloseDivider',
              divider=True,
              insertAfter='validateScene')

    """

    cmds.evalDeferred(script)


if hasattr(cmds, 'about') and not cmds.about(batch=True):
    # If cmds doesn't have any members, we're most likely in an
    # uninitialized batch-mode. It it does exists, ensure we
    # really aren't in batch mode.
    eval_append_to_filemenu()
