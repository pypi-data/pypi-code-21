# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

"""
Generic Test case for 'ztfy.myams' doctest
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os


current_dir = os.path.dirname(__file__)

def doc_suite(test_dir, setUp=None, tearDown=None, globs=None):
    """Returns a test suite, based on doctests found in /doctests."""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    package_dir = os.path.split(test_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    doctest_dir = os.path.join(package_dir, 'doctests')

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

    for test in docs:
        suite.append(doctest.DocFileSuite(test, optionflags=flags,
                                          globs=globs, setUp=setUp,
                                          tearDown=tearDown,
                                          module_relative=False))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
