import pyblish.backend.plugin

import pymel.core as pm


class ValidateMeshHistory(pyblish.backend.plugin.Validator):
    """Check meshes for construction history"""

    families = ['model']
    hosts = ['maya']
    version = (0, 1, 0)

    def process(self, context):
        for instance in self.instances(context):
            for node in instance:
                node = pm.PyNode(node)
                if node.inMesh.listConnections():
                    yield None, ValueError('Construction History on: %s' % node)

    def fix(self, context):
        for instance in self.instances(context):
            for node in instance:
                node = pm.PyNode(node)
                pm.delete(node, ch=True)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
