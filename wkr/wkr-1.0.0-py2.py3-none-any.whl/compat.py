# -*- coding: utf-8 -*-

"""
py2/py3 compatibility.

compat.py
(c) Will Roberts  23 June, 2017
"""

from __future__ import absolute_import

import sys

PY2 = int(sys.version[0]) == 2

if PY2:
    text_type = unicode  # noqa
    binary_type = str
    string_types = (str, unicode)  # noqa
    unicode = unicode  # noqa
    basestring = basestring  # noqa
    chr = unichr
else:
    text_type = str
    binary_type = bytes
    string_types = (str,)
    unicode = str
    basestring = (str, bytes)
    chr = chr
