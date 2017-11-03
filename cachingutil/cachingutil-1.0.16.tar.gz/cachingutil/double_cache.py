# encoding: utf-8

"""
two_level_cache.py

Provides class for joining two caches. e.g. in-memory cache and file-cache
"""

import time
import requests
import logging
import pprint
from abc import ABCMeta, abstractmethod
from base_cache import Cache

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2017 Hywel Thomas'


class TwoLevelCache(object):

    def __init__(self,
                 transient_cache,
                 persistent_cache,
                 key=None,
                 **params):
        """
        Two layer cache. Transient cache is accessed first. It the item
        can't be found, Persistent cache is accessed.

        :param transient_cache:
        :param persistent_cache:
        :param key:
        :param params:
        """
        self.persistent_cache = persistent_cache(**params)
        self.transient_cache = transient_cache(**params)

        if key:
            self.persistent_cache.key = key
            self.transient_cache.key = key
        else:
            self.transient_cache.key = self.persistent_cache.key
        self.key = self.persistent_cache.key
        self.transient_cache.fetch_from_source = self.persistent_cache.fetch

    def clear_expired_items_from_cache(self):
        self.transient_cache.clear_expired_items_from_cache()
        self.persistent_cache.clear_expired_items_from_cache()

    def delete(self,
               **params):
        self.transient_cache.delete(**params)
        self.persistent_cache.delete(**params)

    def reset_cache(self):
        self.transient_cache.reset_cache()
        self.persistent_cache.reset_cache()

    def fetch(self,
              **params):
        return self.transient_cache.fetch(**params)

        # TODO: Add other methods, e.g. add, delete, clear