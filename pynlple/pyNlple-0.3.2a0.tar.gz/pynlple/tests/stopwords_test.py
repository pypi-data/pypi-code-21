# -*- coding: utf-8 -*-
import unittest

from pynlple.module import abs_path

from pynlple.processing.dictionary import FileFolderTokenMapping
from pynlple.processing.stopwords import DictionaryStopwordsFilter


class StopwordsFilterTest(unittest.TestCase):

    def test_should_init_with_default_params(self):
        self.filter = DictionaryStopwordsFilter(FileFolderTokenMapping('punctuation.txt', data_folder=abs_path(__file__, 'data/stopwords')))
        self.assertIsNotNone(self.filter)

    def test_should_filter_with_provided_dictionary(self):
        self.filter = DictionaryStopwordsFilter(FileFolderTokenMapping('punctuation.txt', data_folder=abs_path(__file__, 'data/stopwords')))
        tokens = 'These are some tokens , we need to filter ! So , don\'t be so shy to do it .'.split()

        expected_tokens = 'These are some tokens we need to filter So don\'t be so shy to do it'.split()
        self.assertEqual(expected_tokens, self.filter.filter(tokens))

    def test_should_filter_with_provided_dictionary_and_preprocessing_rule(self):
        preprocessing = lambda x: x if len(x) > 2 else '.'
        self.filter = DictionaryStopwordsFilter(FileFolderTokenMapping('punctuation.txt', data_folder=abs_path(__file__, 'data/stopwords')),
                                                prep=preprocessing)
        tokens = 'These are some tokens , we need to filter ! So , don\'t be so shy to do it .'.split()

        expected_tokens = 'These are some tokens need filter don\'t shy'.split()
        self.assertEqual(expected_tokens, self.filter.filter(tokens))
