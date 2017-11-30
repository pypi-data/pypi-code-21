from __future__ import unicode_literals, print_function

import os
import sys

import itertools
from argparse import ArgumentTypeError

import furl as furl

PY3 = sys.version_info[0] == 3

if PY3:
    from urllib.parse import quote as urlquote
else:
    from urllib import quote as urlquote


def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.

    From django.utils.encoding.
    """
    if not PY3:
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, str('temporary_class'), (), {})


def build_url(base, *segments, **query):
    url = furl.furl(base)
    # Filters return generators
    # Cast to list to force "spin" it
    url.path.segments = list(filter(
        lambda segment: segment,
        map(
            # Furl requires everything to be quoted or not, no mixtures allowed
            # prequote everything so %signs don't break everything
            lambda segment: urlquote(str(segment).strip('/')),
            # Include any segments of the original url, effectively list+list but returns a generator
            itertools.chain(url.path.segments, segments)
        )
    ))
    url.args = query
    return url.url


class FilePathType(object):
    """Factory for creating file path types

    Instances of FilePathType are typically passed as type= arguments to the
    ArgumentParser add_argument() method.
    """

    def __call__(self, string):
        # all other arguments are used as file names
        path = os.path.abspath(string)
        if not os.path.exists(path):
            raise ArgumentTypeError("Can't open '{}'".format(string))

        return path

    def __repr__(self):
        return type(self).__name__


class CommaSeparatedSet(object):
    def __call__(self, string):
        values = set(filter(lambda v: v.strip(), string.split(',')))
        if not values:
            raise ArgumentTypeError("List is empty")

        return values

