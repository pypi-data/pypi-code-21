""" Test doctests module
"""

import unittest
import doctest

from Testing import ZopeTestCase as ztc

from eea.sparql.tests import base


def test_suite():
    """ Suite
    """
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'converter/sparql2json.py', package='eea.sparql',
            test_class=base.SparqlFunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),


        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
