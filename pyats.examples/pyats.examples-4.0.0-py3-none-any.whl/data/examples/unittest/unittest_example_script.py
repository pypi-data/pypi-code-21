#!/bin/env python

import unittest
import logging

from ats.aetest import runtime
from ats.aetest.discovery import ScriptDiscovery, TestcaseDiscovery
from ats.aetest.unittest_compat.script import UnittestScriptDiscovery
from ats.aetest.unittest_compat.testcase import UnittestTestcaseDiscovery

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

runtime.discoverer.script = UnittestScriptDiscovery
runtime.discoverer.testcase = UnittestTestcaseDiscovery

class uniFest(unittest.TestCase):
    def setUp(self):
        log.info('I am doing the setUp')

    def test_one(self):
        log.info('one')

    @classmethod
    def tearDownClass(self):
        log.info('tear down class')

    def test_two(self):
        log.info('two')

    @classmethod
    def setUpClass(self):
        log.info('set up Class')

if __name__ == '__main__':
    runtime.discoverer.script = UnittestScriptDiscovery
    runtime.discoverer.testcase = UnittestTestcaseDiscovery
    unittest.main()
    runtime.discoverer.script = ScriptDiscovery
    runtime.discoverer.testcase = TestcaseDiscovery