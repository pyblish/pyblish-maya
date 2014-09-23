import os

import pyblish.api

from maya import cmds


@pyblish.api.log
class SelectCurrentFile(pyblish.api.Selector):
    """Inject the current working file into context

    .. note:: This is mandatory for the supplied extractors
    or else they will fail.

    """

    hosts = ['maya']
    version = (0, 1, 0)

    def process_context(self, context):
        """Todo, inject the current working file"""
        current_file = cmds.file(sceneName=True, query=True)

        # Maya returns forward-slashes by default
        normalised = os.path.normpath(current_file)

        context.set_data('current_file', value=normalised)
