#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

import unittest
from hamcrest import assert_that
from hamcrest import is_
from hamcrest import none
from hamcrest import has_property

from ..interfaces import InvalidValue

class TestInvalidValue(unittest.TestCase):

    def test_construct(self):
        v = InvalidValue()
        assert_that(v, has_property('value', none()))
        assert_that(v, has_property('field', none()))

        v = InvalidValue(value=1, field=1)
        assert_that(v, has_property('value', 1))
        assert_that(v, has_property('field', 1))
