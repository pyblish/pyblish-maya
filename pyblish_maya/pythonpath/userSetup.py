
try:
    __import__("pyblish_maya")

except ImportError as e:
    print "pyblish: Could not load integration: %s" % e

else:
    import pyblish_maya
    pyblish_maya.setup()
