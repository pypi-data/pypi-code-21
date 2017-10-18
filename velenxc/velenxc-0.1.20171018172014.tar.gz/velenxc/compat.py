# -*- coding: utf-8 -*-

""" Everything is for compatibility """

from __future__ import absolute_import

import sys

PY3 = (sys.version_info[0] == 3)

if PY3:
    STRING_TYPES = str,


    def py_str(x):
        """ convert c string back to python string """

        return x.decode('utf-8')
else:  # pragma: no cover
    STRING_TYPES = basestring,


    def py_str(x):
        """ convert c string back to python string """

        return x

try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle
