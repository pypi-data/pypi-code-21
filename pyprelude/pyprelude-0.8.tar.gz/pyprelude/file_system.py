############################################################
#
# pyprelude.file_system
# Copyright (C) 2017, Richard Cook
# Released under MIT License
# https://github.com/rcook/pyprelude
#
############################################################

import os
import shutil
import stat

from .platform import ON_WINDOWS
from .util import unpack_args

def _hack_make_path_doctest_output(s):
    if ON_WINDOWS:
        drive, _ = os.path.splitdrive(os.getcwd())
        assert s.startswith(drive + "\\")
        return s[len(drive) : ].replace("\\", "/")
    else:
        return s

def _remove_dir_on_error(func, path, exc_info):
    if os.access(path, os.W_OK):
        raise
    else:
        os.chmod(path, stat.S_IWUSR)
        func(path)

def remove_dir(path):
    try:
        shutil.rmtree(path, onerror=_remove_dir_on_error)
    except WindowsError:
        from .process import execute
        from .temp_util import temp_dir
        with temp_dir() as d:
            status, output, error = execute("robocopy.exe", d, path, "/mir", can_fail=True)
            if status != 2:
                raise RuntimeError("robocopy failed with status {} (output={}, error={})".format(status, output, error))

        os.rmdir(path)

def make_path(*args):
    """
    >>> _hack_make_path_doctest_output(make_path("/a", "b"))
    '/a/b'
    >>> _hack_make_path_doctest_output(make_path(["/a", "b"]))
    '/a/b'
    >>> _hack_make_path_doctest_output(make_path(*["/a", "b"]))
    '/a/b'
    >>> _hack_make_path_doctest_output(make_path("/a"))
    '/a'
    >>> _hack_make_path_doctest_output(make_path(["/a"]))
    '/a'
    >>> _hack_make_path_doctest_output(make_path(*["/a"]))
    '/a'
    """
    paths = unpack_args(*args)
    return os.path.abspath(os.path.join(*[p for p in paths if p is not None]))
