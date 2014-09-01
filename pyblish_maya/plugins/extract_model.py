import os
import shutil
import tempfile

import pyblish.backend.lib
import pyblish.backend.plugin

from maya import cmds


@pyblish.backend.lib.log
class ExtractModelAsMa(pyblish.backend.plugin.Extractor):
    """Extract family members of Model in Maya ASCII

    Attributes:
        families: The extractor is triggered upon families of "model"
        hosts: This extractor is designed for Autodesk Maya
        version: The current version of the extractor.

    """

    families = ['model']
    hosts = ['maya']
    version = (0, 1, 0)

    def process(self, context):
        """Returns list of value and exception"""

        compatible_instances = pyblish.backend.plugin.instances_by_plugin(
            instances=context, plugin=self)

        for instance in compatible_instances:
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, 'pyblish')

            self.log.info("Extracting locally..")
            previous_selection = cmds.ls(selection=True)
            cmds.select(list(instance), replace=True)
            cmds.file(temp_file, type='mayaBinary', exportSelected=True)

            self.log.info("Moving extraction relative working file..")
            output = self.commit(path=temp_dir, context=context)

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
