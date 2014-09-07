import os

import pyblish.backend.lib
import pyblish.backend.plugin

from maya import cmds


@pyblish.backend.lib.log
class SelectCurrentFile(pyblish.backend.plugin.Selector):

    hosts = ['maya']
    version = (0, 1, 0)

    def process_context(self, context):
        """Todo, inject the current working file"""
        current_file = cmds.file(sceneName=True, query=True)

        # Maya returns forward-slashes by default
        normalised = os.path.normpath(current_file)

        context.set_data('current_file', value=normalised)
