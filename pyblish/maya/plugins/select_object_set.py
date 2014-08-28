import pyblish.backend.lib
import pyblish.backend.config
import pyblish.backend.plugin

import maya.cmds as cmds


@pyblish.backend.lib.log
class SelectObjectSet(pyblish.backend.plugin.Selector):
    """Select instances of node-type 'transform'

    Opens up the doors for instances containing nodes of any type,
    but lacks the ability to be nested with DAG nodes.

    E.g.          -> /root/MyCharacter.publishable/an_object_set

    """

    hosts = ['maya']
    version = (0, 1, 0)

    def process(self, context):
        for objset in cmds.ls("*." + pyblish.backend.config.identifier,
                              objectsOnly=True,
                              type='objectSet'):

            instance = pyblish.backend.plugin.Instance(name=objset)
            self.log.info("Adding instance: {0}".format(objset))

            for node in cmds.sets(objset, query=True):
                if cmds.nodeType(node) == 'transform':
                    descendents = cmds.listRelatives(node,
                                                     allDescendents=True)
                    for descendent in descendents:
                        instance.add(descendent)
                else:
                    instance.add(node)

            attrs = cmds.listAttr(objset, userDefined=True)
            for attr in attrs:
                if attr == pyblish.backend.config.identifier:
                    continue

                try:
                    value = cmds.getAttr(objset + "." + attr)
                except:
                    continue

                # Allow name to be overriden via attribute.
                if attr == 'name':
                    instance.name = value
                    continue

                instance.config[attr] = value

            context.add(instance)

            yield instance, None
