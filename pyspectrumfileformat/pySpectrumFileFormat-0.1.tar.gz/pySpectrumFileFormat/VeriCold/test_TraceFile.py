#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: VeriCold.test_TraceFile
   :synopsis: Tests for the module :py:mod:`VeriCold.TraceFile`

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module :py:mod:`VeriCold.TraceFile`.
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
import pySpectrumFileFormat.VeriCold.TraceFile as TraceFile
from pySpectrumFileFormat import get_current_module_path

# Globals and constants variables.

class TestTraceFile(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.filepath = get_current_module_path(__file__, "../../test_data/test01.trc")
        if not os.path.isfile(self.filepath):
            raise SkipTest

        self.traceFile = TraceFile.TraceFile(self.filepath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testConstructor(self):
        traceFile = TraceFile.TraceFile(self.filepath)

        self.assertTrue(os.path.isfile(traceFile.filename))

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testGetFileSize(self):
        self.assertEquals(3253456, self.traceFile.getFileSize())

        #self.traceFile.printFileTime()

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

if __name__ == '__main__':  # pragma: no cover
    import nose
    nose.runmodule()
