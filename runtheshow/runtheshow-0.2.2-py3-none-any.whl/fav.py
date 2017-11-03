#!/usr/bin/env python

import os
import json


class Storage(object):

    def __init__(self, path):
        self._path = os.path.expanduser(path)
        if not os.path.exists(self._path):
            Storage.create_file(self._path)

    @staticmethod
    def create_file(name):
        base_dir = os.path.dirname(name)

        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        with open(name, 'a'):
            os.utime(name, None)

    @staticmethod
    def size_file(name):
        statinfo = os.stat(name)
        return statinfo.st_size

    def _read(self):
        with open(self._path, 'r') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()

        if not size:
            # File is empty
            return {}
        else:
            f.seek(0)
            return json.load(f)

    def _write(self, data):
        with open(self._path, 'r+') as f:
            f.seek(0)
            # delete only the content of file in python before writing
            f.truncate()
            f.write(json.dumps(data, sort_keys=True, indent=4))
            f.flush()


class EZTVFavorite(object):

    def __init__(self, json_file="~/eztv.json"):
        self.storage = Storage(json_file)
        self.favorites = self.storage._read()

    def add(self, show, last=None):
        if show not in self.favorites.values():
            self.favorites[show] = last
            self.storage._write()
        else:
            print("{} already added".format(show))

    def delete(self, show):
        if show in self.favorites.values():
            del self.favorites[show]
            self.storage._write()


if __name__ == "__main__":
    print("__MAIN__")

    c = EZTVFavorite()
    print(c.favorites)
