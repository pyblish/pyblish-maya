from version import *

from .lib import (
    show,
    setup,
    teardown,
    register_plugins,
    register_host,
    add_to_filemenu,
    dock,

    # Utility functions
    maintained_selection
)

def is_setup():
    from . import lib
    return lib._has_been_setup

__all__ = [
    "show",
    "setup",
    "teardown",
    "register_plugins",
    "register_host",
    "add_to_filemenu",

    "maintained_selection",
    "maintained_time",
]
