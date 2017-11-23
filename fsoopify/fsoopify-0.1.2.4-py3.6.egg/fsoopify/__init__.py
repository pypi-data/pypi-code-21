#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017~2999 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os

class Path(str):
    def __init__(self, val):
        if not isinstance(val, str):
            raise TypeError
        self._path = str(val)
        self._dirname, self._name = os.path.split(self._path)
        self._pure_name, self._ext = os.path.splitext(self._name)

    def __repr__(self):
        return '{}(\'{}\')'.format(type(self).__name__, self._path)

    @property
    def dirname(self):
        ''' get directory path from path. '''
        return self._dirname

    @property
    def name(self):
        ''' get name from path. '''
        return self._name

    @property
    def pure_name(self):
        ''' get name without ext from path. '''
        return self._pure_name

    @property
    def ext(self):
        ''' get ext from path. '''
        return self._ext

    def is_ext_equals(self, val):
        if not isinstance(val, str):
            raise TypeError
        return self._ext.lower() == val.lower()

    def replace_dirname(self, val):
        if not isinstance(val, str):
            raise TypeError
        return Path(os.path.join(val, self._name))

    def replace_name(self, val):
        if not isinstance(val, str):
            raise TypeError
        return Path(os.path.join(self._dirname, val))

    def replace_pure_name(self, val):
        if not isinstance(val, str):
            raise TypeError
        return Path(os.path.join(self._dirname, val + self._ext))

    def replace_ext(self, val):
        if not isinstance(val, str):
            raise TypeError
        return Path(os.path.join(self._dirname, self._pure_name + val))


class NodeInfo:
    def __init__(self, path):
        self._path: Path = Path(path)

    def __str__(self):
        return str(self._path)

    def __repr__(self):
        return '{}(\'{}\')'.format(type(self).__name__, self._path)

    @property
    def path(self):
        ''' return a Path object. '''
        return self._path

    def is_exists(self):
        raise NotImplementedError

    def is_directory(self):
        ''' check if this is a exists directory. '''
        return False

    def is_file(self):
        ''' check if this is a exists file. '''
        return False

    def rename(self, dest_path: str):
        ''' use `os.rename()` to move the node. '''
        if not isinstance(dest_path, str):
            raise TypeError
        os.rename(self._path, dest_path)
        self._path = Path(dest_path)

    @staticmethod
    def from_path(path):
        ''' create from path. '''
        if os.path.isdir(path):
            return DirectoryInfo(path)
        elif os.path.isfile(path):
            return FileInfo(path)
        else:
            return None


class FileInfo(NodeInfo):
    def __init__(self, path):
        super().__init__(path)

    def is_exists(self):
        return os.path.isfile(self._path)

    def copy_to(self, dest_path: str, buffering: int=-1):
        ''' copy the file to dest path. '''
        with open(self._path, 'rb', buffering=buffering) as source:
            # use x mode to ensure dest does not exists.
            with open(dest_path, 'xb') as dest:
                for buffer in source:
                    dest.write(buffer)

    def is_file(self):
        ''' check if this is a exists file. '''
        return self.is_exists()


class DirectoryInfo(NodeInfo):
    def __init__(self, path):
        super().__init__(path)

    def is_exists(self):
        return os.path.isdir(self._path)

    def is_directory(self):
        ''' check if this is a exists directory. '''
        return self.is_exists()

    def list_items(self, deep: int=1):
        ''' get items from directory. '''
        if deep != None and not isinstance(deep, int):
            raise TypeError
        items = []
        def itor(root, d):
            if d != None:
                d -= 1
                if d < 0:
                    return
            for name in os.listdir(root):
                path = os.path.join(root, name)
                node = NodeInfo.from_path(path)
                items.append(node)
                if isinstance(node, DirectoryInfo):
                    itor(path, d)
        itor(self._path, deep)
        return items
