### ![](https://cloud.githubusercontent.com/assets/2152766/6998101/5c13946c-dbcd-11e4-968b-b357b7c60a06.png)

[![Build Status](https://travis-ci.org/pyblish/pyblish-maya.svg?branch=master)](https://travis-ci.org/pyblish/pyblish-maya)

Pyblish integration for Autodesk Maya 2008-2017.

<br>
<br>
<br>

### What is included?

A set of common plug-ins and functions shared across other integrations - such as getting the current working file. It also visually integrates Pyblish into the File-menu for easy access.

- Common [plug-ins](https://github.com/pyblish/pyblish-maya/tree/master/pyblish_maya/plugins)
- Common [functionality](https://github.com/pyblish/pyblish-maya/blob/master/pyblish_maya/__init__.py)
- File-menu shortcut

<br>
<br>
<br>

### Installation

pyblish-maya depends on [pyblish-base](https://github.com/pyblish/pyblish-base) and is available via PyPI.

```bash
$ pip install pyblish-maya
```

You may also want to consider a graphical user interface, such as [pyblish-qml](https://github.com/pyblish/pyblish-qml) or [pyblish-lite](https://github.com/pyblish/pyblish-lite).

<br>
<br>
<br>

### Usage

To get started using pyblish-maya, run `setup()` at startup of your application.

```python
# 1. Register your favourite GUI
import pyblish.api
pyblish.api.register_gui("pyblish_lite")

# 2. Set-up Pyblish for Maya
import pyblish_maya
pyblish_maya.setup()
```

**Under the hood**

The `setup()` command will:

1. Register `maya` and `mayapy` as as a "host" to Pyblish, allowing plug-ins to be filtered accordingly.
2. Append a new menu item, "Publish" to your File-menu
3. Register a minimal set of plug-ins that are common across all integrations.

![image](https://cloud.githubusercontent.com/assets/2152766/16318991/49012c02-3989-11e6-9602-7ec3d7823b77.png)

**Manually show GUI**

The menu-button is set to run `show()`, which you may also manually call yourself, such as from a shelf-button.

```python
import pyblish_maya
pyblish_maya.show()
```

**No menu-item**

Should you not want a menu-item, pass `menu=False`.

```python
import pyblish_maya
pyblish_maya.show(menu=False)
```

**Teardown pyblish-maya**

To get rid of the menu, and completely remove any trace of pyblish-maya from your Maya session, run `teardown()`.

```python
import pyblish_maya
pyblish_maya.teardown()
```

This will do the opposite of `setup()` and clean things up for you.
