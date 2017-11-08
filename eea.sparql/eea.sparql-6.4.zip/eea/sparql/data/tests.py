""" Doc tests
"""
import doctest
import logging
import unittest

from plone.testing import layered

from eea.sparql.tests.base import FUNCTIONAL_TESTING

try:
    from eea.app.visualization import interfaces as VISUALIZATION
except ImportError, err:
    VISUALIZATION = None
    logger = logging.getLogger('eea.sparql')
    logger.debug(err)

logger = logging.getLogger('eea.sparql')

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    """ Suite
    """
    suite = unittest.TestSuite()
    if VISUALIZATION:
        suite.addTests([
            layered(
                doctest.DocFileSuite(
                    'data/source.py',
                    optionflags=OPTIONFLAGS,
                    package='eea.sparql'),
                layer=FUNCTIONAL_TESTING),
        ])
    return suite
