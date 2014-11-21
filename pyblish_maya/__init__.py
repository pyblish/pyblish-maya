import os
import random
import threading

from . import lib
from . import service

gui = None


def setup():
    """Setup integration"""
    # Underscore prevents makes it less visible from within Maya

    if has_endpoint() and has_frontend():
        setup_endpoint()
        setup_frontend()
        print "pyblish: Setting up frontend"
    else:
        pass

    setup_integration()


def has_endpoint():
    try:
        __import__("pyblish_endpoint.server")
        __import__("pyblish_endpoint.service")
    except ImportError:
        return False
    return True


def has_frontend():
    try:
        __import__("pyblish_qml")
    except ImportError:
        return False
    return True


def setup_endpoint():
    import pyblish_endpoint.server
    import pyblish_endpoint.service

    # Listen for externally running interfaces
    port = random.randint(6000, 7000)

    def server():
        pyblish_endpoint.server.start_production_server(
            service=service.MayaService,
            port=port)

    worker = threading.Thread(target=server)
    worker.daemon = True
    worker.start()

    # Store reference to port for frontend(s)
    os.environ["ENDPOINT_PORT"] = str(port)

    print "pyblish: Endpoint running @ %i" % port


def setup_frontend():
    lib.register_gui("pyblish_qml")


def setup_integration():
    lib.register_plugins()

    # If a frontend is installed, it will be added
    # to the menu as an option-box.
    lib.add_to_filemenu()
    print "pyblish: Integration loaded.."
