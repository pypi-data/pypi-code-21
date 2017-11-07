#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: Edax.test_TemCsvFile
   :synopsis: Tests for the module :py:mod:`Edax.TemCsvFile`

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module :py:mod:`Edax.TemCsvFile`.
"""

###############################################################################
# Copyright 2009 Hendrix Demers
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
import pySpectrumFileFormat.Edax.TemCsvFile as TemCsvFile
from pySpectrumFileFormat import get_current_module_path

# Globals and constants variables.

class TestTemCsvFile(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.filepathRef = get_current_module_path(__file__, "../../test_data/TEM_Edax/OVERALL.CSV")
        if not os.path.isfile(self.filepathRef):
            raise SkipTest

        self.data = TemCsvFile.TemCsvFile(self.filepathRef)

        self.numberPoints = 1024

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the testcase is working.")
        self.assert_(True)

    def test_Constructor(self):
        self.assertEquals(self.filepathRef, self.data._filepath)

        #self.fail("Test if the testcase is working.")
        self.assert_(True)

    def test_readData(self):
        data = self.data._readData(self.filepathRef)

        channels = data[TemCsvFile.CHANNEL]
        counts = data[TemCsvFile.COUNTS]
        self.assertEquals(self.numberPoints, len(channels))
        self.assertEquals(self.numberPoints, len(counts))

        self.assertEquals(1024, channels[-1])
        self.assertEquals(775, counts[-1])

        #self.fail("Test if the testcase is working.")
        self.assert_(True)

    def test_getData(self):
        energies_eV, counts = self.data.getData()

        self.assertEquals(self.numberPoints, len(energies_eV))
        self.assertEquals(self.numberPoints, len(counts))

        self.assertEquals(10240.0, energies_eV[-1])
        self.assertEquals(775, counts[-1])

        #self.fail("Test if the testcase is working.")
        self.assert_(True)

if __name__ == '__main__':  # pragma: no cover
    import nose
    nose.runmodule()
