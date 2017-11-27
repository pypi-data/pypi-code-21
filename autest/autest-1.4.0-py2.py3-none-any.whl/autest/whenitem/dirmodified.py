from os.path import getmtime
from os import getcwd
from os.path import realpath
import os

from autest.api import AddWhenFunction
from autest.testenities.directory import Directory
import hosts.output as host


def DirectoryExists(directory_input):
    if isinstance(directory_input, Directory):    # directory object
        directory_input = directory_input.AbsPath

    def directory_exists(process, **kw):

        if os.path.isabs(directory_input):    # absolute path
            directory_path = directory_input
        else:                            # relative path
            directory_path = os.path.normpath(
                os.path.join(
                    process.RunDirectory,
                    directory_input
                )
            )

        result = os.path.isdir(directory_path)
        host.WriteDebug(
            ['DirectoryExists', 'when'],
            "Testing for directory to exist '{0}' : {1}".format(directory_path, result)
        )
        return result

    return directory_exists


def DirectoryNotExists(directory_input):
    if isinstance(directory_input, Directory):    # directory object
        directory_input = directory_input.AbsPath

    def directory_not_exists(process, **kw):

        if os.path.isabs(directory_input):    # absolute path
            directory_path = directory_input
        else:                            # relative path
            directory_path = os.path.normpath(
                os.path.join(
                    process.RunDirectory,
                    directory_input
                )
            )

        result = not os.path.isdir(directory_path)
        host.WriteDebug(
            ['DirectoryNotExists', 'when'],
            "Test for directory to not exist '{0}' : {1}".format(directory_path, result)
        )
        return result

    return directory_not_exists


def DirectoryModified(directory_input):
    if isinstance(directory_input, Directory):    # directory object
        directory_input = directory_input.AbsPath

    state = {}

    def directory_is_modified(process, **kw):

        if os.path.isabs(directory_input):    # absolute path
            directory_path = directory_input
        else:                            # relative path
            directory_path = os.path.normpath(
                os.path.join(
                    process.RunDirectory,
                    directory_input
                )
            )

        if os.path.isdir(directory_path):
            current_mtime = getmtime(directory_path)
        else:
            host.WriteDebug(["DirectoryModified", "when"],
                            "directory '{0}' does not exist yet".format(directory_path))
            state["modify_time"] = 0
            return False

        if "modify_time" in state:
            host.WriteDebug(["DirectoryModified", "when"],
                            "directory was last modified at {0}".format(state["modify_time"]))
            return state["modify_time"] < current_mtime

        state["modify_time"] = current_mtime
        return False

    return directory_is_modified


AddWhenFunction(DirectoryExists, generator=True)
AddWhenFunction(DirectoryNotExists, generator=True)
AddWhenFunction(DirectoryModified, generator=True)

AddWhenFunction(DirectoryExists, name='DirExists', generator=True)
AddWhenFunction(DirectoryNotExists, name='DirNotExists', generator=True)
AddWhenFunction(DirectoryModified, name='DirModified', generator=True)
