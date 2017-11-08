""" Doc tests
"""
import doctest
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from eea.alchemy.tests.base import EEAAlchemyFunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
            Suite('interfaces.py',
                  optionflags=OPTIONFLAGS,
                  package='eea.alchemy',
                  test_class=EEAAlchemyFunctionalTestCase),
            Suite('browser/app/tool.py',
                  optionflags=OPTIONFLAGS,
                  package='eea.alchemy',
                  test_class=EEAAlchemyFunctionalTestCase),
    ))
