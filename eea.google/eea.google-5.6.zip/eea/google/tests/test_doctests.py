""" Doc tests
"""
import unittest
from zope.testing import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite
from eea.google.tests.base import GoogleFunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
            FunctionalDocFileSuite('README.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.google',
                  test_class=GoogleFunctionalTestCase),
            FunctionalDocFileSuite('docs/api.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.google',
                  test_class=GoogleFunctionalTestCase),
            FunctionalDocFileSuite('docs/analytics.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.google',
                  test_class=GoogleFunctionalTestCase),
            FunctionalDocFileSuite('docs/tool.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.google',
                  test_class=GoogleFunctionalTestCase),
    ))
