#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import functools
import sys


def make_key(args, kwargs, tuple=tuple, hash=hash):
    '''
    Hash function for function arguments.

    :param args: argument iterable
    :type args: iterable
    :param kwargs: keyword argument dict-like object
    :type kwargs: dict
    :returns: hash of arg and kwargs
    :rtype: int
    '''
    return hash(tuple(
        [(value, value.__class__) for value in args] +
        [(key, value, value.__class__) for key, value in kwargs.items()]
        ))


class LFUDACache(object):
    '''
    Less Frequenty Used with Dynamic Aging cache.

    Implementation note:
        Instances will be created from their own different subclass.

        As a side effect, the effective instance type won't be this class, so
        avoid :func:`type` conparisons and use :func:`isinstance` instead.

    How it works:
        * Every cache hit increases item HIT counter.
        * Every cache miss increases THRESHOLD, until max HITS is reached.
        * When full, a new cache item will only be accepted if THRESHOLD is
          above or equals the less frequently used item's HIT counter. Said
          item is evicted.
        * When a new item is cached, its HIT counter is set equal to THRESHOLD
          itself.
        * When an existing item is updated, its HIT counter is incremented 
          by 1 above THRESHOLD.
        * When any item's HITS reaches MAX_HITS, said value is substracted
          from every HIT and THRESHOLD counter.
    '''

    @classmethod
    def _implement(cls, properties):
        '''
        LFUDACache._implement(properties) -> New type instance

        Creates a subclass from current class containing given properties.

        :param properties: class property dictionary
        :type properties: dict
        :return: instance of subtype
        '''
        return type('%sImplementation' % cls.__name__, (cls, ), properties)()

    @staticmethod
    def _drift(size):
        '''
        LFUDACache.drift(size)

        Substract given drift value to HITS and THRESHOLD

        :param drift: value to substract from HITS and THRESHOLD
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def get(key, default=None):
        '''
        LFUDACache.get(key[,default]) -> value

        Get value of key from cache.

        :param key: cache item key
        :param default: optional default parameter
        :returns: cache item value
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def __getitem__(key):
        '''
        LFUDACache[key] -> value

        Get value of key from cache.

        If key is not found, KeyError is raised.

        :param key: cache item key
        :param default: optional default parameter
        :returns: cache item value
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def __setitem__(key, value):
        '''
        LFUDACache[key] = value

        Set value for key in cache.

        :param key: cache item key
        :param value: cache item value
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def __delitem__(key):
        '''
        del LFUDACache[key]

        Remove specified key and return the corresponding value.
        If key is not found KeyError is raised.

        :param key: cache item key
        :param value: cache item value
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def __contains__(key):
        '''
        key in LFUDACache -> True if cached, False otherwise

        :returns: True if key is cached, False otherwise
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def pop(key, default=None):
        '''
        LFUDACache.pop(key[,default]) -> value

        Remove specified key and return the corresponding value.
        If key is not found, default is returned if given, otherwise
        KeyError is raised.

        :param key: cache item key
        :param default: optional default parameter
        :returns: cache item value
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def items():
        '''
        LFUDACache.items() => iterable of key and value tuples

        Iterable of cache pairs (key, value) sorted from most to lesser
        frequently used.

        :yields: (key, value) tuples
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def keys():
        '''
        LFUDACache.keys() -> iterable of keys

        Iterable of cache keys sorted from most to lesser
        frequently used.

        :yields: key
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def __iter__():
        '''
        iter(LFUDACache) -> iterable of keys

        Iterable of cache keys sorted from most to lesser
        frequently used.

        :yields: key
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def values():
        '''
        LFUDACache.values() -> iterable of values

        Iterable of cache values sorted from most to lesser
        frequently used.

        :yields: value
        '''
        raise RuntimeError('Method only available on instances')

    @staticmethod
    def clear():
        '''
        LFUDA.clear()

        Evict the entire cache.
        '''
        raise RuntimeError('Method only available on instances')

    @property
    def threshold(self):
        '''
        Current threshold level
        '''
        raise RuntimeError('Property only available on instances')

    @staticmethod
    def __len__():
        '''
        len(LFUDACache) -> current cache size
        '''
        raise RuntimeError('Method only available on instances')

    def __new__(cls, maxsize):
        '''
        Implement all methods on a subclass and return instance.

        :param maxsize: maximum cache size
        :type maxsize: int
        :returns: instance of subtype
        '''
        NOT_FOUND = object()
        MAX_HITS = sys.maxsize
        KEY, VALUE, HITS, PREV, NEXT, THRESHOLD, FLAG = range(7)
        ITEMSIZE = THRESHOLD
        ROOTSIZE = 7

        CACHE = {}
        ROOT = [None, None, MAX_HITS, None, None, 0, False]
        ROOT[PREV:THRESHOLD] = ROOT, ROOT

        def drift(size):
            for item in CACHE.values():
                item[HITS] -= size
            ROOT[THRESHOLD] -= size

        def get(key, default=None):
            item = CACHE.get(key, NOT_FOUND)
            if item is NOT_FOUND:
                if ROOT[THRESHOLD] < ROOT[PREV][HITS]: 
                    ROOT[THRESHOLD] += 1
                return default

            item[HITS] += 1

            # already sorted
            if item[HITS] < item[NEXT][HITS]:
                return item[VALUE]

            # avoid overflow
            if item[HITS] == MAX_HITS:
                drift(MAX_HITS)

            # extract
            item[PREV][NEXT] = item[NEXT]
            item[NEXT][PREV] = item[PREV]

            # position (start on next)
            next = item[NEXT][NEXT]
            hits = item[HITS]
            while hits >= next[HITS]:
                next = next[NEXT]

            # insert
            item[PREV:ITEMSIZE] = next[PREV], next
            item[PREV][NEXT] = item
            item[NEXT][PREV] = item

            # invalidate iterators
            ROOT[FLAG] = False

            return item[VALUE]

        def getitem(key):
            value = get(key, NOT_FOUND)
            if value is NOT_FOUND:
                raise KeyError('Key %r not found.' % key)
            return value

        def setitem(key, value):
            item = CACHE.get(key, NOT_FOUND)

            if item is NOT_FOUND:
                if len(CACHE) == maxsize:
                    item = ROOT[NEXT]
                    if ROOT[THRESHOLD] < item[HITS]:
                        return value  # not expirable yet

                    # uncache
                    del CACHE[item[KEY]]

                    # extract
                    item[PREV][NEXT] = item[NEXT]
                    item[NEXT][PREV] = item[PREV]

                item = [key, value, ROOT[THRESHOLD], ROOT, ROOT[NEXT]]
                CACHE[key] = item
            else:
                item[VALUE] = value
                item[HITS] = max(ROOT[THRESHOLD], item[HITS]) + 1

                # already sorted
                if item[HITS] < item[NEXT][HITS]:
                    return value

                # avoid overflow
                if item[HITS] == MAX_HITS:
                    drift(MAX_HITS)

                # extract
                item[PREV][NEXT] = item[NEXT]
                item[NEXT][PREV] = item[PREV]

            # position
            next = item[NEXT]
            hits = item[HITS]
            while hits >= next[HITS]:
                next = next[NEXT]

            # insert
            item[PREV:ITEMSIZE] = next[PREV], next
            item[PREV][NEXT] = item
            item[NEXT][PREV] = item

            # invalidate iterators
            ROOT[FLAG] = False

            return value

        def delitem(key):
            item = CACHE.pop(key, NOT_FOUND)
            if item is NOT_FOUND:
                raise KeyError('Key %r not found.' % key)

            # extract
            item[PREV][NEXT] = item[NEXT]
            item[NEXT][PREV] = item[PREV]

        def pop(key, default=NOT_FOUND):
            item = CACHE.pop(key, NOT_FOUND)
            if item is NOT_FOUND:
                if default is NOT_FOUND:
                    raise KeyError('Key %r not found.' % key)
                return default

            # extract
            item[PREV][NEXT] = item[NEXT]
            item[NEXT][PREV] = item[PREV]

            return item[VALUE]

        def items():
            ROOT[FLAG] = True
            prev = ROOT[PREV]
            while prev is not ROOT and ROOT[FLAG]:
                yield prev[KEY], prev[VALUE]
                prev = prev[PREV]

            if not ROOT[FLAG]:
                raise RuntimeError('cache order changed during iteration')

        def keys():
            for k, _ in items():
                yield k

        def iter():
            for k, _ in items():
                yield k

        def values():
            for _, v in items():
                yield v

        def clear():
            CACHE.clear()
            ROOT[PREV:ROOTSIZE] = ROOT, ROOT, 0, 0

        def threshold(self):
            return ROOT[THRESHOLD]

        def new(cls):
            if hasattr(cls, 'instance'):
                raise RuntimeError('This class cannot be used directly.')
            cls.instance = object.__new__(cls)
            return cls.instance 

        properties = dict(
            __iter__=iter,
            __delitem__=delitem,
            __setitem__=setitem,
            __getitem__=getitem,
            _drift=drift,
            get=get,
            pop=pop,
            items=items,
            keys=keys,
            values=values,
            clear=clear,
            )

        for name, fnc in properties.items():
            fnc.__doc__ = getattr(cls, name).__doc__

        properties.update(
            __contains__=CACHE.__contains__,
            __len__=CACHE.__len__,
            )

        for name, fnc in properties.items():
            properties[name] = staticmethod(fnc)

        properties.update(
            __new__=new,
            _threshold=property(threshold),
            _root=ROOT,
            _data=CACHE,
            )

        return cls._implement(properties)


def memoize(maxsize, fnc=None, key_fnc=make_key):
    '''
    Memoization decorator using Less Frequenty Used with Dynamic Aging cache
    eviction algorithm.

    The LFUDACache instance is available on the decorated function, as `cache`
    property.

    :param maxsize: maximum cache size
    :type maxsize: int
    :param fnc: optional function to memoize
    :type fnc: callable or None
    :param key_fnc: optional custom cache key function, receiving argument
                    list and keyword argument dict
    :type key_fnc: callable
    :returns: decorator if fnc is not given, wrapped function otherwise
    :rtype: callable
    '''

    if not isinstance(maxsize, int):
        raise TypeError('Expected maxsize to be an integer')

    def decorator(fnc):
        NOT_FOUND = object()
        cache = LFUDACache(maxsize)
        getitem, setitem = cache.get, cache.__setitem__

        @functools.wraps(fnc)
        def wrapped(*args, **kwargs):
            key = key_fnc(args, kwargs)
            result = getitem(key, NOT_FOUND)
            if result is NOT_FOUND:
                result = fnc(*args, **kwargs)
                setitem(key, result)
            return result
        wrapped.cache = cache
        return wrapped
    return decorator(fnc) if callable(fnc) else decorator
