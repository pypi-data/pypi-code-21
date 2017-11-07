#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pySpectrumFileFormat.EPMA.test_JEOL8900McGill
   :synopsis: Tests for the module :py:mod:`pySpectrumFileFormat.EPMA.JEOL8900McGill`

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Tests for the module :py:mod:`pySpectrumFileFormat.EPMA.JEOL8900McGill`.
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
import warnings

# Third party modules.
from nose.plugins.skip import SkipTest

# Local modules.

# Project modules.
import pySpectrumFileFormat.EPMA.JEOL8900McGill as JEOL8900McGill
from pySpectrumFileFormat import get_current_module_path

# Globals and constants variables.

class TestJEOL8900McGill(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter("ignore")

        unittest.TestCase.setUp(self)

        projectPath = get_current_module_path(__file__)

        self.filename = os.path.join(projectPath, "../../test_data/data0407.ful")
        if not os.path.isfile(self.filename):
            raise SkipTest

        self.linescanFile = JEOL8900McGill.JEOL8900McGill(self.filename)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testReadResultsFile(self):
        linescanFile = JEOL8900McGill.JEOL8900McGill(self.filename)

        numberLines = linescanFile.readResultsFile(self.filename)

        self.assertEquals(5276, numberLines)

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testReadMasterHeader(self):
        line = "Intensity & Wt. %      Group : Lang            Sample : Song             Page 1 \n"

        self.linescanFile.readMasterHeader(line)

        self.assertEquals(self.linescanFile.masterHeader, {})

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testReadPointData(self):
        lines = """Unknown Specimen No. 1178
 Group        : Lang            Sample  : Song
 UNK No.      : 1178            Comment : Line 255 AlMgZn-region3
 Stage        :    X=   62.9595  Y=   54.2735  Z=    9.8025
 Acc. Voltage :    15.0 (kV)    Probe Dia. : 0    Scan : Off
 Dated on Apr 11 16:22 2007
 WDS only       No. of accumulation : 1

Curr.(A) : 1.999E-08
Element Peak(mm)    Net(cps)  Bg-(cps)  Bg+(cps)   S.D.(%)   D.L.(ppm)
 1 Al    90.637        -0.3      23.6      17.0    300.00 ?     86
 2 Mg   107.784     30962.1      30.5      33.5      0.38      153
 3 Zn   133.173       242.3      13.7       7.1      4.48      507


Element  f(chi)    If/Ip     abs-el    1/s-el      r-el      c/k-el    c/k-std
 Mg      0.7796    0.0000    0.8997    1.0116     0.9959     1.1033     1.1033
 Zn      0.7657    0.0508    1.1682    0.7385     1.1311     0.9752     0.9752

Element  El. Wt%   Ox Wt%   Norm El%  Norm ox%  At prop    k-value   k-(std)
 Al       0.00      0.00      0.00      0.00     0.000   0.00000  -0.00001 ?
 Mg      96.40     96.40     95.94     95.94    98.451   0.88308   0.88308
 Zn       4.08      4.08      4.06      4.06     1.549   0.04183   0.04183
 -----------------------------------------------------------------------------
Total:  100.48    100.48    100.00    100.00   100.000




""".splitlines()

        self.linescanFile.readPointData(lines)

        spectrumID = 1178
        group = "Lang"
        sample = "Song"
        number = 1178
        comment = "Line 255 AlMgZn-region3"
        stageX = 62.9595
        stageY = 54.2735
        stageZ = 9.8025
        incidentEnergy_keV = 15.0
        probeDiameter = 0
        scanOn = False
        date = "Apr 11 16:22 2007"
        detectorType = "WDS only"
        numberAccumulation = 1

        current_A = 1.999E-08

        # Test experimental condition.
        self.assertEquals(spectrumID, self.linescanFile.points[1178].spectrumID)

        self.assertEquals(group, self.linescanFile.points[1178].group)

        self.assertEquals(sample, self.linescanFile.points[1178].sample)

        self.assertEquals(number, self.linescanFile.points[1178].number)

        self.assertEquals(comment, self.linescanFile.points[1178].comment)

        self.assertEquals(stageX, self.linescanFile.points[1178].stageX)

        self.assertEquals(stageY, self.linescanFile.points[1178].stageY)

        self.assertEquals(stageZ, self.linescanFile.points[1178].stageZ)

        self.assertEquals(incidentEnergy_keV, self.linescanFile.points[1178].incidentEnergy_keV)

        self.assertEquals(probeDiameter, self.linescanFile.points[1178].probeDiameter)

        self.assertEquals(scanOn, self.linescanFile.points[1178].scanOn)

        self.assertEquals(date, self.linescanFile.points[1178].date)

        self.assertEquals(detectorType, self.linescanFile.points[1178].detectorType)

        self.assertEquals(numberAccumulation, self.linescanFile.points[1178].numberAccumulation)

        self.assertEquals(current_A, self.linescanFile.points[1178].current_A)

        # Test intensities lines.
        self.assertEquals(300.0, self.linescanFile.points[1178].elementData['Al']['sd_%%'])

        self.assertEquals(86.0, self.linescanFile.points[1178].elementData['Al']['dl_ppm'])

        self.assertEquals(30962.1, self.linescanFile.points[1178].elementData['Mg']['net_cps'])

        self.assertEquals(3, self.linescanFile.points[1178].elementData['Zn']['id'])

        self.assertEquals(507.0, self.linescanFile.points[1178].elementData['Zn']['dl_ppm'])

        # Test correction lines.
        self.assertEquals(0.0000, self.linescanFile.points[1178].elementData['Mg']['If/Ip'])

        self.assertEquals(1.1033, self.linescanFile.points[1178].elementData['Mg']['c/k-el'])

        self.assertEquals(0.7657, self.linescanFile.points[1178].elementData['Zn']['f(chi)'])

        self.assertEquals(0.9752, self.linescanFile.points[1178].elementData['Zn']['c/k-std'])

        # Test concentration lines.
        self.assertEquals(-0.00001, self.linescanFile.points[1178].elementData['Al']['k-std'])

        self.assertEquals(98.451, self.linescanFile.points[1178].elementData['Mg']['Atomic'])

        self.assertEquals(4.08, self.linescanFile.points[1178].elementData['Zn']['El fw'])

        self.assertEquals(0.04183, self.linescanFile.points[1178].elementData['Zn']['k-value'])


        # Test total line.
        self.assertEquals(100.48, self.linescanFile.points[1178].elementData['total']['El fw'])

        self.assertEquals(100.0, self.linescanFile.points[1178].elementData['total']['Atomic'])

        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

if __name__ == '__main__':  # pragma: no cover
    import nose
    nose.runmodule()
