# encoding: utf-8
"""
binary_file_cache.py

Provides class for caching binary data in files.
"""

import os
import sys
import codecs
import pprint
import logging
from abc import ABCMeta, abstractmethod
from base_file_cache import BaseFileCache, CacheError

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class BinaryFileCache(BaseFileCache):

    __metaclass__ = ABCMeta  # Marks this as an abstract class

    # Also re-implement fetch_from_source and key

    @staticmethod
    def read(filepath):
        with open(name=filepath,
                  mode=u'rb') as cached_file:
            return cached_file.read()

    @staticmethod
    def write(item,
              filepath):
        with open(name=filepath,
                  mode=u'wb') as cached_file:
            cached_file.write(item)
