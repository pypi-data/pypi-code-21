#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: hoonds.patterns.observer
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Here we have the means by which to implement the sometimes controversial, but often useful
`singleton <https://en.wikipedia.org/wiki/Singleton_pattern>`_ pattern.
"""


class _Singleton:
    """
    This is a singleton wrapper class.  New instances are created for each decorated class.
    """

    def __init__(self, cls: type):
        """

        :param cls: the decorated class
        """
        self.__multiplet__: type = cls  #: the original, non-singleton class
        self._instance = None  #: the single instance

    def __call__(self, *args, **kwargs):
        """
        Return a single instance of the decorated class.
        :return: the singleton instance
        """
        if self._instance is None:
            self._instance = self.__multiplet__(*args, **kwargs)
        return self._instance


def singleton(cls):
    """
    Use this decorator to declare your class as a singleton instance.  You can use the __multiplet__ attribute to
    access the decorated class in tests.
    """
    return _Singleton(cls)
