#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pySpectrumFileFormat.OxfordInstruments.INCA.test_ReadSpectrumFullResults
   :synopsis: Tests for the module :py:mod:`pySpectrumFileFormat.OxfordInstruments.INCA.ReadSpectrumFullResults`

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module :py:mod:`pySpectrumFileFormat.OxfordInstruments.INCA.ReadSpectrumFullResults`.
"""

###############################################################################
# Copyright 2007 Hendrix Demers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import unittest
import os.path

# Third party modules.
from nose.plugins.skip import SkipTest

# Local modules.

# Project modules.
import pySpectrumFileFormat.OxfordInstruments.INCA.ReadSpectrumFullResults as ReadSpectrumFullResults
from pySpectrumFileFormat import get_current_module_path

# Globals and constants variables.

class TestReadSpectrumFullResults(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.filepath = get_current_module_path(__file__, "../../../test_data/SpectrumFullResults 10.txt")
        if not os.path.isfile(self.filepath):
            raise SkipTest

        self.results = ReadSpectrumFullResults.ReadSpectrumFullResults(self.filepath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testConstructor(self):
        results = ReadSpectrumFullResults.ReadSpectrumFullResults(self.filepath)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def test_read(self):
        self.results.read(self.filepath)

        data = self.results.data

        self.assertAlmostEquals(0.0088, data["O"][2], 4)

        self.assertAlmostEquals(0.28664, data["Zr"][2], 5)

        self.assertAlmostEquals(100.00, data["Totals"], 2)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def test_isValidFile(self):
        folderpath = get_current_module_path(__file__, "../../../test_data")

        filepath = os.path.join(folderpath, "SpectrumFullResults 10.txt")
        self.assertEquals(True, ReadSpectrumFullResults.isValidFile(filepath))

        filepath = os.path.join(folderpath, "SpectrumProcessing 10.txt")
        self.assertEquals(False, ReadSpectrumFullResults.isValidFile(filepath))

        filepath = os.path.join(folderpath, "AllSpectra.txt")
        self.assertEquals(False, ReadSpectrumFullResults.isValidFile(filepath))

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

if __name__ == '__main__':  # pragma: no cover
    import nose
    nose.runmodule()
