import os
import tempfile

import pyblish.backend.lib
import pyblish.backend.plugin

from maya import cmds
import maya.mel as mel


@pyblish.backend.lib.log
class ExtractAlembic(pyblish.backend.plugin.Extractor):
    """Extract family members to Alembic format

    Attributes:
        families: The extractor is triggered upon families of "model"
        hosts: This extractor is designed for Autodesk Maya
        version: The current version of the extractor.

    """

    families = ['demo.alembic']
    hosts = ['maya']
    version = (0, 1, 0)

    def process_instance(self, instance):
        #loading alembic plugin
        cmds.loadPlugin('AbcExport.mll', quiet=True)
        cmds.loadPlugin('AbcImport.mll', quiet=True)

        #create temp dir
        temp_dir = tempfile.mkdtemp()
        fileName = instance.data('name').replace('|', '_')
        fileName = fileName.replace(':', '-')
        fileName += ".abc"
        temp_file = os.path.join(temp_dir, fileName)

        #get time range
        start = cmds.playbackOptions(q=True, animationStartTime=True)
        end = cmds.playbackOptions(q=True, animationEndTime=True)

        #extracting
        self.log.info("Extracting {0} locally..".format(instance))

        #finding root nodes within instance
        transforms = {}
        for child in instance:
            if cmds.nodeType(child) == 'transform':
                transforms[child] = len(child.split('|'))

        minValue = transforms[min(transforms, key=transforms.get)]

        cmd = ' -root '
        for key in transforms:
            if transforms[key] == minValue:
                cmd += key + ' '

        melCmd = 'AbcExport -j \"-frameRange %s %s' % (start, end)
        melCmd += ' -writeVisibility -uvWrite -worldSpace %s -file' % cmd
        melCmd += ' \\\"%s\\\"\";' % temp_file.replace('\\', '/')

        #exporting alembic
        mel.eval(melCmd)

        self.commit(path=temp_dir, instance=instance)
