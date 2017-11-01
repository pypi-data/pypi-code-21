#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import json
import os

from .dir import LocalDir

DEFAULT_CONF = os.environ.get('USERPROFILE', os.environ.get('HOME', '.')) + '/' + '.hsync.json'
DEFAULT_SYNC_DIR = 'all'


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


def json_decode(json_str):
    try:
        return json.loads(json_str)
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


def run():
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
                    pass
                    print '[old][%s]\t%s' % (f.get_mod_time(), f.path)
            print c['name'], 'end sync'


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


if __name__ == '__main__':
    run()
