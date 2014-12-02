
# Dependencies
import pyblish_endpoint.service

from maya import utils


# def from_main_thread(func):
#     """Decorator to make `func` execute from main thread"""
#     def wrapper(*args, **kwargs):
#         return utils.executeInMainThreadWithResult(func, *args, **kwargs)
#     return wrapper


class MayaService(pyblish_endpoint.service.EndpointService):
    def init(self, *args, **kwargs):
        return utils.executeInMainThreadWithResult(
            super(MayaService, self).init, *args, **kwargs)

    def process(self, *args, **kwargs):
        return utils.executeInMainThreadWithResult(
            super(MayaService, self).process, *args, **kwargs)
