# coding=utf-8

"""
A Mash behaves like both a dictionary and a NameSpace.  This is a very simple implementation,
attribute accessors are just added onto a dictionary.  So a['foo'] == a.foo

Keys must be hashable.  If a key is not a valid attribute name, then it can only be accessed
using dict accessors.


For example:

..code-block:: python

    a = Mash()
    a['foo'] = 'bar'
    assert a['foo'] == 'bar'
    assert a.foo == 'bar'
    a.foo = 'fig'
    assert a['foo'] == 'fig'
    assert a.foo == 'fig'

"""
import collections

from argparse import Namespace

__docformat__ = 'restructuredtext en'

class Mash(dict):
    """
    dictionary keys must be hashable.

    Inherits dict behavior so we just extend by adding attribute accessing.
    """

    def __init__(self, obj=None):
        if obj is None:
            super(Mash, self).__init__(dict())
        elif isinstance(obj, collections.Mapping):
            super(Mash, self).__init__(obj)
        elif isinstance(obj, dict):
            super(Mash, self).__init__(obj)
        elif isinstance(obj, Namespace):
            super(Mash, self).__init__(vars(obj))
        elif isinstance(obj, Mash):
            super(Mash, self).__init__(vars(obj))

    def __getattr__(self, key):
        """
        Support self.key read access

        :param key: the mash dictionary key
        :type key: collections.Hashable
        :return: the value or None
        :rtype: object|None
        :raises: TypeError
        """
        if not isinstance(key, collections.Hashable):
            raise TypeError("The key ({key}) is not hashable".format(key=str(key)))
        if key not in self:
            self[key] = None
        # noinspection PyTypeChecker
        return self[key]

    def __setattr__(self, key, value):
        """
        Support self.key write access

        :param key: the mash dictionary key
        :type key: collections.Hashable
        :param value: the value to associate with the key
        :type value: object
        :return: this instance
        :rtype: Mash
        :raises: TypeError
        """
        if not isinstance(key, collections.Hashable):
            raise TypeError("The key ({key}) is not hashable".format(key=str(key)))
        self[key] = value
        return self

    def __delattr__(self, key):
        """
        Support deleting: del self.key

        :param key: the mash dictionary key
        :type key: collections.Hashable
        :return: this instance
        :rtype: Mash
        :raises: TypeError
        """
        if not isinstance(key, collections.Hashable):
            raise TypeError("The key ({key}) is not hashable".format(key=str(key)))
        # noinspection PyTypeChecker
        del self[key]
        return self

    def __eq__(self, other):
        # print('{src}.__eq__({other})'.format(src=repr(self), other=repr(other)))
        if other is None:
            # print("if other is None:")
            return vars(self) == {}
        elif isinstance(other, Mash):
            # print("elif isinstance(other, Mash):")
            return vars(self) == vars(other)
        elif isinstance(other, collections.Mapping):
            # print("elif isinstance(other, collections.Mapping):")
            return vars(self) == other
        elif isinstance(other, dict):
            # print("elif isinstance(other, dict):")
            return vars(self) == other
        elif isinstance(other, Namespace):
            # print("elif isinstance(other, Namespace):")
            return vars(self) == vars(other)
        else:
            # print("else:")
            return vars(self) == vars(other)


Namespace.__eq__ = Mash.__eq__
