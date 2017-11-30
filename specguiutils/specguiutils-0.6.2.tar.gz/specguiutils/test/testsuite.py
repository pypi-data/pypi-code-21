'''
Created on Aug 21, 2017

@author: hammonds
'''
import unittest
from specguiutils.test.testScanBrowser import TestScanBrowserTest
from specguiutils.test.testCounterSelectorModel import CounterSelectorTableModelTest
from specguiutils.test import testCounterSelectorView


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestScanBrowserTest())
    suite.addTest(CounterSelectorTableModelTest())
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)