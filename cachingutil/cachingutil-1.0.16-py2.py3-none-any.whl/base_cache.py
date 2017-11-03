# encoding: utf-8
"""
base_cache.py

Provides base class for caching
"""

import time
import pprint
import logging
from timingsutil.timers import Throttle
from abc import ABCMeta, abstractmethod

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


class CacheError(Exception):
    pass


class Cache(object):

    """
    Subclass this to fetch and cache items, adding appropriate
    expiration rules.
    """

    __metaclass__ = ABCMeta  # Marks this as an abstract class

    def __init__(self,
                 throttle=None,
                 **params):
        """
        :param throttle:
        :param params: Discarded, but allows extraneous parameters to be passed
                       safely.
        """
        if throttle is None or isinstance(throttle, Throttle):
            self.throttle = throttle
        else:
            raise ValueError(u'throttle must be an instance of Throttle or None'
                             u' ({cls} was used)'
                             .format(cls=throttle.__class__))

    def key(self,
            **params):
        """
        Create a key into the cache

        :param params: list of parameters require to
                       create a key into the cache
        :return: key into the cache
        """
        raise NotImplemented(u"'key' has not been overridden in either "
                             u"the subclass definition or the subclass "
                             u"instance.")

    def fetch_from_source(self,
                          **params):
        """
        Fetch an uncached item.

        :param params: list of parameters required to
                       fetch the item and create a key
        :return: item to cache and return
        """
        raise NotImplemented(u"'fetch_from_source' has not been overridden in "
                             u"either the subclass definition or the subclass "
                             u"instance.")

    @staticmethod
    def cook(raw_item,
             **params):
        """
        If it's convenient to cache a modified version of the item that was
        fetched, it can be transformed here.
        :param raw_item: item to be cooked
        :param params: other parameters that may be required
        :return: cooked item
        """
        return raw_item

    @abstractmethod
    def cache(self,
              item,
              **params):
        """
        Store an item in the cache.

        :param item: item to be cached
        :param params: list of parameters required to
                       create a key into the cache
        :return: key into the cache
        """
        pass

    @abstractmethod
    def fetch_from_cache_by_key(self,
                                key):
        """
        Fetch the item from the cache by key

        :param key: key into cache
        :return:
        """
        pass

    @abstractmethod
    def delete_by_key(self,
                      key):
        """
        Delete an item from the cache.

        :param key: list of parameters required to
                    fetch the item and create a key
        """
        pass

    def delete(self,
               **params):
        """
        Delete an item from the cache.

        :param params: list of parameters required to
                       fetch the item and create a key
        """
        try:
            self.delete_by_key(self.key(**params))
        except TypeError as te:
            logging.exception(te)
            logging.error(u'params:')
            for p in params:
                logging.error(u'{param}'
                              .format(param=pprint.pformat(p)))
            raise te

    def clear_expired_items_from_cache(self):
        """
        Implement in subclass if required
        """
        pass

    def reset_cache(self):
        """
        Clears all cached items.
        
        """
        raise NotImplemented(u'reset_cache is not implemented for this cache')

    def cached_time(self,
                    key):
        """
        Get the global expiry time.

        Implement in subclass this if expiry_time
        can't be directly determined.

        :return: time in seconds when items older
                 than this should be deemed to have
                 expired
        """
        pass

    @abstractmethod
    def expiry_time(self,
                    key):
        """
        Get the expiry time of the item.

        :return: time in seconds when items older
                 than this should be deemed to have
                 expired
        """
        pass

    def _fetch_from_cache(self,
                          **params):
        """
        Fetch an item in the cache.

        :param params: list of parameters required to
                       create a key into the cache
        :return: item from cache
        """
        try:
            if not self.expired(**params):
                return self.fetch_from_cache_by_key(key=self.key(**params))
            raise CacheError()
        except KeyError:
            raise CacheError()
        except TypeError as te:
            logging.exception(te)
            logging.error(u'params:')
            for p in params:
                logging.error(u'{param}'
                              .format(param=pprint.pformat(p)))
            raise te

    def cached(self,
               **params):
        try:
            self._fetch_from_cache(self,
                                   **params)
            return True
        except:
            return False

    def pre_fetch_tasks(self,
                        **params):
        """
        Optional to implement in subclass.
        An example use is to clear expired items from the cache.

        :param params:
        :return: n/a
        """
        pass

    def expired(self,
                key = None,
                **params):
        """
        Returns a flag to indicate if the item in the cache
        for the given key has expired.

        DO NOT RE-IMPLEMENT IN SUBCLASS

        :param key: key to the item in the cache
               **params: alternative to allow for checking outside
                         the caching class without needing the key.
        :return: bool: True if the item has expired from the cache
        """
        try:
            key = (key
                   if key is not None
                   else self.key(**params))
        except TypeError as te:
            logging.exception(te)
            logging.error(u'Actual params:')
            for p in params:
                logging.error(u'{param}'
                              .format(param=pprint.pformat(p)))
            #TODO: Add formal parameters for self.key
            raise te
        try:
            return self.expiry_time(key) <= time.time()
        except KeyError as ke:
            raise CacheError(ke)

    def fetch(self,
              **params):
        """
        If an item is not in the cache or has expired, it is
        fetched from source and cached.
        If it in the cache an not expired, it's fetched from
        the cache and returned.

        DO NOT RE-IMPLEMENT IN SUBCLASS

        :param params: parameters required to generate a unique key
                       into the cache and to fetch uncached items
        :return: cached or uncached item.

        Pro-Tip:
        If you see this error:

        TypeError: fetch() takes exactly 1 argument (2 given)

        You've probably forgotten to used named parameters
        """
        self.pre_fetch_tasks(**params)

        try:
            cached_value = self._fetch_from_cache(**params)
            return cached_value
        except CacheError:
            pass

        # When not fetching from the cache, wait for the throttle expiry
        try:
            self.throttle.wait()
        except AttributeError:
            pass  # No throttle

        raw_item = self.fetch_from_source(**params)

        cooked_item = self.cook(raw_item,
                                **params)

        self.cache(item=cooked_item,
                   **params)

        return cooked_item
