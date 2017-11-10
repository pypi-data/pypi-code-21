# -*- coding: utf-8 -*-

import os
import json


class Storage(object):

    def __init__(self, path="~/last.json"):

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
            self.config = json.load(f)

    def _write(self):

        with open(self.path, 'r+') as f:
            f.seek(0)
            f.truncate()  # delete only the content of file in python before writing
            f.write(json.dumps(self.config, sort_keys=True, indent=4))
            f.flush()

    def add(self, manga, last):

        if manga not in self.config:
            self.config[manga] = int(last)
            self._write()
        else:
            print("{} already added".format(manga))

    def delete(self, manga):

        if manga in self.config:
            del self.config[manga]
            self._write()

    def update(self, data):

        self.config.update(data)
        self._write()
