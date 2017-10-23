#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# Add test directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import coverage

    coverage.process_startup()
except ImportError:
    pass


def generatte_test_suit():
    '''
        Add testcases into test suite
    :return:
    '''
    current_pwd = os.path.dirname(__file__)
    testcase_directory = current_pwd + os.sep + 'testcase'
    return unittest.defaultTestLoader.discover(testcase_directory)


if __name__ == '__main__':
    suite = generatte_test_suit()
    unittest.TextTestRunner().run(suite)
