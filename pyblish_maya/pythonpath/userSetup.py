try:
    import pyblish_maya.lib
except ImportError:
    raise ImportError("Error: Couldn't find "
                      "pyblish_maya on your PYTHONPATH")

# Register Maya plugins upon startup
pyblish_maya.lib.register_plugins()
pyblish_maya.lib.add_to_filemenu()
