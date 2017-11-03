""":mod:`util` module contains utility functions and classes for :mod:`latest` package.

"""

import os.path
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


def is_scalar(obj):
    return isinstance(obj, (bool, int, float, complex, str))


def is_vector(obj):
    return isinstance(obj, (set, frozenset, tuple, list)) and (not is_scalar(obj))


def is_tensor(obj):
    return (not is_scalar(obj)) and (not is_vector(obj))


def path(location):
    return os.path.abspath(os.path.expanduser(location))


def getopt(parser, section, key, default):
    try:
        if hasattr(parser, '__getitem__'):
            return parser[section][key]
        else:
            return parser.get(section, key)
    except:
        return default
