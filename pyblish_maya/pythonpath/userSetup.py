
INTEGRATION = False
ENDPOINT = False

try:
    import pyblish_maya
    INTEGRATION = True
except ImportError as e:
    print "Couldn't find pyblish_maya on your PYTHONPATH: ", e

try:
    import pyblish_endpoint.server
    ENDPOINT = True
except ImportError as e:
    # If Endpoint isn't installed, Maya won't be able to communicate
    # with externally running interfaces; such as the QML frontend.
    pass


if INTEGRATION:
    # Register Maya plugins upon startup
    pyblish_maya.register_plugins()

    if ENDPOINT:
        # Listen for externally running interfaces
        pyblish_endpoint.server.start(service=pyblish_maya.EndpointService)

        try:
            import pyblish_qml
            pyblish_maya.register_gui("pyblish_qml")
            print "Registing QML GUI"
        except ImportError:
            pass

        print "Pyblish Endpoint started.."

    # Filemenu will append GUI only if there is an endpoint
    # willing to communicate with it.
    pyblish_maya.add_to_filemenu()
    print "Pyblish integration loaded.."
