import pyblish.api

import maya.cmds as cmds


@pyblish.api.log
class SelectTransform(pyblish.api.Selector):
    """Select instances of node-type 'transform'"""

    hosts = ['maya']
    version = (0, 1, 0)

    def process_context(self, context):
        for transform in cmds.ls(
                "*." + pyblish.api.config['identifier'],
                recursive=True,
                objectsOnly=True,
                type='transform',
                long=True):

            name = transform.split('|')[-1]
            name = name.replace(':', '-')
            instance = context.create_instance(name=name)

            instance.add(transform)
            for child in cmds.listRelatives(transform, allDescendents=True,
                                            fullPath=True):
                    instance.add(child)

            attrs = cmds.listAttr(transform, userDefined=True)

            for attr in attrs:
                if attr == pyblish.api.config['identifier']:
                    continue

                try:
                    value = cmds.getAttr(transform + "." + attr)
                except:
                    continue

                instance.set_data(attr, value=value)
