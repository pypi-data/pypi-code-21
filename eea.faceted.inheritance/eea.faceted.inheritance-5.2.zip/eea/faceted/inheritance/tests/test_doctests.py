""" Doc tests
"""
import unittest
import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite
from eea.faceted.inheritance.tests.base import (
    FacetedInheritanceFunctionalTestCase,
)

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
            FunctionalDocFileSuite('README.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.faceted.inheritance',
                  test_class=FacetedInheritanceFunctionalTestCase),
            FunctionalDocFileSuite('docs/browser.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.faceted.inheritance',
                  test_class=FacetedInheritanceFunctionalTestCase),
            FunctionalDocFileSuite('docs/inheritance.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.faceted.inheritance',
                  test_class=FacetedInheritanceFunctionalTestCase),
    ))
