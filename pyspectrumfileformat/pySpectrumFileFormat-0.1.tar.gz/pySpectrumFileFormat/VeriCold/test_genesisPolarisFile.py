#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: ${module}
   :synopsis: Tests for the module :py:mod:`${moduleName}`

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module :py:mod:`${moduleName}`.
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
import pySpectrumFileFormat.VeriCold.genesisPolarisFile as genesisPolarisFile
from pySpectrumFileFormat import get_current_module_path

# Globals and constants variables.

class TestgenesisPolarisFile(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.filepath = get_current_module_path(__file__, "../../test_data/k3670_30keV_OFeCalibration.csp")
        if not os.path.isfile(self.filepath):
            raise SkipTest

        self.gpFile = genesisPolarisFile.GenesisPolarisFile()

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testConstructor(self):
        gpFile = genesisPolarisFile.GenesisPolarisFile()

        self.assertEquals(False, gpFile.isFileRead)

        gpFile = genesisPolarisFile.GenesisPolarisFile(self.filepath)

        self.assertEquals(True, gpFile.isFileRead)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def test_readFile(self):
        self.assertEquals(False, self.gpFile.isFileRead)

        self.gpFile.readFile(self.filepath)

        self.assertEquals(True, self.gpFile.isFileRead)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def test_readHeader(self):
        header = self.gpFile.readHeader(self.filepath)

        self.assertEquals(1001, header["version"])

        self.assertEquals(3072, header["pixOffset"])

        self.assertEquals(0, header["pixSize"])

        self.assertEquals(3072, header["dataOffset"])

        self.assertEquals(19724, header["dataSize"])

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

if __name__ == '__main__':  # pragma: no cover
    import nose
    nose.runmodule()
