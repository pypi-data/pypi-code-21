"""Ways to supply (string) content for Actions that create or manipulate files."""

import subprocess
from typing import Union, Callable


StrSupplier = Callable[[], str]


class DeferStr(object):
    """Lazy string, making a string supplier appear as a string.

    It is possible to create Actions that provide information at runtime, e.g. an installation path or a version number.
    DeferStr can be used to encapsulate such an Action method, and make it appear as a plain string, in order to pass
    it as argument to another Action. It will then be evaluated lazily, at runtime.
    """

    def __init__(self, supplier):
        self.supplier = supplier

    def __str__(self):
        return str(self.supplier())


StringArg = Union[str, DeferStr]


def supplier(contents: Union[StringArg, StrSupplier]) -> StrSupplier:
    """Convert an argument to a string supplier, if it is not already."""
    return contents if callable(contents) else lambda: contents


class OutputOf(object):
    """Supply the output of a command, executed inside the container.

    Parameters
    ----------
    command
      Command to execute. If it is a string, it will be interpreted by the shell.

    """

    def __init__(self, command):
        self.command = command
        super(OutputOf, self).__init__()

    def __call__(self):
        return subprocess.check_output(self.command, shell=type(self.command) is str, universal_newlines=True)
