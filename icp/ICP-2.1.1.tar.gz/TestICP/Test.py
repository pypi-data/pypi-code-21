#!/usr/bin/env python

import unittest
import TestPixelAcquisitionModel
import TestPixelAcquisitionData
import TestFontFileAvailability 

class ICPTestCase( unittest.TestCase ):
    def checkVersion(self):
        import ICP

testSuites = [unittest.makeSuite(ICPTestCase, 'test')] 

for test_type in [
            TestPixelAcquisitionModel,
            TestPixelAcquisitionData,
            TestFontFileAvailability, 
    ]:
    testSuites.append(test_type.getTestSuites('test'))


def getTestDirectory():
    try:
        return os.path.abspath(os.path.dirname(__file__))
    except:
        return '.'

import os
os.chdir(getTestDirectory())

runner = unittest.TextTestRunner()
runner.run(unittest.TestSuite(testSuites))
