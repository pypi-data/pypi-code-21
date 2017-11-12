#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools


MAX_STR_ATTR_LENGTH = 2000


def attr_length_validator(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):

        nargs = []
        for arg in args:
            if isinstance(arg, basestring):
                nargs.append(arg[:MAX_STR_ATTR_LENGTH])
            else:
                nargs.append(arg)

        for key, value in kwargs.iteritems():
            if isinstance(value, basestring):
                kwargs[key] = value[:MAX_STR_ATTR_LENGTH]

        return func(*nargs, **kwargs)
    return inner
