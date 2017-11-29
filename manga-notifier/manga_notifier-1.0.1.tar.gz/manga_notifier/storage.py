# -*- coding: utf-8 -*-

import os
import json
from collections import OrderedDict

all = ['Favorite']


class Storage(object):

    def __init__(self, path):

        self.initialize(path)

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

        path = os.path.expanduser(path)

        base_dir = os.path.dirname(path)
        if not base_dir:
            path = "/".join([os.getcwd(), path])

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

        super(Favorite, self).__init__(path)
        self._empty = True if not any(self._json) else False

    @property
    def empty(self):
        return self._empty

    @property
    def json(self):
        return self._json

    def add(self, manga, chapter, url):

        if manga not in self._json.keys():
            self._json[manga] = OrderedDict({
                "chapter": chapter,
                "url": url
            })
            self._write()

    def delete(self, manga):

        if manga in self._json.keys():
            del self._json[manga]
            self._write()

    def update(self, data):

        self._json.update(data)
        self._write()
