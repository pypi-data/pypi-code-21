# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate
