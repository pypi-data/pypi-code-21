# -*- coding: utf-8 -*-

import unittest

from zope.interface import implements
from zope.interface import Interface
from zope.component import getAdapter

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone.app.discussion.comment import Comment

from plone.stringinterp.interfaces import IStringSubstitution 
from collective.stringinterp.text.testing import STRING_INTERP_TEXT_INTEGRATION_TESTING


class Foo(object):
    implements(Interface)
    def __init__(self):
        self.text = ''

class TestStringInterp(unittest.TestCase):

    layer = STRING_INTERP_TEXT_INTEGRATION_TESTING

    def test_text_substitution(self):
        d = Foo()
        d.text = 'foo\nbaz'
        adapter = getAdapter(d, name=u'text', context=self.layer['portal'])
        self.assertEqual(adapter.safe_call(), 'foo\nbaz')

    def test_text_substitution_whistespaces(self):
        d = Foo()
        d.text = 'foo\n baz'
        adapter = getAdapter(d, name=u'text', context=self.layer['portal'])
        self.assertEqual(adapter.safe_call(), 'foo\nbaz')

    def test_indented_text_substitution(self):
        d = Foo()
        d.text = 'foo\nbaz'
        adapter = getAdapter(d, name=u'indented_text', context=self.layer['portal'])
        self.assertEqual(adapter.safe_call(), '\tfoo\n\tbaz')

    def test_indented_text_substitution_whitespaces(self):
        d = Foo()
        d.text = '  foo\n baz '
        adapter = getAdapter(d, name=u'indented_text', context=self.layer['portal'])
        self.assertEqual(adapter.safe_call(), '\tfoo\n\tbaz')
