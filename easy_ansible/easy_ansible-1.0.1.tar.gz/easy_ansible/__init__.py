#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
easy_ansible library
~~~~~~~~~~~~~~~~~~~~~
An ansible api that can be used directly and easily.

:copyright: (c) 2017 by CcccFz.
:license: Apache2, see LICENSE for more details.

usage:
    See using example on 'test.py'.

"""

from ansible import __version__ as VERSION

if VERSION < '2':
    from ansible_19_api import Command
else:
    from ansible_24_api import PlayQueue, EachPlay
