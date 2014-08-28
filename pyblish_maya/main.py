import logging

import pyblish.main
import pyblish.backend.plugin

from maya import cmds

log = logging.getLogger('pyblish_maya.main')


def get_workspace():
    workspace_dir = cmds.workspace(rootDirectory=True, query=True)

    if not workspace_dir:
        # Project has not been set. Files will
        # instead end up next to the working file.
        workspace_dir = cmds.workspace(dir=True, query=True)

    return workspace_dir


def publish_all(context=None):
    """Maya-adaptation of pyblish.main

    Instead of instantiating a context using the current working
    directory, which is from where Python got run, we'll use
    the current working file or workspace, depending on whether
    or not the user has set up his project.

    """

    workspace_dir = get_workspace()
    context = pyblish.backend.plugin.Context(current_path=workspace_dir)
    return pyblish.main.publish_all(context)


def validate_all(context=None):
    workspace_dir = get_workspace()
    context = pyblish.backend.plugin.Context(current_path=workspace_dir)
    return pyblish.main.validate_all(context)
