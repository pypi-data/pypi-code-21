# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import re
import filecmp
import hashlib
import unicodedata
from io import open
from builtins import str
from functools import partial
try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence

from six import string_types

from pyfileinfo.file import File


class PyFileInfo(Sequence):
    def __init__(self, path):
        Sequence.__init__(self)

        self._path = unicodedata.normalize('NFC', str(path))
        self._instance = None

    def __lt__(self, other):
        def split_by_number(file_path):
            def to_int_if_possible(c):
                try:
                    return int(c)
                except:  # noqa: E722
                    return c.lower()

            return [to_int_if_possible(c) for c in re.split('([0-9]+)', file_path)]

        return split_by_number(self.path) < split_by_number(other.path)

    def __hash__(self):
        return self._path.__hash__()

    def __eq__(self, other):
        if isinstance(other, string_types):
            return filecmp.cmp(self.path, other, False)

        if isinstance(other, PyFileInfo):
            return filecmp.cmp(self.path, other.path, False)

        return False

    def __str__(self):
        return self._path

    def __getattr__(self, item):
        for class_ in File.__subclasses__():
            if item == 'is_{}'.format(class_.__name__.lower()):
                if self._instance is None:
                    return lambda: class_.is_valid(self.path)

                return lambda: isinstance(self.instance, class_)

        return getattr(self.instance, item)

    def __getitem__(self, item):
        return self.instance[item]

    def __len__(self):
        return len(self.instance)

    def is_hidden(self):
        return self.name[0] in ['.', '$', '@']

    def is_exists(self):
        return os.path.exists(self.path)

    @property
    def instance(self):
        if self._instance is None:
            classes = sorted(File.__subclasses__(),
                             key=lambda class_: self.extension in class_.hint(),
                             reverse=True)
            self._instance = File(self.path)
            for class_ in classes:
                if not class_.is_valid(self.path):
                    continue

                self._instance = class_(self.path)
                break

        return self._instance

    @property
    def path(self):
        return self._path

    @property
    def extension(self):
        return os.path.splitext(self.path)[1]

    @property
    def name(self):
        return os.path.split(self.path)[1]

    @property
    def body(self):
        return PyFileInfo(os.path.split(self.path)[0])

    @property
    def md5(self):
        return self._calculate_hash(hashlib.md5)

    def relpath(self, start):
        return os.path.relpath(self.path, start)

    def _calculate_hash(self, hash_algorithm):
        with open(self.path, mode='rb') as f:
            digest = hash_algorithm()
            for buf in iter(partial(f.read, 128), b''):
                digest.update(buf)

        return digest.hexdigest()
