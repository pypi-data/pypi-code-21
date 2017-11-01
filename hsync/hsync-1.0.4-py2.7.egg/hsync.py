# !/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import hashlib
import json
import os
import re
import time

import requests
from flask import Flask, request
from werkzeug.routing import BaseConverter

DEFAULT_CONF = os.environ.get('USERPROFILE', os.environ.get('HOME', '.')) + '/' + '.hsync.json'
DEFAULT_SYNC_DIR = 'all'

sep = '/'


def _parse_args_local():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', default=DEFAULT_CONF, help='config file default: $HOME/.hsync.json',
                        metavar='hsync.json')
    parser.add_argument('-d', '--dir', nargs='*', default=DEFAULT_SYNC_DIR, help='need sync dir',
                        metavar='dir')
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0',
    )
    return parser.parse_args()


def unicode_in_iter_to_utf8(iterable):
    if type(iterable) == unicode:
        return iterable.encode('utf-8')
    if type(iterable) == dict:
        new_dict = {}
        for k, v in iterable.items():
            new_dict[unicode_in_iter_to_utf8(k)] = unicode_in_iter_to_utf8(v)
        return new_dict
    if type(iterable) == tuple or type(iterable) == list:
        new_list = []
        for v in iterable:
            new_list.append(unicode_in_iter_to_utf8(v))
        return new_list

    return iterable


def json_decode(json_str):
    try:
        return unicode_in_iter_to_utf8(json.loads(json_str))
    except ValueError:
        return None


def init_conf(filename):
    with open(filename) as f:
        return json_decode(f.read())


def get_dir_name_list(conf):
    dir_name = {}
    for section in conf:
        section['need_sync'] = False
        dir_name[section['name']] = section
    return dir_name


def local():
    args = _parse_args_local()
    conf = init_conf(args.conf)
    dir_name = get_dir_name_list(conf)
    sync_dir = args.dir

    if DEFAULT_SYNC_DIR in sync_dir:
        for d in dir_name.values():
            d['need_sync'] = True
        print 'sync all dir'
    else:
        for s in sync_dir:
            if s in dir_name:
                dir_name[s]['need_sync'] = True
            else:
                print s, 'not in the conf file'

    for c in dir_name.values():
        if c['need_sync'] is True:
            print c['name'], 'start sync'
            local_dir = LocalDir(c)
            local_file = local_dir.get_file_list()
            for i in range(len(local_dir.server_list)):
                server_file_list = local_dir.request(i)
                new, update, old, same = diff(local_file, server_file_list)
                for f in (update | new):
                    local_dir.post(i, f)
                for f in old:
                    print '[old][%s]\t%s' % (f.get_mod_time(), f.path)
            print c['name'], 'end sync'


class RegexConverter(BaseConverter):
    def __init__(self, _map, *args):
        super(RegexConverter, self).__init__(_map)
        self.map = map
        self.regex = args[0]


def _parse_args_server():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--port', default=6688, help='http server bind port default: 6688')

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.1',
    )
    return parser.parse_args()


def server():
    args = _parse_args_server()

    app = Flask(__name__)

    app.url_map.converters['regex'] = RegexConverter

    @app.route('/<regex("([\/\w-]+)*$"):root_path>', methods=['GET'])
    def get(root_path):
        root_path = '/' + root_path
        server_dir = ServerDir(root_path, (), ())
        return json.dumps([i.__dict__ for i in server_dir.get_file_list()])

    @app.route('/<regex("([\/\w-]+)*$"):root_path>', methods=['POST'])
    def post(root_path):
        root_path = '/' + root_path
        os.chdir(root_path)
        file_data = request.get_data()

        f = File.from_json(file_data)
        f.write_file(request.files.get('file'))
        return 'success!'

    app.run(host='0.0.0.0', debug=False, port=args.port)


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
        self.server_list = [LocalDir.ServerPart(server['remote_path'], server['remote_url']) for server in
                            conf['server']]

    def request(self, index):
        tree_list = requests.get(self.server_list[index].get_request_url()).content
        if len(tree_list) == 0:
            return None
        return [File.from_dict(j) for j in json.loads(tree_list)]

    def post(self, index, file_data):
        print 'uploading %s' % file_data.path
        requests.post(self.server_list[index].get_request_url(), data=file_data.to_json(), files={'file': file_data.open()})
        file_data.fp.close()


class File:
    def __init__(self, path, md5=None, access_time=None, mod_time=None):
        if type(path) != unicode:
            path = path.decode('utf-8')
        if type(md5) != unicode:
            md5 = md5.decode('utf-8')
        self.path = sep.join(path.split(os.sep))
        self.md5 = md5file(path) if md5 is None else md5
        self.access_time = int(os.path.getctime(self.path)) if access_time is None else access_time
        self.mod_time = int(os.path.getmtime(self.path)) if mod_time is None else mod_time
        self.fp = None

    def get_mod_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.mod_time))

    def __eq__(self, other):
        return self.path == other.path and self.md5 == other.md5 and self.mod_time == other.mod_time and self.access_time == other.access_time

    def __hash__(self):
        return hash(self.path) ^ hash(self.md5) ^ hash(self.mod_time) ^ hash(self.access_time)

    def open(self):
        self.fp = open(self.path, 'rb')
        return self.fp

    def write_file(self, fp):
        p_path = os.path.split(self.path)[0]
        if p_path != '' and not os.path.exists(p_path):
            os.makedirs(p_path)
        fp.save(self.path)
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
        return File(path=dict_data['path'], md5=dict_data['md5'], access_time=dict_data['access_time'],
                    mod_time=dict_data['mod_time'])


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


if __name__ == '__main__':
    p = json.dumps(File('hsync.py').__dict__)
    print json.loads(p, cls=File)
