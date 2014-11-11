import pyblish.main
import pyblish.api

# Dependencies
import pyblish_endpoint.service

from maya import utils


class EndpointService(pyblish_endpoint.service.EndpointService):
    def instances(self):
        return utils.executeInMainThreadWithResult(get_instances)

    def publish(self):
        return utils.executeInMainThreadWithResult(publish)


def publish():
    pyblish.main.publish()


def get_instances():
    ctx = pyblish.api.Context()
    plugins = pyblish.api.discover(type="selectors")

    instances = []
    for plugin in plugins:
        for inst, err in plugin().process(ctx):
            if err is not None:
                instances.append({"instance": None,
                                  "message": "Exception occured"})

    for instance in ctx:
        instances.append({
            "instance": instance.name,
            "family": instance.data("family")
        })

    return instances
