# -*- coding: utf-8 -*-

from __future__ import absolute_import

import yaml
from io import open
try:
    from collections.abc import Sequence
except ImportError:
    from collections import Sequence

from pyfileinfo.file import File


class YAML(File, Sequence):
    def __init__(self, file_path):
        File.__init__(self, file_path)
        Sequence.__init__(self)

        self._instance = None

    def __str__(self):
        return '%s\n%s' % (self.path, yaml.dump(self.instance))

    def __getitem__(self, item):
        return self.instance[item]

    def __len__(self):
        return len(self.instance)

    def __getattr__(self, item):
        return getattr(self.instance, item)

    @staticmethod
    def hint():
        return ['.yml']

    @staticmethod
    def is_valid(path):
        try:
            yaml.load(open(path, encoding='utf8'))
        except Exception:  # noqa: E722
            return False

        return True

    @property
    def instance(self):
        if self._instance is None:
            self._instance = yaml.load(open(self.path, encoding='utf8'))

        return self._instance
