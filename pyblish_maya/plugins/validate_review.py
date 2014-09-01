
import pyblish.backend.plugin


class ValidateReviewInstances(pyblish.backend.plugin.Validator):
    """If there are any review instances, validate them

    Ensure that review selections contain a camera.

    """

    families = ['review']
    hosts = ['maya']

    def process(self, context):
        instances_by_plugin = pyblish.backend.plugin.instances_by_plugin
        compatible_instances = instances_by_plugin(instances=context,
                                                   plugin=self)
        for instance in compatible_instances:
            print "Running reviewvalidator on %s" % instance
            yield instance, None
