# coding=utf-8
import os
import errno
import shutil


def create_dir(dirname):
    if not dirname or os.path.exists(dirname):
        return

    try:
        os.makedirs(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def remove_dir(dirname):
    try:
        shutil.rmtree(dirname)
    except (OSError, IOError):
        pass
