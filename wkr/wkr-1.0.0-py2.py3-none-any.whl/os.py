# -*- coding: utf-8 -*-

"""
OS-level routines.

Parts of the atomic file I/O are adapted from the code given here:

http://stackoverflow.com/a/29491523/1062499

os.py
(c) Will Roberts  23 June, 2017
"""

from __future__ import absolute_import

import errno
import os
import shutil
import tempfile
from contextlib import contextmanager

import wkr.io


def mkdir_p(path):
    """Functionality similar to mkdir -p."""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python > 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


@contextmanager
def temp_file_name(suffix='', directory=None):
    """
    Context manager for creating temporary file names.

    Will find a free temporary filename upon entering and will try to
    delete the file on leaving, even in case of an exception.

    :param str suffix: optional file suffix
    :param str directory: optional directory to save temporary file in
    """
    tfile = tempfile.NamedTemporaryFile(delete=False,
                                        suffix=suffix,
                                        dir=directory)
    tfile.file.close()
    try:
        yield tfile.name
    finally:
        try:
            os.remove(tfile.name)
        except OSError as err:
            if err.errno == errno.ENOENT:  # No such file or directory
                pass
            else:
                raise


@contextmanager
def open_atomic(filepath, mode='w+b', fsync=False, **kwargs):
    """
    Open atomic temporary file object.

    The returned file atomically moves to destination upon exiting.

    Allows reading and writing to and from the same filename.

    The file will not be moved to destination in case of an exception.

    :param str filepath: the file path to be opened
    :param bool fsync: whether to force write the file to disk
    :param kwargs: Any valid keyword arguments for `open`
    """
    with temp_file_name(
            directory=os.path.dirname(os.path.abspath(filepath))) as tmppath:
        with wkr.io.open_file(tmppath, mode, **kwargs) as output_file:
            try:
                yield output_file
            finally:
                if fsync:
                    # TODO: this will not work with stdin/stdout, gzip, etc.
                    output_file.flush()
                    os.fsync(output_file.fileno())
        os.rename(tmppath, filepath)


def backup_file(filename):
    """Back up the old file, if it exists."""
    if os.path.exists(filename):
        if os.path.exists(filename + '~'):
            os.unlink(filename + '~')
        shutil.copyfile(filename, filename + '~')


def write_atomic(lines, output_filename, backup=True):
    """
    Write the given chunks to the named file atomically.

    :param iterable lines:
    :param str output_filename:
    :param bool backup: Defaults to True
    """
    if backup:
        backup_file(output_filename)
    with open_atomic(output_filename, 'wb') as output_file:
        for line in lines:
            output_file.write(line)


@contextmanager
def momentary_chdir(path):
    """
    Context manager to temporarily change the working directory.

    :param str path:
    """
    # record starting PWD
    oldpwd = os.getcwd()
    # change dir
    os.chdir(path)
    yield
    # go back
    os.chdir(oldpwd)
