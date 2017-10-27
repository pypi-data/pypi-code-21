"""
All the exceptions and their messages used by the program
"""
import sys

ERROR_HEAD = 'dploy {subcmd}: can not {subcmd} '


class Errors():
    """
    A class that collects and executes action objects
    """

    def __init__(self, is_silent):
        self.exceptions = []
        self.is_silent = is_silent

    def add(self, error):
        """
        Adds an error
        """
        self.exceptions.append(error.exception)

    def handle(self):
        """
        Prints and handles errors
        """
        if len(self.exceptions) > 0:
            if not self.is_silent:
                for exception in self.exceptions:
                    print(exception, file=sys.stderr)
            raise self.exceptions[0]


# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods


class SourceIsSameAsDest():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': A source argument is the same as the dest argument"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = ValueError(self.msg)


class ConflictsWithAnotherSource():
    def __init__(self, subcmd, files):
        self.msg = ERROR_HEAD + "the following: Conflicts with other source {files}"
        files_list = '\n    ' + '\n    '.join(files)
        self.msg = self.msg.format(subcmd=subcmd, files=files_list)
        self.exception = ValueError(self.msg)


class ConflictsWithExistingFile():
    def __init__(self, subcmd, source, dest):
        self.msg = ERROR_HEAD + "'{source}': Conflicts with existing file '{dest}'"
        self.msg = self.msg.format(subcmd=subcmd, source=source, dest=dest)
        self.exception = ValueError(self.msg)


class ConflictsWithExistingLink():
    def __init__(self, subcmd, source, dest):
        self.msg = ERROR_HEAD + "'{source}': Conflicts with existing symlink '{dest}'"
        self.msg = self.msg.format(subcmd=subcmd, source=source, dest=dest)
        self.exception = ValueError(self.msg)


class InsufficientPermissions():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': Insufficient permissions"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = PermissionError(self.msg)


class NoSuchDirectory():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': No such directory"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = NotADirectoryError(self.msg)


class PermissionDenied():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': Permission denied"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = PermissionError(self.msg)


class InsufficientPermissionsToSubcmdFrom():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "from '{file}': Insufficient permissions"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = PermissionError(self.msg)


class NoSuchDirectoryToSubcmdInto():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "into '{file}': No such directory"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = NotADirectoryError(self.msg)


class InsufficientPermissionsToSubcmdTo():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "to '{file}': Insufficient permissions"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = PermissionError(self.msg)


class NoSuchFileOrDirectory():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': No such file or directory"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = FileNotFoundError(self.msg)


class DuplicateSource():
    def __init__(self, subcmd, file):
        self.msg = ERROR_HEAD + "'{file}': Duplicate source argument"
        self.msg = self.msg.format(subcmd=subcmd, file=file)
        self.exception = ValueError(self.msg)
