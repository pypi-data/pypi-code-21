# -*- coding: utf-8 -*-

import os
import json

all = ['Favorite']


class Storage(object):

    def __init__(self, path):

        self.initialize(os.path.expanduser(path))

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

    def initialize(self, path):

        if not os.path.exists(path):
            Storage.create_file(path)
        if Storage.size_file(path) == 0:
            with open(path, 'r+') as f:
                f.write("{}")
                f.flush()

        self.path = path

        with open(self.path, 'r+') as f:
            self._json = json.load(f)

    def _write(self):

        with open(self.path, 'r+') as f:
            f.seek(0)
            # delete only the content of file in python before writing
            f.truncate()
            f.write(json.dumps(self._json, sort_keys=True, indent=4))
            f.flush()


class Favorite(Storage):

    def __init__(self, path="~/last.json"):
        super().__init__(path)
        self._empty = True if not any(self._json) else False

    @property
    def empty(self):
        return self._empty

    @property
    def json(self):
        return self._json

    def add(self, manga, last):

        if manga not in self._json:
            self._json[manga] = int(last)
            self._write()
        else:
            print("{} already added".format(manga))

    def delete(self, manga):

        if manga in self._json:
            del self._json[manga]
            self._write()

    def update(self, data):

        self._json.update(data)
        self._write()


if __name__ == "__main__":

    l = Favorite("~/test.json")
    print(l)
    print(l._empty)
    l.add('Full Drive', 3)
