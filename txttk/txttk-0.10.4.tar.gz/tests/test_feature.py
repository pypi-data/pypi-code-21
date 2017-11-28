#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import unittest
from collections import OrderedDict
from txttk import feature

class FeatureTestCase(unittest.TestCase):
    def test_lexical(self):
        token = 'Hello'
        result = feature.lexical(token)
        wanted = OrderedDict([
                ('lowercase', 'hello'),
                ('first4', 'hell'),
                ('last4', 'ello')
                ])
        self.assertEqual(result, wanted)
    
    def test_char_shape(self):
        char = 'X'
        wanted = 'A'
        result = feature._char_shape(char)
        self.assertEqual(result, wanted)
        
        char = '8'
        wanted = '0'
        result = feature._char_shape(char)
        self.assertEqual(result, wanted)
        
        char = '-'
        wanted = '-'
        result = feature._char_shape(char)
        self.assertEqual(result, wanted)
        
    def test_shape(self):
        token = 'Abc-987'
        wanted = 'Aaa-000'
        result = feature._shape(token)
        self.assertEqual(result, wanted)
        
    def test_contains_a_letter(self):
        token = 'a123'
        result = feature._contains_a_letter(token)
        self.assertTrue(result)
        
        token = '1234'
        result = feature._contains_a_letter(token)
        self.assertFalse(result)
    
    def test_contains_a_capital(self):
        token = 'A001'
        result = feature._contains_a_capital(token)
        self.assertTrue(result)
        
        token = 'abcd'
        result = feature._contains_a_capital(token)
        self.assertFalse(result)
    
    def test_all_capital(self):
        token = 'XYZ'
        result = feature._all_capital(token)
        self.assertTrue(result)
        
        token = 'XyZ'
        result = feature._all_capital(token)
        self.assertFalse(result)
        
    def test_contains_a_digit(self):
        token = 'A001'
        result = feature._contains_a_digit(token)
        self.assertTrue(result)
        
        token = 'ab-xy'
        result = feature._contains_a_digit(token)
        self.assertFalse(result)
        
    def test_all_digit(self):
        token = '1238'
        result = feature._all_digit(token)
        self.assertTrue(result)
        
        token = 'A123'
        result = feature._all_digit(token)
        self.assertFalse(result)
        
    def test_contains_a_punctuation(self):
        token = 'abc*'
        result = feature._contains_a_punctuation(token)
        self.assertTrue(result)
        
        token = 'a123'
        result = feature._contains_a_punctuation(token)
        self.assertFalse(result)
        
    def test_consists_letters_n_digits(self):
        token = 'Ax123'
        result = feature._consists_letters_n_digits(token)
        self.assertTrue(result)
    
        token = '1-2-3'
        result = feature._consists_letters_n_digits(token)
        self.assertFalse(result)
    
    def test_consists_digits_n_punctuations(self):
        token = '123-123-123'
        result = feature._consists_digits_n_punctuations(token)
        self.assertTrue(result)
        
        token = 'ax123-422'
        result = feature._consists_digits_n_punctuations(token)
        self.assertFalse(result)
    
    def test_orthographic(self):
        token = 'JeroYang123'
        result = feature.orthographic(token)
        wanted = ['AaaaAaaa000',
                  11,
                  True,
                  True,
                  True,
                  False,
                  True,
                  False,
                  False,
                  True,
                  False
                  ]
        self.assertEqual(list(result.values()), wanted)