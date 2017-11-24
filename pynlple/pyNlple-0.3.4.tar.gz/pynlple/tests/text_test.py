# -*- coding: utf-8 -*-
import unittest

from pynlple.processing.dictionary import DictionaryLookUp, DictionaryBasedTagger
from pynlple.processing.text import ClassTokenFilter


class ClassTokenFilterTest(unittest.TestCase):

    def setUp(self):
        self.mappings = [
            ('a b', 'c1'),
            ('a b c', 'c1'),
            ('.', 's'),
            (',', 's'),
            ('d', 'c2'),
            ('e', 'c2'),
            ('f', 'c3'),
            ]
        self.dictionary_lookup = DictionaryLookUp(self.mappings)
        self.tagger = DictionaryBasedTagger(self.dictionary_lookup)

    def test_should_not_filter_no_representatives(self):
        filter_ = ClassTokenFilter(self.tagger, ['s'])
        tokens = 'y n n y n'.split()

        expected_tokens = 'y n n y n'.split()
        self.assertEqual(expected_tokens, filter_.filter(tokens))

    def test_should_filter_s_class_no_other_classes(self):
        filter_ = ClassTokenFilter(self.tagger, ['s'])
        tokens = 'y n . n y , n'.split()

        expected_tokens = 'y n n y n'.split()
        self.assertEqual(expected_tokens, filter_.filter(tokens))

    def test_should_filter_s_class_with_other_classes(self):
        filter_ = ClassTokenFilter(self.tagger, ['s'])
        tokens = 'y n a b . n d e f y , n a b c'.split()

        expected_tokens = 'y n a b n d e f y n a b c'.split()
        self.assertEqual(expected_tokens, filter_.filter(tokens))

    def test_should_filter_two_classes_no_other_classes(self):
        filter_ = ClassTokenFilter(self.tagger, ['s', 'c3'])
        tokens = 'y f n . n f y , n f'.split()

        expected_tokens = 'y n n y n'.split()
        self.assertEqual(expected_tokens, filter_.filter(tokens))

    def test_should_filter_two_classes_with_other_classes(self):
        filter_ = ClassTokenFilter(self.tagger, ['s', 'c3'])
        tokens = 'y n f a b . n d e f y , n f a b c'.split()

        expected_tokens = 'y n a b n d e y n a b c'.split()
        self.assertEqual(expected_tokens, filter_.filter(tokens))

    def test_should_filter_all_known_classes(self):
        filter_ = ClassTokenFilter(self.tagger)
        tokens = 'y n f a b . n d e f y , n f a b c'.split()

        expected_tokens = 'y n n y n'.split()
        self.assertEqual(expected_tokens, filter_.filter(tokens))
