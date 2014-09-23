import pyblish.api

import maya.cmds as cmds


@pyblish.api.log
class SelectObjectSet(pyblish.api.Selector):
    """Identify publishable instances via an associated identifier

    The identifier is located within the Pyblish configuration
    as `pyblish.identifier` and is typically something
    like "publishable".

    Any node of type objectSet containing this attribute will be
    deemed an `Instance` capable of being published. Additionally,
    the objectSet may contain a "family" attribute that will be
    injected into the given instance.

    Prerequisities:
        INSTANCE is of type `objectSet`
        Each INSTANCE MUST contain the attribute `publishable`
        Each INSTANCE MUST contain the attribute `family`

    """

    hosts = ['maya']
    version = (0, 1, 0)

    def process_context(self, context):
        for objset in cmds.ls("*." + pyblish.api.config['identifier'],
                              objectsOnly=True,
                              type='objectSet',
                              long=True):

            name = cmds.ls(objset, long=False)[0]  # Use short name
            instance = context.create_instance(name=name)
            self.log.info("Adding instance: {0}".format(objset))

            for node in cmds.sets(objset, query=True):
                if cmds.nodeType(node) == 'transform':
                    descendents = cmds.listRelatives(node,
                                                     allDescendents=True,
                                                     fullPath=True)
                    for descendent in descendents:
                        instance.add(descendent)

                instance.add(node)

            attrs = cmds.listAttr(objset, userDefined=True)
            for attr in attrs:
                if attr == pyblish.api.config['identifier']:
                    continue

                try:
                    value = cmds.getAttr(objset + "." + attr)
                except:
                    continue

                instance.set_data(attr, value=value)
