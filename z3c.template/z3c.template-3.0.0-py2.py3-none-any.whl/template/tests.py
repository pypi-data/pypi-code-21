##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests
"""
import doctest
import itertools
import re
import unittest

from zope.configuration import xmlconfig
from zope.component import testing
from zope.testing import renormalizing

import z3c.pt
import z3c.ptcompat
import z3c.template.template

checker = renormalizing.RENormalizing([
    # Python 3 adds module name to exceptions;
    # The output of this one is too complex for IGNORE_EXCEPTION_MODULE_IN_PYTHON2
    (re.compile('zope.configuration.xmlconfig.ZopeXMLConfigurationError'),
     'ZopeXMLConfigurationError'),
])


def setUp(test):
    testing.setUp(test)
    # Traversal Setup
    from zope.traversing.testing import setUp
    setUp()
    test.globs['root'] = object()

def tearDown(test):
    testing.tearDown(test)

def setUpZPT(suite):
    setUp(suite)

def setUpZ3CPT(suite):
    setUp(suite)
    xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
    xmlconfig.XMLConfig('configure.zcml', z3c.ptcompat)()

    # We have to cook this template explicitly, because it's a module
    # global.
    z3c.template.template.Macro.wrapper._cook()

class TestMacro(unittest.TestCase):

    def test_call_sets_content_type(self):

        class Response(object):
            def __init__(self):
                self.headers = {}
                self.getHeader = self.headers.get
            def setHeader(self, k, v):
                self.headers[k] = v

        class Request(object):
            def __init__(self):
                self.response = Response()

        class Template(object):
            def __init__(self):
                self.macros = {}

        template = Template()
        template.macros['name'] = None
        request = Request()
        macro = z3c.template.template.Macro(template, 'name', None,
                                            request, 'text/html')
        macro.wrapper = lambda **kwargs: None

        macro()
        self.assertEqual('text/html', request.response.getHeader("Content-Type"))

class TestBoundViewTemplate(unittest.TestCase):

    def test_call_no__self__uses_first_arg(self):
        def im_func(*args):
            return args
        bound = z3c.template.template.BoundViewTemplate(im_func, None)

        im_self = 1
        args = (2, 3)
        result = bound(im_self, *args)
        self.assertEqual(result, (1, 2, 3))

    def test_cant_setattr(self):
        bound = z3c.template.template.BoundViewTemplate(None, None)
        with self.assertRaisesRegexp(AttributeError,
                                     "Can't set attribute"):
            setattr(bound, 'im_func', 42)

    def test_repr(self):
        bound = z3c.template.template.BoundViewTemplate(None, 'im_self')
        self.assertEqual("<BoundViewTemplate of 'im_self'>",
                         repr(bound))

    def test_attributes(self):
        func = object()
        bound = z3c.template.template.BoundViewTemplate(func, self)
        self.assertIs(self, bound.im_self)
        self.assertIs(self, bound.__self__)
        self.assertIs(func, bound.im_func)
        self.assertIs(func, bound.__func__)


def test_suite():
    setups = (setUpZPT, setUpZ3CPT)
    doctests = ((
        doctest.DocFileSuite(
            'README.rst',
            setUp=setUp, tearDown=tearDown,
            optionflags=(doctest.NORMALIZE_WHITESPACE
                         | doctest.ELLIPSIS
                         | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2),
            checker=checker,
        ),
        doctest.DocFileSuite(
            'zcml.rst',
            setUp=setUp, tearDown=tearDown,
            optionflags=(doctest.NORMALIZE_WHITESPACE
                         | doctest.ELLIPSIS
                         | renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2),
            checker=checker,
        ),
    ) for setUp in setups)
    doctests = list(itertools.chain(*doctests))

    suite = unittest.defaultTestLoader.loadTestsFromName(__name__)
    suite.addTests(doctests)

    return suite
