#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import os
import pickle
import re
import struct
import time

import requests

sep = '/'


class Dir:
    def __init__(self, root_path, exclude_ext_list, exclude_dir_list):
        self.root_path = root_path
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        os.chdir(self.root_path)
        self.exclude_ext_list = exclude_ext_list
        self.exclude_dir_list = exclude_dir_list

    def get_file_list(self):

        def root_exclude(exclude_dir_list, _root):

            def dir_to_list(dir_str):
                dir_list = re.split(r'/|\\', dir_str)
                if '.' in dir_list:
                    dir_list.remove('.')
                return dir_list

            # 判断dir1是否为dir2的子目录
            def dir_in(dir1, dir2):
                if len(dir1) < len(dir2):
                    return False
                for i in range(len(dir2)):
                    if dir1[i] != dir2[i]:
                        return False
                return True

            for exclude_dir in exclude_dir_list:
                exclude_dir = dir_to_list(exclude_dir)
                root_dir_list = dir_to_list(_root)
                if dir_in(root_dir_list, exclude_dir):
                    return True
            return False
        file_set = set()
        for root, dirs, files in os.walk('.', topdown=False):
            if root_exclude(self.exclude_ext_list, root):
                continue
            for name in files:
                if os.path.splitext(name)[1] in self.exclude_ext_list:
                    continue
                file_set.add(File(sep.join((root, name))))
        return file_set


class ServerDir(Dir):
    pass


class LocalDir(Dir):
    class ServerPart:
        def __init__(self, path, url):
            self.path = path
            self.url = url

        def get_request_url(self):
            return self.url + self.path

    def __init__(self, conf):
        Dir.__init__(self, root_path=conf['local_path'],
                     exclude_ext_list=conf.get('exclude_ext', ()),
                     exclude_dir_list=conf.get('exclude_dir', ()),
                     )
        self.server_list = [LocalDir.ServerPart(server['remote_path'], server['remote_url']) for server in conf['server']]

    def request(self, index):
        tree_list = requests.get(self.server_list[index].get_request_url()).content
        if len(tree_list) == 0:
            return None
        return pickle.loads(tree_list)

    def post(self, index, file_data):
        print 'uploading %s' % file_data.path
        file_data.read_file()
        requests.post(self.server_list[index].get_request_url(), data=file_data.to_json())


class File:
    def __init__(self, path, md5=None, access_time=None, mod_time=None, file_data=None):
        if type(path) == unicode:
            path = path.encode('utf-8')
        if type(md5) == unicode:
            md5 = md5.encode('utf-8')
        self.path = sep.join(path.split(os.sep))
        self.md5 = md5file(path) if md5 is None else md5
        self.access_time = int(os.path.getctime(self.path)) if access_time is None else access_time
        self.mod_time = int(os.path.getmtime(self.path)) if mod_time is None else mod_time
        self.file_data = None if file_data is None else file_data

    def get_mod_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.mod_time))

    def __eq__(self, other):
        return self.path == other.path and self.md5 == other.md5 and self.mod_time == other.mod_time and self.access_time == other.access_time

    def __hash__(self):
        return hash(self.path) ^ hash(self.md5) ^ hash(self.mod_time) ^ hash(self.access_time)

    def to_json(self):
        return json.dumps({
            'path': self.path,
            'md5': self.md5,
            'access_time': self.access_time,
            'mod_time': self.mod_time,
            'file_data': self.file_data
        })

    def read_file(self):
        with open(self.path, 'rb') as f:
            data = f.read()
        self.file_data = struct.unpack('%sB' % len(data), data)

    def write_file(self):
        p_path = os.path.split(self.path)[0]
        if p_path != '' and not os.path.exists(p_path):
            os.makedirs(p_path)
        data = struct.pack('%sB' % len(self.file_data), *self.file_data)
        with open(self.path, 'wb+') as f:
            f.write(data)
        os.utime(self.path, (self.access_time, self.mod_time))

    @staticmethod
    def from_json(json_data):
        data_dict = json.loads(json_data)
        return File(path=data_dict['path'], md5=data_dict['md5'], access_time=data_dict['access_time'],
                    mod_time=data_dict['mod_time'], file_data=data_dict['file_data'])


def diff(source, targets):
    target_dic = {}
    for target in targets:
        target_dic[target.path] = target
    new = set()
    overwrite = set()
    old = set()
    same = set()
    for s in source:
        t = target_dic.get(s.path, None)
        if t is None:
            new.add(s)
        else:
            if t.md5 == s.md5:
                same.add(s)
            elif t.mod_time > s.mod_time:
                old.add(s)
            elif t.mod_time < s.mod_time:
                overwrite.add(s)
            else:
                print 'err'
    return new, overwrite, old, same


def md5file(file_path):
    fp = open(file_path, 'rb')
    return hashlib.md5(fp.read()).hexdigest()
