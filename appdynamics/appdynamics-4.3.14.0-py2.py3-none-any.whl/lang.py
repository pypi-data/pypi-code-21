from __future__ import unicode_literals
import functools
import inspect
import itertools
import os
import sys

# The aim here is make Python 2 behave like Python 3.
# This means we write code in modern Python 3 style, where everything is an
# iterator, everything is unicode etc.

# pylint: disable=import-error,no-name-in-module,no-member,undefined-variable

SUPER_FUN_HAPPY_PYTHON = sys.version_info[0] > 2

if SUPER_FUN_HAPPY_PYTHON:
    # Imports
    from configparser import SafeConfigParser
    from http.client import HTTPConnection, HTTPSConnection
    from http.cookies import SimpleCookie
    try:
        from importlib import reload
    except ImportError:
        from imp import reload
    import queue
    import _thread as thread
    from urllib.request import urlopen
    from urllib.parse import parse_qs, parse_qsl, urlparse

    # Types
    bytes_t = bytes
    long_t = int
    str_t = str

    # Functions
    filter = filter
    getcwd = os.getcwd
    items = lambda d: d.items()
    keys = lambda d: d.keys()
    long = int
    map = map
    range = range
    values = lambda d: d.values()
    zip = zip

    def get_args(callable):
        return inspect.signature(callable).parameters

    import importlib

    def import_module(name):
        return importlib.import_module(name)
else:
    # Imports
    from __builtin__ import reload
    from ConfigParser import SafeConfigParser
    from Cookie import SimpleCookie
    from httplib import HTTPConnection, HTTPSConnection
    import Queue as queue
    import thread
    from urllib import urlopen
    from urlparse import parse_qs, parse_qsl, urlparse

    # Types
    bytes_t = bytes
    long_t = long
    str_t = unicode

    # Functions
    filter = lambda f, it: itertools.ifilter(f, it)
    getcwd = os.getcwdu
    items = lambda d: d.iteritems()
    keys = lambda d: d.iterkeys()
    long = long
    map = lambda f, *it: itertools.imap(f, *it)
    range = xrange
    values = lambda d: d.itervalues()
    zip = lambda *it: itertools.izip(*it)

    def get_args(callable):
        return inspect.getargspec(callable).args

    import imp

    def import_module(name):
        file, pathname, desc = imp.find_module(name)
        try:
            return imp.load_module(name, file, pathname, desc)
        finally:
            if file is not None:
                file.close()

# Common Stuff
native_str = str
reduce = functools.reduce


def bytes(s, encoding='utf-8'):
    # Encode all bytes strings as utf-8.
    if isinstance(s, bytes_t):
        return s
    else:
        # This None thing isn't ideal, but since we use this function mainly
        # for making byte strings for protobufs, we want None to stay None.
        return None if s is None else s.encode(encoding)


def str(s, encoding='utf-8'):
    # Assume all bytes strings are utf-8 encoded.
    if isinstance(s, bytes_t):
        return s.decode(encoding)
    else:
        return str_t(s)
