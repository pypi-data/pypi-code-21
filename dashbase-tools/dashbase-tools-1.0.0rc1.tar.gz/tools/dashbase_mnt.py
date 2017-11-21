#!/usr/bin/env python
from __future__ import print_function, absolute_import, division

import logging
import os
import re
from stat import S_IFDIR, S_IFREG
from sys import argv, exit
from time import time

from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, ENOENT
from treelib import Tree

from tools.dashbase import DashbaseClient
from utils.local_cache import LocalCache
from utils.rpc import RPC

# init logging config
logging.basicConfig(level=logging.INFO)


def split_filename_and_sql(filename):
    """
    matching data"?sql=select *"
    return basic_filename, sql or filename, None
    """
    pattern = r'(?P<filename>\S+)\?sql=(?P<sql>[\w\s*,]+)'
    r = re.match(pattern, filename)
    if r:
        basic_filename = r.groupdict()['filename']
        extend_sql = r.groupdict()['sql']
    else:
        basic_filename = filename
        extend_sql = None
    return basic_filename, extend_sql


class FNode(object):
    def __init__(self, is_dir=False, is_file=False, size=0, ctime=time(), mtime=time(), atime=time()):
        self.is_dir = is_dir
        self.is_file = is_file
        if self.is_dir:
            self.attr = dict(st_mode=(S_IFDIR | 0o755), st_nlink=2)
        if self.is_file:
            self.attr = dict(st_mode=(S_IFREG | 0o755), st_nlink=1, st_size=size,
                             st_ctime=ctime, st_mtime=mtime, st_atime=atime)
        self.attr["attrs"] = {}


class FileSystemTree(object):
    def __init__(self):
        self.tree = Tree()
        self.fd = 0
        self.tree.create_node("root", "/", data=FNode(is_dir=True))

    def create_file(self, path, parent, size=0, ctime=time(), mtime=time(), atime=time()):
        data = FNode(is_file=True, size=size, ctime=ctime, mtime=mtime, atime=atime)
        self.tree.create_node(path, identifier=path, parent=parent,
                              data=data)

    def create_dir(self, path, parent):
        data = FNode(is_dir=True)
        self.tree.create_node(path, identifier=path, parent=parent,
                              data=data)

    def get_node(self, path):
        return self.tree.get_node(path)


class DashbaseMount(LoggingMixIn, Operations):
    """Example memory filesystem. Supports only one level of files."""

    def __init__(self, rpc):
        self.fd = 0
        self.rpc = rpc
        self.client = DashbaseClient(rpc)
        self.tree = FileSystemTree()
        self.cache = LocalCache()

    def update_tables(self):
        self.tree = FileSystemTree()
        tables = self.client.get_tables()
        if tables is None:
            print('\nCan\'t get table information from api.')
            print('Did you set the right address?\n')
            print('You can use "dashbase_umnt" to stop "dashbase_mnt".\n')
            return 0
        for t in tables:
            path = os.path.join("/", t)
            self.tree.create_dir(path, "/")
            self.tree.create_file(os.path.join(path, "data"), path, size=99999)
            self.tree.create_file(os.path.join(path, "info"), path, size=99999)
            self.tree.create_file(os.path.join(path, "schema"), path, size=99999)

    def chmod(self, path, mode):
        return 0

    def chown(self, path, uid, gid):
        return 0

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        data = self.cache[path] if path in self.cache.keys() else ''

        table_name = os.path.dirname(path)[1:]
        if path.endswith("info"):
            data = self.client.get_info(table_name)

        if path.endswith("schema"):
            data = self.client.get_schema(table_name)

        if len(data) <= offset:
            return 0

        if len(data) <= offset + size:
            return data[offset:]
        return data[offset: offset + size]

    def readdir(self, path, fh):
        self.update_tables()
        node = self.tree.get_node(path)
        if not node:
            raise FuseOSError(ENOENT)
        result = ['.', '..']
        if not path.endswith("/"):
            path += "/"

        for i in node.fpointer:
            result.append(i[len(path):])

        return result

    def getattr(self, path, fh=None):
        if path == '/':
            node = self.tree.get_node(path)
        else:
            prefix, filename = os.path.split(path)
            basic_filename, extend_sql = split_filename_and_sql(filename)
            if basic_filename == 'data':
                if not extend_sql:
                    extend_sql = "select * from {}".format(os.path.basename(prefix))
                self.cache[path] = self.client.get_data(extend_sql)
                node = self.tree.get_node(os.path.join(prefix, basic_filename))
            else:
                node = self.tree.get_node(path)
        if not node:
            raise FuseOSError(ENOENT)

        return node.data.attr

    def getxattr(self, path, name, position=0):
        node = self.tree.get_node(path)
        if not node:
            raise FuseOSError(ENOENT)

        try:
            return node.data.attr["attrs"][name]
        except KeyError:
            return ''

    def listxattr(self, path):
        node = self.tree.get_node(path)
        if not node:
            raise FuseOSError(ENOENT)

        try:
            return node.data.attr["attrs"]
        except KeyError:
            return {}


def main():
    if len(argv) != 3:
        name = argv[0].rsplit('/')[-1]
        print('usage: {} <dashbase api url> <mountpoint> &'.format(name))
        print('example: {} https://api.dashbase.example.com:9876 dashbase &'.format(name))
        exit(1)

    logging.basicConfig(level=logging.INFO)
    rpc = RPC(argv[1])
    try:
        FUSE(DashbaseMount(rpc), argv[2], foreground=True)
    except RuntimeError as e:
        if e.message:
            print('RuntimeError occurred!')
            print(e.message)
    finally:
        rpc.close()
