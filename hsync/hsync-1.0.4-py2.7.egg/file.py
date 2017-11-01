#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import os

import time


class File:
    def __init__(self, path, md5=None, access_time=None, mod_time=None):

        self.path = '/'.join(path.split(os.sep))
        if md5 is None:
            self.md5file()
        else:
            self.md5 = md5
        self.access_time = int(os.path.getctime(self.path)) if access_time is None else access_time
        self.mod_time = int(os.path.getmtime(self.path)) if mod_time is None else mod_time

    def get_mod_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.mod_time))

    def __eq__(self, other):
        return self.path == other.path and self.md5 == other.md5 and self.mod_time == other.mod_time and self.access_time == other.access_time

    def __hash__(self):
        return hash(self.path) ^ hash(self.md5) ^ hash(self.mod_time) ^ hash(self.access_time)

    def write_file(self, fp):
        p_path = os.path.split(self.path)[0]
        if p_path != '' and not os.path.exists(p_path):
            os.makedirs(p_path)
        new_fp = open(self.path, 'wb')
        data = fp.read()
        new_fp.write(data)
        new_fp.close()
        os.utime(self.path, (self.access_time, self.mod_time))

    def to_json(self):
        return json.dumps({
            'path': self.path,
            'md5': self.md5,
            'access_time': self.access_time,
            'mod_time': self.mod_time
        })

    @staticmethod
    def from_json(json_data):
        return File.from_dict(json.loads(json_data))

    @staticmethod
    def from_dict(dict_data):
        return File(path=dict_data['path'], md5=dict_data['md5'], access_time=int(dict_data['access_time']),
                    mod_time=int(dict_data['mod_time']))

    def md5file(self):
        fp = open(self.path, 'rb')
        self.md5 = hashlib.md5(fp.read()).hexdigest()
        fp.close()
