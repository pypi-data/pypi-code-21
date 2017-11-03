from os.path import getmtime
from os import getcwd
from os.path import realpath
import os

from autest.api import AddWhenFunction
from autest.testenities.file import File
import hosts.output as host


def FileModified(file_input):
    if isinstance(file_input, File):    # file object
        file_input = file_input.AbsPath

    state = {}

    def file_is_modified(process, hasRunFor):
        host.WriteDebug(
            ['file', 'when'],
            "working out of directory {0}".format(getcwd())
        )

        # print(process.RunDirectory)

        if os.path.isabs(file_input):    # absolute path
            file_path = file_input
        else:                            # relative path
            file_path = os.path.normpath(
                os.path.join(process.RunDirectory, file_input))

        current_mtime = getmtime(file_path)

        if "modify_time" in state:
            host.WriteDebug(["file", "when"],
                            "file was last modified at {0}".format(state["modify_time"]))
            return state["modify_time"] < current_mtime

        state["modify_time"] = current_mtime
        return False

    return file_is_modified


AddWhenFunction(FileModified, generator=True)
