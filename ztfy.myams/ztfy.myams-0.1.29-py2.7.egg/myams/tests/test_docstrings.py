# Copyright (c) 2008-2012 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.

"""
Generic Test case for 'ztfy.myams' doc strings
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os


current_dir = os.path.abspath(os.path.dirname(__file__))

def doc_suite(test_dir, globs=None):
    """Returns a test suite, based on doc tests strings found in /*.py"""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    package_dir = os.path.split(test_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    # filtering files on extension
    docs = [doc for doc in
            os.listdir(package_dir) if doc.endswith('.py')]
    docs = [doc for doc in docs if not doc.startswith('__')]

    for test in docs:
        fd = open(os.path.join(package_dir, test))
        content = fd.read()
        fd.close()
        if '>>> ' not in content:
            continue
        test = test.replace('.py', '')
        location = 'ztfy.myams.%s' % test
        suite.append(doctest.DocTestSuite(location, optionflags=flags,
                                          globs=globs))

    return unittest.TestSuite(suite)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
