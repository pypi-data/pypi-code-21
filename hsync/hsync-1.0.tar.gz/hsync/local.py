#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import sys

from file import LocalDir, diff

DEFAULT_CONF = '.hsync.json'


# 递归方式转化所有unicode为utf8
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


# 避免json解析错误抛出异常 并转化结果为utf8 解析错误返回None
def json_decode(json_str):
    try:
        return unicode_in_iter_to_utf8(json.loads(json_str))
    except ValueError, e:
        return None


def init_conf(filename):
    with open(filename) as f:
        return json_decode(f.read())


# def get_dir_name_list(conf):
#     return [{'name': section['name'], 'conf': section} for section in conf]


def run():
    home = os.environ.get('USERPROFILE', os.environ.get('HOME', '.'))
    if len(sys.argv) == 1:
        conf_filename = home + '/' + DEFAULT_CONF
    else:
        conf_filename = sys.argv[1]

    conf = init_conf(conf_filename)

    for c in conf:
        local_dir = LocalDir(c)
        local_file = local_dir.get_file_list()
        for i in range(len(local_dir.server_list)):
            server_file_list = local_dir.request(i)
            new, update, old, same = diff(local_file, server_file_list)
            for f in (update | new):
                local_dir.post(i, f)
            for f in old:
                print '[old][%s]\t%s' % (f.get_mod_time(), f.path)
