import os
import time
import shutil
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

    families = ['model']
    hosts = ['maya']
    version = (0, 1, 0)

    def process(self, context):
        cmds.loadPlugin('AbcExport.mll', quiet=True)
        cmds.loadPlugin('AbcImport.mll', quiet=True)

        #get time range
        start = cmds.playbackOptions(q=True, animationStartTime=True)
        end = cmds.playbackOptions(q=True, animationEndTime=True)

        for instance in self.instances(context):
            family = instance.config.get('family')
            for node in instance:
                temp_dir = tempfile.mkdtemp()
                temp_file = os.path.join(temp_dir, '%s.abc' % node.replace(':', '-'))

                self.log.info("Extracting locally..")
                previous_selection = cmds.ls(selection=True)
                cmd = ' -root ' + node
                melCmd = 'AbcExport -j \"-frameRange %s %s' % (start, end)
                melCmd += ' -writeVisibility -uvWrite -worldSpace %s -file' % cmd
                melCmd += ' \\\"%s\\\"\";' % temp_file.replace('\\', '/')
                mel.eval(melCmd)

                self.log.info("Moving extraction relative working file..")
                output = self.commit(path=temp_dir, family=family)

                # Record where instance was extracted
                if not hasattr(instance, 'output_paths'):
                    instance.output_paths = list()

                instance.output_paths.append(output)

                self.log.info("Clearing local cache..")
                shutil.rmtree(temp_dir)

                if previous_selection:
                    cmds.select(previous_selection, replace=True)
                else:
                    cmds.select(deselect=True)

                self.log.info("Extraction successful.")

                yield instance, None  # Value, Exception

    def commit(self, path, family):
        """Move to timestamped destination relative workspace"""

        date = time.strftime(pyblish.backend.config.date_format)

        workspace_dir = cmds.workspace(rootDirectory=True, query=True)
        if not workspace_dir:
            # Project has not been set. Files will
            # instead end up next to the working file.
            workspace_dir = cmds.workspace(dir=True, query=True)
        published_dir = os.path.join(workspace_dir,
                                     pyblish.backend.config.prefix,
                                     family)

        commit_dir = os.path.join(published_dir, date)

        shutil.copytree(path, commit_dir)

        return commit_dir
