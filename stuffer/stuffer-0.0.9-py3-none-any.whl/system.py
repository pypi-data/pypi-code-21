import getpass
import os

from stuffer.content import StringArg
from stuffer.core import Action


class ShellCommand(Action):
    """Run an arbitrary shell command.

    Parameters
    ----------
    command
        Command to execute. It will be interpreted by the shell, so pipes, redirects, etc are allowed.
    """

    def __init__(self, command: StringArg):
        self._command = command
        super().__init__()

    def command(self):
        return self._command


def real_user():
    return os.environ.get('SUDO_USER', getpass.getuser())
