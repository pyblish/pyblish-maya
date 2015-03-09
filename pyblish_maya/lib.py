# Standard library
import random
import contextlib

# Host libraries
from maya import cmds

# https://msdn.microsoft.com/en-us/library/ms684863(v=VS.85).aspx
CREATE_NO_WINDOW = 0x08000000


def find_next_port():
    return random.randint(6000, 7000)


@contextlib.contextmanager
def maintained_selection():
    """Maintain selection during context

    Example:
        >>> with maintained_selection():
        ...     # Modify selection
        ...     cmds.select('node', replace=True)
        >>> # Selection restored

    """

    previous_selection = cmds.ls(selection=True)
    try:
        yield
    finally:
        if previous_selection:
            cmds.select(previous_selection,
                        replace=True,
                        noExpand=True)
        else:
            cmds.select(deselect=True,
                        noExpand=True)
