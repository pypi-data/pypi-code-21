"""
Authentication testcases

Copyright (C) 2017 ERT Inc.
"""
__author__ = "Brandon J. Van Vaerenbergh <brandon.vanvaerenbergh@noaa.gov>"

import doctest

from . import (
    metadata
    ,sso
)

def load_tests(loader, tests, ignore):
    """
    integrate Doctests with unittest test descovery API

    per: https://docs.python.org/3/library/doctest.html#unittest-api
    """
    tests.addTests(doctest.DocTestSuite(metadata))
    tests.addTests(doctest.DocTestSuite(sso))
    return tests
