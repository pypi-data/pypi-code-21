from os.path import getmtime
from os import getcwd
from os.path import realpath
import os

from autest.api import AddWhenFunction
from autest.testenities.file import File
import hosts.output as host


def FileExists(file_input):
    if isinstance(file_input, File):    # file object
        file_input = file_input.AbsPath

    def file_exists(process, **kw):

        if os.path.isabs(file_input):    # absolute path
            file_path = file_input
        else:                            # relative path
            file_path = os.path.normpath(
                os.path.join(
                    process.RunDirectory,
                    file_input
                )
            )

        result = os.path.isfile(file_path)
        host.WriteDebug(
            ['FileExists', 'when'],
            "Testing for file to exist '{0}' : {1}".format(file_path, result)
        )
        return result

    return file_exists


def FileNotExists(file_input):
    if isinstance(file_input, File):    # file object
        file_input = file_input.AbsPath

    def file_not_exists(process, **kw):

        if os.path.isabs(file_input):    # absolute path
            file_path = file_input
        else:                            # relative path
            file_path = os.path.normpath(
                os.path.join(
                    process.RunDirectory,
                    file_input
                )
            )

        result = not os.path.isfile(file_path)
        host.WriteDebug(
            ['FileNotExists', 'when'],
            "Test for file to not exist '{0}' : {1}".format(file_path, result)
        )
        return result

    return file_not_exists


def FileModified(file_input):
    if isinstance(file_input, File):    # file object
        file_input = file_input.AbsPath

    state = {}

    def file_is_modified(process, **kw):
        host.WriteDebug(
            ['FileModified', 'when'],
            "working out of directory {0}".format(getcwd())
        )

        if os.path.isabs(file_input):    # absolute path
            file_path = file_input
        else:                            # relative path
            file_path = os.path.normpath(
                os.path.join(
                    process.RunDirectory,
                    file_input
                )
            )

        if os.path.isfile(file_path):
            current_mtime = getmtime(file_path)
        else:
            host.WriteDebug(["FileModified", "when"],
                            "file '{0}' does not exist yet".format(file_path))
            state["modify_time"] = 0
            return False

        if "modify_time" in state:
            host.WriteDebug(["FileModified", "when"],
                            "file was last modified at {0}".format(state["modify_time"]))
            return state["modify_time"] < current_mtime

        state["modify_time"] = current_mtime
        return False

    return file_is_modified


AddWhenFunction(FileExists, generator=True)
AddWhenFunction(FileNotExists, generator=True)
AddWhenFunction(FileModified, generator=True)
