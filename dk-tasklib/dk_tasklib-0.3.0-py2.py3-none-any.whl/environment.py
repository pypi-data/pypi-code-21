# -*- coding: utf-8 -*-
"""
Global state.
"""
import six


class Environment(object):
    def __call__(self, ctx):
        return ctx


env = Environment()


