import os

import pyblish.api

from maya import cmds


@pyblish.api.log
class CollectWorkspace(pyblish.api.ContextPlugin):
    """Inject the current working file into context

    .. note:: This is optional and used in the supplied extractors.
        If present, the destination of files extracted will end up
        relative this workspace.

    """
    order = pyblish.api.CollectorOrder

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

        context.set_data('workspaceDir', value=normalised)

        # For backwards compatibility
        context.set_data('workspace_dir', value=normalised)
