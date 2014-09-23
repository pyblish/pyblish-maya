import os
import tempfile

import pyblish.api

from maya import cmds


@pyblish.api.log
class ExtractModelAsMb(pyblish.api.Extractor):
    """Extract family members of Model in Maya ASCII

    Attributes:
        families: The extractor is triggered upon families of "model"
        hosts: This extractor is designed for Autodesk Maya
        version: The current version of the extractor.

    """

    families = ['demo.model']
    hosts = ['maya']
    version = (0, 1, 0)

    def process_instance(self, instance):
        """Returns list of value and exception"""

        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(
            temp_dir, instance.data('name') + ".mb")

        self.log.info("Extracting {0} locally..".format(instance))
        previous_selection = cmds.ls(selection=True)
        cmds.select(list(instance), replace=True)
        cmds.file(temp_file, type='mayaBinary', exportSelected=True)

        self.commit(path=temp_dir, instance=instance)

        if previous_selection:
            cmds.select(previous_selection, replace=True)
        else:
            cmds.select(deselect=True)

        self.log.info("Extraction successful.")
