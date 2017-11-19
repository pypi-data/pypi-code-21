#!/usr/bin/python
 # -*- coding: utf-8 -*-

import unittest

from pytorrentz.torrentz import *


class SearchTests(unittest.TestCase):
    def test_bad_search(self):
        with self.assertRaises(KeywordError):
            s = search('test', quality='blah')
        with self.assertRaises(KeywordError):
            s = search('test', order='blah')

    def test_basic_search(self):
        s = search('2015')
        self.assertIsInstance(s, list)
        self.assertIsInstance(s[0], Torrent)

    def test_build_magnet_uri(self):
        s = search('2016')
        self.assertIsInstance(s[0].get_magnet_uri(), str)
