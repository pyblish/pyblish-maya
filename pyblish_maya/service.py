# Dependencies
import pyblish_endpoint.service

from maya import utils

wrapper = utils.executeInMainThreadWithResult


class MayaService(pyblish_endpoint.service.EndpointService):
    def init(self, *args, **kwargs):
        orig = super(MayaService, self).init
        return wrapper(orig, *args, **kwargs)

    def process(self, *args, **kwargs):
        orig = super(MayaService, self).process
        return wrapper(orig, *args, **kwargs)
