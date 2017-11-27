#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import sys


IS_PY2 = sys.version_info.major == 2


if not IS_PY2:
    p3_str = str
    p3_bytes = bytes
    p3_chr = chr
    p3_input = input

    def iteritems(x):
        return x.items()

    OpenFileException = FileNotFoundError
else:
    p3_str = unicode  # noqa: F821
    p3_bytes = str
    p3_chr = unichr  # noqa: F821
    p3_input = raw_input  # noqa: F821

    def iteritems(x):
        return x.iteritems()

    OpenFileException = IOError
