""" Doc tests
"""
import unittest
import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite
from eea.relations.tests.base import EEARelationsFunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    """ Suite
    """
    return unittest.TestSuite((
        FunctionalDocFileSuite('docs/graph.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/components.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/categorizations.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/faceted.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/exportimport.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/validation.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/discover.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/workflow.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
        FunctionalDocFileSuite('docs/badrelations.txt',
                               optionflags=OPTIONFLAGS,
                               package='eea.relations',
                               test_class=EEARelationsFunctionalTestCase),
    ))
