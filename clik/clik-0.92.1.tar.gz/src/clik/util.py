# -*- coding: utf-8 -*-
"""
The ever-present utilities module.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""


class AttributeDict(dict):
    """
    Simple :class:`dict` wrapper that allows key access via attribute.

    Example::

        d = AttributeDict(foo='bar', baz='qux')
        d['foo']      # 'bar'
        d.foo         # 'bar'
        d['baz']      # 'qux'
        d.baz         # 'qux'
        d.foo = 'bup'
        d['foo']      # 'bup'
        d.foo         # 'bup'
        del d.foo
        d.foo         # KeyError

    """

    def __getattr__(self, name):
        """Get via attribute name."""
        return self[name]

    def __setattr__(self, name, value):
        """Set via attribute name."""
        self[name] = value

    def __delattr__(self, name):
        """Delete via attribute name."""
        del self[name]
