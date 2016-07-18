
try:
    __import__("pyblish_maya")
    __import__("pyblish")

except ImportError as e:
    import traceback
    print ("pyblish-maya: Could not load integration: %s"
           % traceback.format_exc())
else:

    import pyblish.api
    import pyblish_maya

    # Setup integration
    pyblish_maya.setup()

    # register default guis
    pyblish.api.register_gui("pyblish_qml")
    pyblish.api.register_gui("pyblish_lite")
