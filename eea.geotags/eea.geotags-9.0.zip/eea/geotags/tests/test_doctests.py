""" Doc tests
"""
import unittest
from zope.testing import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from eea.geotags.tests.base import EEAGeotagsFunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
            Suite('README.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.geotags',
                  test_class=EEAGeotagsFunctionalTestCase),
            Suite('docs/vocabulary.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.geotags',
                  test_class=EEAGeotagsFunctionalTestCase),
            Suite('docs/storage.txt',
                  optionflags=OPTIONFLAGS,
                  package='eea.geotags',
                  test_class=EEAGeotagsFunctionalTestCase),
    ))
