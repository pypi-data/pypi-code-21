#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pySpectrumFileFormat.OxfordInstruments.INCA.test_ReadAllSpectrumResults
   :synopsis: Tests for the module :py:mod:`pySpectrumFileFormat.OxfordInstruments.INCA.ReadAllSpectrumResults`

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module :py:mod:`pySpectrumFileFormat.OxfordInstruments.INCA.ReadAllSpectrumResults`.
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
import pySpectrumFileFormat.OxfordInstruments.INCA.ReadAllSpectrumResults as ReadAllSpectrumResults
from pySpectrumFileFormat import get_current_module_path

# Globals and constants variables.

class TestReadAllSpectrumResults(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.filepath = get_current_module_path(__file__, "../../../test_data/AllSpectra.txt")
        if not os.path.isfile(self.filepath):
            raise SkipTest

        self.results = ReadAllSpectrumResults.ReadAllSpectrumResults(self.filepath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testConstructor(self):
        results = ReadAllSpectrumResults.ReadAllSpectrumResults(self.filepath)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def test_read(self):
        self.results.read(self.filepath)

        data = self.results.data

        self.assertAlmostEquals(0.853, data["Spectrum 5"][1], 3)

        self.assertAlmostEquals(100.000, data["Spectrum 5"][-1], 3)

        self.assertAlmostEquals(0.520, data["Minimum"][1], 3)

        self.assertAlmostEquals(15.128, data["Minimum"][-1], 3)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def test_extractMinData(self):
        #line = "Min.    19.086    0.520    4.404    0.598    40.670    14.894    15.128     "
        line = "Min.\t19.086\t0.520\t4.404\t0.598\t40.670\t14.894\t15.128\t"
        results = self.results._extractLineData(line)

        self.assertAlmostEquals(0.520, results[1], 3)

        self.assertAlmostEquals(15.128, results[-1], 3)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def test_isValidFile(self):
        folderpath = get_current_module_path(__file__, "../../../test_data")

        filepath = os.path.join(folderpath, "SpectrumFullResults 10.txt")
        self.assertEquals(False, ReadAllSpectrumResults.isValidFile(filepath))

        filepath = os.path.join(folderpath, "SpectrumProcessing 10.txt")
        self.assertEquals(False, ReadAllSpectrumResults.isValidFile(filepath))

        filepath = os.path.join(folderpath, "AllSpectra.txt")
        self.assertEquals(True, ReadAllSpectrumResults.isValidFile(filepath))

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

if __name__ == '__main__':  # pragma: no cover
    import nose
    nose.runmodule()
