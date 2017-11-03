# -*-encoding:utf-8 -*-
import os


# @six.add_metaclass(abc.ABCMeta)

class Storage(object):
    @classmethod
    def from_str(cls, storage_str):
        if storage_str.startswith('file://'):
            return LocalStorage(storage_str[8:])

    def exists(self, path):
        pass

    def move(self, path, dest):
        pass


class LocalStorage(object):
    def __init__(self, path):
        self.path = path

    def exists(self, path):
        return os.path.exists(path)

    def open(self, mode='r'):
        return open(self.path, mode=mode)


class HdfsStorage(Storage):
    pass
