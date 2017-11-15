# coding=utf-8

"""
Context manager for using a temporary directory.

Usage::

    with TmpDir as dir:
        print("temp directory: {dir}".format(dir=dir))

"""
import shutil
import tempfile


class TmpDir(object):
    def __init__(self):
        self.__dir_path = None

    def __enter__(self):
        self.__dir_path = tempfile.mkdtemp()
        return self.__dir_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.__dir_path)
