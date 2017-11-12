#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import collections

import six


__version__ = '0.0.12'


def regular_cast(original, *attempts):
    for attem in attempts:
        if not callable(attem):
            return attem
        try:
            return attem(original)
        except (TypeError, ValueError):
            pass
    return original


def smart_cast(value, default):
    """
    Cast to the same type as `default`;
    if fail, return default
    :param value:
    :param default:
    :return:
    """
    func = type(default)
    try:
        return func(value)
    except (TypeError, ValueError):
        return default


def numerify(s):
    return regular_cast(s, int, float)


def want_bytes(s, **kwargs):
    """
    :param s: 
    :param kwargs: key word arguments passed to str.encode(..)
    :return: 
    """
    if not isinstance(s, six.binary_type):
        s = s.encode(**kwargs)
    return s


def want_unicode(s, **kwargs):
    """
    :param s: 
    :param kwargs: key word arguments passed to bytes.decode(..)
    :return: 
    """
    if not isinstance(s, six.text_type):
        return s.decode(**kwargs)
    return s


def want_str(s, **kwargs):
    """
    :param s:
    :param kwargs: key word arguments passed to s.decode(..)
    :return:
    """
    if not isinstance(s, str):
        return s.decode(**kwargs)
    return s


def namedtuple_to_dict(nt):
    fields = getattr(nt, '_fields')
    return collections.OrderedDict(zip(fields, nt))


def represent(obj, fields):
    c = obj.__class__.__name__
    parts = ('{}={}'.format(k, repr(getattr(obj, k))) for k in fields)
    s = ', '.join(parts)
    return '<{}({}) at {}>'.format(c, s, hex(id(obj)))

