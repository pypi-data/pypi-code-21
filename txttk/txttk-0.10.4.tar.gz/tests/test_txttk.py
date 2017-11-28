#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

"""
test_txttk
----------------------------------

Tests for `txttk` module.
"""

import unittest

class TestTxttk(unittest.TestCase):

    def test_import_corpus(self):
        from txttk import Corpus

    def test_import_feature(self):
        from txttk import orthographic

    def test_import_nlptools(self):
        from txttk import powerset

    def test_import_retools(self):
        from txttk import condense
