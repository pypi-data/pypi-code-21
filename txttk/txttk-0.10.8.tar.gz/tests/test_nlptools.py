#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function)
from builtins import *

import unittest
from txttk import nlptools

class NlptoolsTestCase(unittest.TestCase):
    def setUp(self):
        self.sentences = """A common problem faced by biocurators when using text mining systems is that these are difficult to use or do not provide an output that can be directly exploited by biocurators during their literature curation process.
In this respect, the BioCreative Interactive {Text Mining} (IAT) task has served as a great means to observe the approaches, standards and functionalities used by state-of-the-art text mining systems with potential applications in the biocuration domain.
The IAT task also provides a means for biocurators to be directly involved in the testing of text mining systems.
For the upcoming BioCreative V, seven teams have submitted a text mining/NLP system targeted to a specific biocuration task.
These systems will be formally evaluated by users, but not competitively.""".split('\n')
        self.context = " ".join(self.sentences)

    def test_sent_tokenize(self):
        result = [s.strip() for s in nlptools.sent_tokenize(self.context)]
        self.assertEqual(result, self.sentences)

    def test_sent_tokenize_intergration(self):
        self.assertEqual(''.join(nlptools.sent_tokenize(self.context)), self.context)

    def test_sent_count(self):
        self.assertEqual(nlptools.sent_count(self.context), 5)

    def test_clause_tokenize(self):
        sentence = self.sentences[1]
        wanted = ['In this respect, the BioCreative Interactive {Text Mining} (IAT) task has served as a great means to observe the approaches,',
                  ' standards and functionalities used by state-of-the-art text mining systems with potential applications in the biocuration domain.']
        self.assertEqual(nlptools.clause_tokenize(sentence), wanted)

    def test_clause_tokenize_intergration(self):
        self.assertEqual(''.join(nlptools.clause_tokenize(self.sentences[1])), self.sentences[1])

    def test_word_tokenzie(self):
        sentence = 'A 2.1 cm tumor (right tongue) noted on 2013-11-11.'
        wanted = ['A', ' ', '2.1', ' ', 'cm', ' ', 'tumor', ' ', '(', 'right', ' ', 'tongue', ')', ' ', 'noted', ' ', 'on', ' ', '2013-11-11', '.']
        self.assertEqual(list(nlptools.word_tokenize(sentence)), wanted)

    def test_word_tokenzie2(self):
        sentence = '-999 1,234,000 3.1415'
        wanted = ['-999', ' ', '1,234,000', ' ', '3.1415']
        self.assertEqual(list(nlptools.word_tokenize(sentence)), wanted)

    def test_word_tokenize_intergration(self):
        for sent in self.sentences:
          self.assertEqual(''.join(list(nlptools.word_tokenize(sent))), sent)

    def test_slim_stem(self):
        word2target = [('magic', 'mag'),
                       ('automatic', 'automa'),
                       ('life', 'lif'),
                       ('active', 'act'),
                       ('hiking', 'hik'),
                       ('medical', 'med'),
                       ('national', 'natio'),
                       ('animal', 'anim'),
                       ('Parkinsonism', 'Parkinson'),
                       ('mission', 'miss'),
                       ('medication', 'medic'),
                       ('radar', 'rad'),
                       ('dialysis', 'dialy'),
                       ('status', 'stat'),
                       ('measurement', 'measure'),
                       ('signalling', 'signal')]
        for word, target in word2target:
            self.assertEqual(nlptools.slim_stem(word), target)

    def test_powerset(self):
        wanted = [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
        self.assertEqual(list(nlptools.powerset([1,2,3])), wanted)

    def test_ngram(self):
        tokens = 'hello world kitty'.split(' ')

        self.assertEqual(list(nlptools.ngram(2, tokens)), [['hello', 'world'], ['world', 'kitty']])
        self.assertEqual(list(nlptools.ngram(3, tokens)), [tokens])
        self.assertEqual(list(nlptools.ngram(4, tokens)), [])

    def test_power_ngram(self):
        tokens = 'hello world kitty'.split(' ')

        self.assertEqual(list(nlptools.power_ngram(tokens)), \
            [['hello'], ['world'], ['kitty'], ['hello', 'world'], ['world', 'kitty'], ['hello', 'world', 'kitty']])

    def test_count_start(self):
        tokenizer = lambda sentence: sentence.split(' ')
        sentence = 'The quick brown'
        tokenizer = nlptools.count_start(tokenizer)
        result = [start for token, start in tokenizer(sentence, 0)]
        wanted = [0, 4, 10]
        self.assertEqual(result, wanted)

        sentence = 'jumps over the'
        result = [start for token, start in tokenizer(sentence, 16)]
        wanted = [16, 22, 27]
        self.assertEqual(result, wanted)
