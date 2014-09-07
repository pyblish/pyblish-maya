
import pyblish.backend.plugin


class ValidateReviewInstances(pyblish.backend.plugin.Validator):
    """If there are any review instances, validate them

    Ensure that review selections contain a camera.

    """

    families = ['demo.review']
    hosts = ['maya']

    def process_instance(self, instance):
        pass
