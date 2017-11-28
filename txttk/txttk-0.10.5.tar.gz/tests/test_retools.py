#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

"""
test_retools
----------------------------------

Tests for `retools` module.
"""

import unittest
from txttk import retools
import re

class RetoolsTestCase(unittest.TestCase):
    def test_condense(self):
        words = ['hello', 'hellokitty', 'hellomonkey', 'goodbye', 'hell',
                 'he', 'his', 'hi', 'bye', 'history', 'story', 'condense',
                 'hematoma', 'lymphoma']
        regex = retools.condense(words)
        condensed = re.compile(regex)
        for word in words:
            self.assertTrue(condensed.match(word))

        negative_words = ['akkk', 'adadkjkl ', 'avxnbcjn']
        for word in negative_words:
            self.assertFalse(condensed.match(word))

    def test_is_solid(self):
        regex = r'a'
        self.assertTrue(retools.is_solid(regex))
        regex = r'[ab]'
        self.assertTrue(retools.is_solid(regex))
        regex = r'(a|b|c)'
        self.assertTrue(retools.is_solid(regex))
        regex = r'(a|b|c)?'
        self.assertTrue(retools.is_solid(regex))
        regex = r'(ab)c'
        self.assertFalse(retools.is_solid(regex))
        regex = r'(ab)c?'
        self.assertFalse(retools.is_solid(regex))
        regex = r'(a)(b|c)'
        self.assertFalse(retools.is_solid(regex))
        regex = r'(a)(b|c)?'
        self.assertFalse(retools.is_solid(regex))

    def test_is_packed(self):
        regex = r'a'
        self.assertFalse(retools.is_packed(regex))
        regex = r'[ab]'
        self.assertFalse(retools.is_packed(regex))
        regex = r'(a|b|c)'
        self.assertTrue(retools.is_packed(regex))
        regex = r'(ab)c'
        self.assertFalse(retools.is_packed(regex))

    def test_consolidate(self):
        regex = r'a|b'
        wanted = r'(a|b)'
        result = retools.consolidate(regex)
        self.assertEqual(result, wanted)

        regex = r'[ab]'
        wanted = r'[ab]'
        result = retools.consolidate(regex)
        self.assertEqual(result, wanted)

        regex = r'(?:a|b)'
        wanted = r'(?:a|b)'
        result = retools.consolidate(regex)
        self.assertEqual(result, wanted)

    def test_danger_unpack(self):
        regex = r'(abc)'
        wanted = r'abc'
        result = retools.danger_unpack(regex)
        self.assertEqual(result, wanted)

        regex = r'(?:abc)'
        wanted = r'abc'
        result = retools.danger_unpack(regex)
        self.assertEqual(result, wanted)

        regex = r'(?P<xyz>abc)'
        wanted = r'abc'
        result = retools.danger_unpack(regex)
        self.assertEqual(result, wanted)

        regex = r'[abc]'
        wanted = r'[abc]'
        result = retools.danger_unpack(regex)
        self.assertEqual(result, wanted)

    def test_unpack(self):
        regex = r'(abc)'
        wanted = r'abc'
        result = retools.unpack(regex)
        self.assertEqual(result, wanted)

        regex = r'(?:abc)'
        wanted = r'abc'
        result = retools.unpack(regex)
        self.assertEqual(result, wanted)

        regex = r'(?P<xyz>abc)'
        wanted = r'(?P<xyz>abc)'
        result = retools.unpack(regex)
        self.assertEqual(result, wanted)

        regex = r'[abc]'
        wanted = r'[abc]'
        result = retools.unpack(regex)
        self.assertEqual(result, wanted)

    def test_parallel(self):
        result = retools.parallel([r'abc', r'def'])
        wanted = r'abc|def'
        self.assertEqual(result, wanted)

        result = retools.parallel([r'abc', r'd|ef'])
        wanted = 'abc|d|ef'
        self.assertEqual(result, wanted)

        result = retools.parallel([r'abc', r'(d|ef)'])
        wanted = 'abc|d|ef'
        self.assertEqual(result, wanted)

        result = retools.parallel([r'abc', r'defg'], sort=True)
        wanted = 'defg|abc'
        self.assertEqual(result, wanted)
        
    def test_nocatch(self):
        regex = r'a|b'
        wanted = r'(?:a|b)'
        result = retools.nocatch(regex)
        self.assertEqual(result, wanted)

        regex = r'(a|b)'
        wanted = r'(?:a|b)'
        result = retools.nocatch(regex)
        self.assertEqual(result, wanted)

        regex = r'(?P<x>ab)'
        wanted = r'(?:ab)'
        result = retools.nocatch(regex)
        self.assertEqual(result, wanted)

        regex = r'[ab]'
        wanted = r'[ab]'
        result = retools.nocatch(regex)
        self.assertEqual(result, wanted)

    def test_concat(self):
        regex_1 = r'a|b'
        regex_2 = r'(c|de)'
        regex_3 = r'[fg]'

        result_12 = retools.concat([regex_1, regex_2])
        wanted_12 = r'(a|b)(c|de)'
        self.assertEqual(result_12, wanted_12)

        result_13 = retools.concat([regex_1, regex_3])
        wanted_13 = r'(a|b)[fg]'
        self.assertEqual(result_13, wanted_13)

        result_123 = retools.concat([regex_1, regex_2, regex_3])
        wanted_123 = r'(a|b)(c|de)[fg]'
        self.assertEqual(result_123, wanted_123)

    def test_nocatchall(self):
        regex = r'abc'
        wanted = r'abc'
        result = retools.nocatchall(regex)
        self.assertEqual(result, wanted)

        regex = r'(abc)'
        wanted = r'(?:abc)'
        result = retools.nocatchall(regex)
        self.assertEqual(result, wanted)

        regex = r'(?:abc)'
        wanted = r'(?:abc)'
        result = retools.nocatchall(regex)
        self.assertEqual(result, wanted)

        regex = r'(?P<xyz>abc)'
        wanted = r'(?:abc)'
        result = retools.nocatchall(regex)
        self.assertEqual(result, wanted)

        regex = r'(abc(?P<xyz>def))'
        wanted = r'(?:abc(?:def))'
        result = retools.nocatchall(regex)
        self.assertEqual(result, wanted)

        regex = r'\(abc\)'
        wanted = r'\(abc\)'
        result = retools.nocatchall(regex)
        self.assertEqual(result, wanted)

    def test_option(self):
        regex = r'abc'
        wanted = r'(?:abc)?'
        result = retools.option(regex)
        self.assertEqual(result, wanted)

        regex = r'(abc)'
        wanted = r'(?:abc)?'
        result = retools.option(regex)
        self.assertEqual(result, wanted)

        regex = r'[abc]'
        wanted = r'[abc]?'
        result = retools.option(regex)
        self.assertEqual(result, wanted)
