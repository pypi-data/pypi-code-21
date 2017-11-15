##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test that the Zope appserver configuration schema can be loaded.
"""
import os.path
import unittest

import ZConfig


class TestConfiguration(unittest.TestCase):

    def test_schema(self):
        dir = os.path.dirname(os.path.dirname(__file__))
        filename = os.path.join(dir, "schema.xml")
        ZConfig.loadSchema(filename)
