# encoding: utf-8
"""
file_cache.py

Provides class for file based caching with encoding a decoding
"""

import codecs
from abc import ABCMeta
from base_file_cache import BaseFileCache

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class FileCache(BaseFileCache):

    __metaclass__ = ABCMeta  # Marks this as an abstract class

    # Also re-implement key, fetch_from_source, read and write

    def encode(self,
               data):
        """
        Converts the data into a writable form.

        Re-implement if serialisation is required. (e.g. using pickle)

        :param data: data/object to serialise
        :return: serialised data
        """
        encoded = data
        return encoded

    def decode(self,
               encoded):
        """
        Converts the raw data read into a usable form.

        Re-implement if serialisation is required. (e.g. using pickle)

        :param encoded: serialise data to de-serialise
        :return: de-serialised data
        """
        decoded = encoded
        return decoded

    def read(self,
             filepath):
        with codecs.open(filename=filepath,
                         encoding=self.encoding,
                         mode=u'r') as cached_file:
            return self.decode(cached_file.read())

    def write(self,
              item,
              filepath):
        with codecs.open(filename=filepath,
                         encoding=self.encoding,
                         mode=u'w') as cached_file:
            cached_file.write(self.encode(item))

    u"""
        ┌────────────────────────────┐
        │ Don't re-implement methods │
        │ below when subclassing...  │
        └────────────────────────────┘
     """

    def __init__(self,
                 max_age=0,
                 folder=None,
                 encoding=u'UTF-8',
                 **params):
        """
        Adds encoding to instance vars of BaseFileCache
        """
        super(FileCache, self).__init__(max_age=max_age,
                                        folder=folder,
                                        **params)
        self.encoding = encoding

