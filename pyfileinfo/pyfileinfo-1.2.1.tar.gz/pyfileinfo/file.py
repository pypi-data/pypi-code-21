# -*- coding: utf-8 -*-

import os


class File(object):
    def __init__(self, path):
        self._path = path

    def __str__(self):
        return self._path

    @staticmethod
    def is_valid(path):
        return True

    @staticmethod
    def hint():
        return []

    @property
    def path(self):
        return self._path

    @property
    def size(self):
        return os.path.getsize(self.path)
