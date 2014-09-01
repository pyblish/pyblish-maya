import os

import pyblish.backend.lib
import pyblish.backend.plugin

from maya import cmds


@pyblish.backend.lib.log
class SelectWorkspace(pyblish.backend.plugin.Selector):

    hosts = ['maya']
    version = (0, 1, 0)

    def process(self, context):
        workspace = cmds.workspace(rootDirectory=True, query=True)
        if not workspace:
            # Project has not been set. Files will
            # instead end up next to the working file.
            workspace = cmds.workspace(dir=True, query=True)

        # Maya returns forward-slashes by default
        normalised = os.path.normpath(workspace)

        context.set_data('workspace', value=normalised)

        yield None, None


@pyblish.backend.lib.log
class SelectCurrentFile(pyblish.backend.plugin.Selector):

    hosts = ['maya']
    version = (0, 1, 0)

    def process(self, context):
        """Todo, inject the current working file"""
        current_file = cmds.file(sceneName=True, query=True)

        # Maya returns forward-slashes by default
        normalised = os.path.normpath(current_file)

        context.set_data('current_file', value=normalised)
        yield None, None
