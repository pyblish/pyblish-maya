
try:
    __import__("pyblish_maya")

except ImportError:
    print "pyblish: Could not load integration"

else:
    import pyblish_maya
    pyblish_maya.setup()
