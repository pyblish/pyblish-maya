import pyblish.backend.plugin

from maya import cmds


class ValidateMutedChannels(pyblish.backend.plugin.Validator):
    """Ensure no muted channels exists in scene

    Todo: Ensure no muted channels are associated with involved nodes
        At the moment, the entire scene is checked.

    """

    families = ['model']
    hosts = ['maya']
    version = (0, 1, 0)

    def process(self, context):
        """Look for nodes of type 'mute'"""
        mutes = cmds.ls(type='mute')
        if mutes:
            yield None, ValueError("Muted nodes found")
        else:
            yield None, None


if __name__ == '__main__':
    import doctest
    doctest.testmod()
