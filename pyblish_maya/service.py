# Dependencies
import pyblish_endpoint.service
from .version import version

from maya import utils

wrapper = utils.executeInMainThreadWithResult


class MayaService(pyblish_endpoint.service.EndpointService):
    def init(self, *args, **kwargs):
        orig = super(MayaService, self).init
        return wrapper(orig, *args, **kwargs)

    def next(self, *args, **kwargs):
        orig = super(MayaService, self).next
        return wrapper(orig, *args, **kwargs)

    def versions(self):
        versions = super(MayaService, self).versions()
        versions["pyblish-nuke"] = version
        return versions
