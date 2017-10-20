'''Dumped: easy objects persistence

This module provides Dumped superclass.
You can use it to keep some data between program runs.

Example:
    >>> class Data(Dumped):
    ...     FIELDS = ['a', 'b']
    ...     filename = 'data.json'
    ...
    >>> d = Data()
    >>> d.a = 2
    >>> d2 = Data()
    >>> d2.a
    2
'''

import json
import os
import functools


DUMPED_KEYWORDS = ['_dump', '_load', '_init_dumper',
                   '_data', '_w', '_r', 'FIELDS',
                   'DUMPER', 'BINARY']
'''list: Words that cannot be used as a name for field'''


class DumpedClassError(Exception):
    '''This exception is raised when there is error in constructing Dumped class'''
    pass


class DumpedMeta(type):
    '''Metaclass for constructing Dumped classes.
    Performs checks on new class & patches __init__.

    Shouldn't be used itself, inherit from Dumped instead.

    Example:
        >>> class Data(Dumped):
        ...     pass
        ...
        Traceback (most recent call last):
            ...
        dumped.DumpedClassError: Dumped class must define filename attr
        >>>
        >>> class Data(Dumped):
        ...     filename = 'data.json'
        ...     FIELDS = ['_r']
        ...
        Traceback (most recent call last):
            ...
        dumped.DumpedClassError: _r can't be Dumped field
        >>>
        >>> class Data(Dumped):
        ...     filename = 'data.json'
        ...
        >>> d = Data()
        >>> d._data
        {}
        >>> # _data attr was defined in patched init
        '''
    def __new__(dumped_meta, class_name, class_parents, class_attr):
        fields = class_attr.get('FIELDS', [])
        if fields is not None:
            for kw in DUMPED_KEYWORDS:
                if kw in fields:
                    raise DumpedClassError("{} can't be Dumped field".format(kw))

        old_init = class_attr.get('__init__', None)
        if old_init is not None:
            @functools.wraps(old_init)
            def new_init(self, *args, **kwargs):
                old_init(self, *args, **kwargs)
                self._init_dumper()
            class_attr['__init__'] = new_init

        if 'filename' not in class_attr:
            raise DumpedClassError("Dumped class must define filename attr")

        return type.__new__(dumped_meta, class_name, class_parents, class_attr)


class Dumped(metaclass=DumpedMeta):
    '''Superclass for dumping data, itself.
    Inherit from it and define your own `filename` and you're ready to go!

    Attributes:
        FIELDS: List of fields to be dumped. If None, will dump every field but `DUMPED_KEYWORDS`.
        DUMPER: Object providing dump() and load() methods. Defaults to json.
        BINARY (bool): If True, will open files to "wb" and "rb" instead of "w" and "r".
        _data (dict): Data stored in object.
        _w (str): Mode for opening file to write.
        _r (str): Mode for opening file to read.

    Example:
        >>> import pickle
        >>> class Data(Dumped):
        ...     FIELDS = ['a', 'b'] # If not specified will be everything but DUMPED_KEYWORDS
        ...     DUMPER = pickle # If not specified will be json. Should provide json-like interface (dump, load)
        ...     BINARY = True # Need to specify it for opening files to "wb" and "rb" instead of "r" and "w"
        ...     def __init__(self, id):
        ...         self.id = id # We will use it for generating filenames
        ...         # No need to write anything else here, metaclass will do it for you
        ...     @property
        ...     def filename(self): # Can be just string if you want class to be singleton
        ...         return 'data-{}.pickle'.format(self.id)
        ...
        >>> d1 = Data(1)
        >>> d2 = Data(2)
        >>> d1.a
        >>> d1.a = 2
        >>> d1.a
        2
        >>> d2.a
        >>> d2.b = 3
        >>> d1.b
        >>> d2.b
        3
        >>> del d2.b
        >>> d2.b
        >>> d1.c
        Traceback (most recent call last):
            ...
        AttributeError: 'Data' object has no attribute 'c'
        '''
    FIELDS = None
    DUMPER = json
    BINARY = False
    filename = 'dumped.json'

    def __init__(self, *args, **kwargs):
        self._init_dumper()

    def _init_dumper(self):
        '''Initialize Dumper. Will be auto-called from child objects' __init__().'''
        self._data = dict()
        if self.__class__.BINARY:
            self._w = 'wb'
            self._r = 'rb'
        else:
            self._w = 'w'
            self._r = 'r'

        if not os.path.isfile(self.filename):
            self._dump()

    def _is_field(self, attrname):
        '''Check if `attrname` is field name for this Dumper class.

        Example:
            >>> class Data1(Dumped):
            ...     FIELDS = ['a']
            ...     filename = 'data1.json'
            ...
            >>> d1 = Data1()
            >>> d1._is_field('a')
            True
            >>> d1._is_field('b')
            False
            >>> class Data2(Dumped):
            ...     filename = 'data2.json'
            ...
            >>> d2 = Data2()
            >>> d2._is_field('a')
            True
            >>> d2._is_field('b')
            True
            >>> d2._is_field('_w')
            False
        '''
        if self.__class__.FIELDS is None:
            return attrname not in DUMPED_KEYWORDS
        else:
            return attrname in self.__class__.FIELDS

    def _dump(self):
        '''Dump object's data to file. Auto-called from __setattr__ and __delattr__.'''
        with open(self.filename, self._w) as file:
            self.__class__.DUMPER.dump(self._data, file)

    def _load(self):
        '''Load object's data from file. Auto-called from __getattr__.'''
        with open(self.filename, self._r) as file:
            self._data = self.__class__.DUMPER.load(file)

    def __getattr__(self, attrname):
        '''For fields returns object's _data field, otherwise uses object.__getattr__()'''
        if self._is_field(attrname):
            self._load()
            return self._data.get(attrname, None)
        else:
            return object.__getattribute__(self, attrname)

    def __setattr__(self, attrname, value):
        '''For fields sets object's _data field, otherwise uses object.__setattr__()'''
        if self._is_field(attrname):
            self._data[attrname] = value
            self._dump()
        else:
            object.__setattr__(self, attrname, value)

    def __delattr__(self, attrname):
        '''For fields sets object's _data field to None, otherwise uses object.__delattr__()

        Example:
            >>> class Data(Dumped):
            ...     FIELDS = ['a']
            ...     filename = 'data.json'
            ...
            >>> d = Data()
            >>> d.a = 2
            >>> d.a
            2
            >>> del d.a
            >>> d.a
            >>> del d._data # Don't do it!
            >>> d._data
            Traceback (most recent call last):
                ...
            AttributeError: 'Data' object has no attribute '_data'
            '''
        if self._is_field(attrname):
            self._data[attrname] = None
            self._dump()
        else:
            object.__delattr__(self, attrname)


__all__ = ['Dumped']
