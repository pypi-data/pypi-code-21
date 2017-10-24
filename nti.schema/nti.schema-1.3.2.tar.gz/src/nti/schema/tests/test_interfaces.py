#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for interfaces.py

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# stdlib imports
import unittest

from ..interfaces import InvalidValue

from hamcrest import assert_that
from hamcrest import has_property
from hamcrest import none

__docformat__ = "restructuredtext en"

#disable: accessing protected members, too many methods
#pylint: disable=W0212,R0904

class TestInvalidValue(unittest.TestCase):

    def test_construct(self):
        v = InvalidValue()
        assert_that(v, has_property('value', none()))
        assert_that(v, has_property('field', none()))

        v = InvalidValue(value=1, field=1)
        assert_that(v, has_property('value', 1))
        assert_that(v, has_property('field', 1))
