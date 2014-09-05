import pyblish.backend.plugin

from maya import cmds


class ValidateMutedChannels(pyblish.backend.plugin.Validator):
    """Ensure no muted channels exists in scene

    Todo: Ensure no muted channels are associated with involved nodes
        At the moment, the entire scene is checked.

    """

    families = ['demo.model']
    hosts = ['maya']
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Look for nodes of type 'mute'"""
        for node in instance:
            if cmds.nodeType(node) == 'mute':
                raise ValueError("Mute node found: {0}".format(node))
