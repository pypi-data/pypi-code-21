# -*- coding: utf-8 -*-

import unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone.app.discussion.comment import Comment

from collective.stringinterp.text.interfaces import ITextExtractor 
from collective.stringinterp.text.testing import STRING_INTERP_TEXT_INTEGRATION_TESTING

class TestStringSubstitutionAdapter(unittest.TestCase):

    layer = STRING_INTERP_TEXT_INTEGRATION_TESTING
    
    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
    
    def test_simple_extraction(self):
        self.layer['portal'].invokeFactory(type_name='Document', id='document',
                                           text='Foo bar baz')
        doc = self.layer['portal'].document
        adapter = ITextExtractor(doc)
        self.assertEqual(adapter.text, 'Foo bar baz')

    def test_html_extraction(self):
        self.layer['portal'].invokeFactory(type_name='Document', id='document',
                                           text='<p>Foo <strong>bar</strong> baz</p>')
        doc = self.layer['portal'].document
        adapter = ITextExtractor(doc)
        self.assertEqual(adapter.text, 'Foo bar baz')

    def test_multiline_extraction(self):
        self.layer['portal'].invokeFactory(type_name='Document', id='document',
                                           text='<p>Foo <strong>bar</strong> baz</p>\n'
                                                '<p>Lorem Ipsum</p>')
        doc = self.layer['portal'].document
        adapter = ITextExtractor(doc)
        self.assertEqual(adapter.text, 'Foo bar baz \n Lorem Ipsum')

class TestCommentAdapter(unittest.TestCase):

    layer = STRING_INTERP_TEXT_INTEGRATION_TESTING
    
    def test_pacomment_text(self):
        comment = Comment()
        comment.text = u'Foo bar baz'
        adapter = ITextExtractor(comment)
        self.assertEqual(adapter.text, 'Foo bar baz')


class Foo(object):
    
    def __init__(self):
        self.text = ''


class TestWhateverObjectAdapter(unittest.TestCase):

    layer = STRING_INTERP_TEXT_INTEGRATION_TESTING
    
    def test_pacomment_text(self):
        obj = Foo()
        obj.text = 'Foo bar baz'
        adapter = ITextExtractor(obj)
        self.assertEqual(adapter.text, 'Foo bar baz')

    def test_invalid_text_info(self):
        obj = Foo()
        obj.text = 5
        adapter = ITextExtractor(obj)
        self.assertEqual(adapter.text, '')

    def test_invalid_object(self):
        obj = 31
        adapter = ITextExtractor(obj)
        self.assertEqual(adapter.text, '')
