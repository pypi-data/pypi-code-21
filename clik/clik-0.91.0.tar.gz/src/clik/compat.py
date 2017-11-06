# -*- coding: utf-8 -*-
"""
Python compatibility helpers.

:author: Joe Joyce <joe@decafjoe.com>
:copyright: Copyright (c) Joe Joyce and contributors, 2009-2017.
:license: BSD
"""
import sys


#: Indicates whether we are on Python 2.
#:
#: :type: :class:`bool`
PY2 = sys.version_info[0] == 2

#: Indicates whether we are on Python 2.6.
#:
#: :type: :class:`bool`
PY26 = sys.version_info[0:2] == (2, 6)

#: Indicates whether we are on Python 3.3.
#:
#: :type: :class:`bool`
PY33 = sys.version_info[0:2] == (3, 3)

# LINT: Ignore undocumented function violations. Compatibility code is not
#       formally documented.

if PY2:
    def iteritems(d, *args, **kwargs):  # noqa: D103
        return d.iteritems(*args, **kwargs)

    def implements_bool(cls):  # noqa: D103
        cls.__nonzero__ = cls.__bool__
        del cls.__bool__
        return cls
else:
    def iteritems(d, *args, **kwargs):  # noqa: D103
        return iter(d.items(*args, **kwargs))

    def implements_bool(cls):  # noqa: D103
        return cls
