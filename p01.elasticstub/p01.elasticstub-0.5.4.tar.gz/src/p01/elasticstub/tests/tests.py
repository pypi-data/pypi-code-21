###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################

__docformat__ = "reStructuredText"

import doctest
import unittest

import p01.elasticstub.testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
            setUp=p01.elasticstub.testing.doctestSetUp,
            tearDown=p01.elasticstub.testing.doctestTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            encoding='utf-8'),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
