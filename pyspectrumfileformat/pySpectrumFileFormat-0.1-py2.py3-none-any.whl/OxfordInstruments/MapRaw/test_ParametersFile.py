#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: OxfordInstruments.MapRaw.test_ParametersFile
   :synopsis: Tests for module `OxfordInstruments.MapRaw.ParametersFile`.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for module `OxfordInstruments.MapRaw.ParametersFile`.
"""

###############################################################################
# Copyright 2012 Hendrix Demers
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
import pySpectrumFileFormat.OxfordInstruments.MapRaw.ParametersFile as ParametersFile
from pySpectrumFileFormat import get_current_module_path

# Globals and constants variables.

class TestParametersFile(unittest.TestCase):
    """
    TestCase class for the module `ParametersFile`.
    """

    def setUp(self):
        """
        Setup method.
        """

        unittest.TestCase.setUp(self)

        self.path = get_current_module_path(__file__, "../../../test_data/OxfordInstruments/MapRaw")
        if not os.path.isdir(self.path):
            raise SkipTest

    def tearDown(self):
        """
        Teardown method.
        """

        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        """
        First test to check if the testcase is working with the testing framework.
        """

        #self.fail("Test if the testcase is working.")
        self.assert_(True)

    def test_read(self):
        filename = "Map30kV.rpl"
        filepath = os.path.join(self.path, filename)

        parameters = ParametersFile.ParametersFile()
        parameters.read(filepath)

        self.assertEquals(512, parameters.width)
        self.assertEquals(384, parameters.height)
        self.assertEquals(2048, parameters.depth)
        self.assertEquals(0, parameters.offset)
        self.assertEquals(1, parameters.dataLength_B)
        self.assertEquals(ParametersFile.DATA_TYPE_UNSIGNED, parameters.dataType)
        self.assertEquals(ParametersFile.BYTE_ORDER_DONT_CARE, parameters.byteOrder)
        self.assertEquals("IMAGE \"Site of Interest 1\"", parameters.recordBy)

        filename = "Project 1.rpl"
        filepath = os.path.join(self.path, filename)

        parameters = ParametersFile.ParametersFile()
        parameters.read(filepath)

        self.assertEquals(512, parameters.width)
        self.assertEquals(384, parameters.height)
        self.assertEquals(2048, parameters.depth)
        self.assertEquals(0, parameters.offset)
        self.assertEquals(2, parameters.dataLength_B)
        self.assertEquals(ParametersFile.DATA_TYPE_SIGNED, parameters.dataType)
        self.assertEquals(ParametersFile.BYTE_ORDER_LITTLE_ENDIAN, parameters.byteOrder)
        self.assertEquals("IMAGE \"Site of Interest 1\"", parameters.recordBy)

        filename = "mapSOI_15.rpl"
        filepath = os.path.join(self.path, filename)

        parameters = ParametersFile.ParametersFile()
        parameters.read(filepath)

        self.assertEquals(512, parameters.width)
        self.assertEquals(384, parameters.height)
        self.assertEquals(2048, parameters.depth)
        self.assertEquals(0, parameters.offset)
        self.assertEquals(4, parameters.dataLength_B)
        self.assertEquals(ParametersFile.DATA_TYPE_SIGNED, parameters.dataType)
        self.assertEquals(ParametersFile.BYTE_ORDER_LITTLE_ENDIAN, parameters.byteOrder)
        self.assertEquals("IMAGE \"Site of Interest 15\"", parameters.recordBy)

        filename = "mapSOI14.rpl"
        filepath = os.path.join(self.path, filename)

        parameters = ParametersFile.ParametersFile()
        parameters.read(filepath)

        self.assertEquals(512, parameters.width)
        self.assertEquals(384, parameters.height)
        self.assertEquals(2048, parameters.depth)
        self.assertEquals(0, parameters.offset)
        self.assertEquals(4, parameters.dataLength_B)
        self.assertEquals(ParametersFile.DATA_TYPE_SIGNED, parameters.dataType)
        self.assertEquals(ParametersFile.BYTE_ORDER_LITTLE_ENDIAN, parameters.byteOrder)
        self.assertEquals("IMAGE \"Site of Interest 14\"", parameters.recordBy)

        #self.fail("Test if the testcase is working.")

if __name__ == '__main__':  # pragma: no cover
    import nose
    nose.runmodule()
