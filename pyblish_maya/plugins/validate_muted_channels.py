import pyblish.api

from maya import cmds


class ValidateMutedChannels(pyblish.api.Validator):
    """Ensure no muted channels exists in scene

    Todo: Ensure no muted channels are associated with involved nodes
        At the moment, the entire scene is checked.

    """

    families = ['demo.animation']
    hosts = ['maya']
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Look for nodes of type 'mute'

        .. note:: At the moment, it only considers mute nodes present within
            the selection. What should really happen is for nodes to be
            discovered based on whether or not they are connected to any
            of the channels of any transforms present in the selection.

        """

        for node in instance:
            if cmds.nodeType(node) == 'mute':
                raise ValueError("Mute node found: {0}".format(node))
