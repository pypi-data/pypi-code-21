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
    >>> class Human(Dumped):
    ...     def __init__(self, name):
    ...         self.name = name
    ...     @property
    ...     def filename(self): # Filename can be dynamic!
    ...         return str(self.name) + '.json' # Be sure to convert all fields to str, even if you sure it is.
    ...                                         # Everything is None until initialized.
    ...                                         # Yes, filename can be called before __init__.
    ...
    >>> man = Human('John')
    >>> man.age = 23
    >>> man.age
    23
    >>> man.name = 'Smith' # Switching to another file. John.json is saved, now we're working with Smith.json
    >>>                    # Probably, you don't want to do so: it's not intuitive to reset whole file when connecting.
    >>>                    # Better create another object with new name.
    >>> man.age # Now Smith also have age 23, because man dumped to it
    23
    >>> man.age = 25
    >>> man.age
    25
    >>> Human('John').age # But John still have age == 23
    23
    >>> # To prevent it, it's recommended to make fields used in filename readonly.
    >>> class Row(Dumped):
    ...     READONLY = ['id']
    ...     def __init__(self, id):
    ...         self.id = id
    ...     @property
    ...     def filename(self):
    ...         return 'row-' + str(self.id) + '.json'
    ...
    >>> row = Row(1)
    >>> row.id
    1
    >>> row.data = 'Hello!'
    >>> row.data
    'Hello!'
    >>> row.id = 2
    Traceback (most recent call last):
        ...
    dumped.DumpedReadonlyError: Trying to change Row.id, which is readonly
'''

import json
import os
import functools


DUMPED_KEYWORDS = ['_dump', '_load', '_init_dumper',
                   '_data', '_w', '_r',  '_init_state',
                   'FIELDS', 'DUMPER', 'BINARY']
'''list: Words that cannot be used as a name for field'''

DUMPED_OBJS = dict()
'''dict: Filename → obj. Used to make Dumped objects singletons.'''


class DumpedClassError(Exception):
    '''This exception is raised when there is error in constructing Dumped class'''
    pass


class DumpedReadonlyError(Exception):
    '''This exception is raised when program tries to change readonly field'''
    pass


class DumpedMeta(type):
    '''Metaclass for constructing Dumped classes.
    Performs checks on new class & patches __init__.
    Also manages file access: Dumped objs are singletons on one filename.

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
        >>> class SomeData(Dumped):
        ...     filename = 'somedata.json'
        ...
        >>> d = SomeData()
        >>> d._data
        {}
        >>> # _data attr was defined in patched init
        >>>
        >>> class Cat(Dumped):
        ...     filename = 'cat.json'
        ...
        >>> a = Cat()
        >>> b = Cat()
        >>> a is b # It's the same cat!
        True
        >>> class Dog(Dumped):
        ...     filename = 'cat.json'
        ...
        >>> c = Dog() # Trying to create dog instead of cat
        Traceback (most recent call last):
            ...
        dumped.DumpedClassError: cat.json is already used by Cat
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
                self._init_state = True
                self._data = dict()
                if self.__class__.BINARY:
                    self._w = 'wb'
                    self._r = 'rb'
                else:
                    self._w = 'w'
                    self._r = 'r'
                old_init(self, *args, **kwargs)
                self._init_dumper()
                self._load()
                self._init_state = False
            class_attr['__init__'] = new_init

        if 'filename' not in class_attr:
            raise DumpedClassError("Dumped class must define filename attr")

        return type.__new__(dumped_meta, class_name, class_parents, class_attr)

    def __call__(cls, *args, **kwargs):
        instance = super(DumpedMeta, cls).__call__(*args, **kwargs)
        if instance.filename in DUMPED_OBJS:
            if type(DUMPED_OBJS[instance.filename]) == cls:
                return DUMPED_OBJS[instance.filename]
            else:
                raise DumpedClassError("{} is already used by {}".format(instance.filename,
                                                                         type(DUMPED_OBJS[instance.filename]).__name__))
        DUMPED_OBJS[instance.filename] = instance
        return instance


class Dumped(metaclass=DumpedMeta):
    '''Superclass for dumping data, itself.
    Inherit from it and define your own `filename` and you're ready to go!

    Attributes:
        FIELDS: List of fields to be dumped. If None, will dump every field but `DUMPED_KEYWORDS`.
        READONLY: List of fields which can be set only in __init__.
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
    READONLY = []
    DUMPER = json
    BINARY = False
    filename = 'dumped.json'

    def __init__(self, *args, **kwargs):
        self._init_dumper()

    def _init_dumper(self):
        '''Initialize Dumper. Will be auto-called from child objects' __init__().'''
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
            return self._data.get(attrname, None)
        else:
            return object.__getattribute__(self, attrname)

    def __setattr__(self, attrname, value):
        '''For fields sets object's _data field, otherwise uses object.__setattr__()'''
        if self._is_field(attrname):
            if attrname in self.__class__.READONLY and not self._init_state:
                raise DumpedReadonlyError('Trying to change {}.{}, which is readonly'.format(self.__class__.__name__,
                                                                                             attrname))
            old_filename = self.filename
            self._data[attrname] = value
            if not self._init_state:
                if self.filename != old_filename:
                    del DUMPED_OBJS[old_filename]
                    DUMPED_OBJS[self.filename] = self
                self._dump()
        else:
            object.__setattr__(self, attrname, value)

    def __delattr__(self, attrname):
        '''For fields sets object's _data field to None, otherwise uses object.__delattr__()

        Example:
            >>> class OtherData(Dumped):
            ...     FIELDS = ['a']
            ...     filename = 'otherdata.json'
            ...
            >>> d = OtherData()
            >>> d.a = 2
            >>> d.a
            2
            >>> del d.a
            >>> d.a
            >>> del d._data # Don't do it!
            >>> d._data
            Traceback (most recent call last):
                ...
            AttributeError: 'OtherData' object has no attribute '_data'
            '''
        if self._is_field(attrname):
            self._data[attrname] = None
            self._dump()
        else:
            object.__delattr__(self, attrname)


__all__ = ['Dumped']
