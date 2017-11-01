#!/usr/bin/env python
# -*- coding: utf-8 -*-
import hashlib
import json
import locale
import os
import re
import sys
import time

import requests


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
                name = name.decode(sys.getfilesystemencoding())
                if os.path.splitext(name)[1] in self.exclude_ext_list:
                    continue
                file_set.add(File('/'.join((root, name))))
        return file_set


class ServerDir(Dir):
    pass


class LocalDir(Dir):
    class ServerPart:
        def __init__(self, path, url):
            self.path = path
            self.url = url

        def get_request_url(self):
            return (self.url + self.path).encode('utf-8')

    def __init__(self, conf):
        Dir.__init__(self, root_path=conf['local_path'],
                     exclude_ext_list=conf.get('exclude_ext', ()),
                     exclude_dir_list=conf.get('exclude_dir', ()),
                     )
        self.server_list = [LocalDir.ServerPart(server['remote_path'], server['remote_url']) for server in
                            conf['server']]

    def request(self, index):
        response = requests.get(self.server_list[index].get_request_url())
        if response.status_code != 200:
            print response.status_code
            return None
        tree_list = response.content
        return [File.from_dict(j) for j in json.loads(tree_list)]

    def post(self, index, file_data):
        print 'uploading %s' % file_data.path
        with open(file_data.path, 'rb') as fp:
            requests.post(self.server_list[index].get_request_url(),
                          data=file_data.__dict__,
                          files={'file_body': fp}
                          )


if __name__ == '__main__':
    print os.getcwd()
    print sys.stdout.encoding
    print sys.getdefaultencoding()
    print locale.getdefaultlocale()
    print locale.getlocale()
    print sys.getfilesystemencoding()
    print sys.stdin.encoding
    print sys.stdout.encoding
    for p in Dir('./', [], []).get_file_list():
        print repr(p.path)
