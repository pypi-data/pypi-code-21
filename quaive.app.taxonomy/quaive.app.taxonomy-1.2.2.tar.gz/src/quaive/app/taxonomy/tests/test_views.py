# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from quaive.app.taxonomy.setuphandlers import create_taxonomy_app
from quaive.app.taxonomy.testing import QUAIVE_APP_TAXONOMY_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


class TaxonomyViewsTestBase(TestCase):

    layer = QUAIVE_APP_TAXONOMY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        create_taxonomy_app(
            id='test-doc-browser',
            app_parameters='{"vocabulary": "testvocab"}',
        )
        self.app = getattr(self.portal.apps, 'test-doc-browser')
        self.view = api.content.get_view(
            'app-document-browser', self.app, self.request)

        # FIXME: why isn't the config working?
        self.view.vocabulary_name = 'testvocab'
        self.view.vocabulary_index = 'testvocab'

        factory = getUtility(IVocabularyFactory, self.view.vocabulary_name)
        self.view.vocabulary = factory(self.portal)
        self.doc1 = api.content.create(
            self.portal,
            'Document',
            id='one',
            testvocab='1',
            title='Unique1',
        )
        self.doc1_1 = api.content.create(
            self.portal,
            'Document',
            id='one_dot_one',
            testvocab='1.1',
            title='Unique1dot1',
        )


class TestDocumentBrowserView(TaxonomyViewsTestBase):

    def test_default_terms(self):
        self.assertEqual(self.view.terms(), self.view.vocabulary)

    def test_sub_terms(self):
        self.request['term-id'] = '1'
        self.assertEqual(
            self.view.terms(), self.view.vocabulary[self.view.current_term])

    def test_default_breadcrumb(self):
        self.assertEqual(self.view.breadcrumb, None)

    def test_first_level_breadcrumb(self):
        self.request['term-id'] = '1'
        self.assertEqual(
            self.view.breadcrumb, {
                'url': (
                    'http://nohost/plone/apps/test-doc-browser'
                ),
                'title': u'Document browser'
            }
        )

    def test_second_level_breadcrumb(self):
        self.request['term-id'] = '1.1'
        self.assertEqual(
            self.view.breadcrumb, {
                'url': (
                    'http://nohost/plone/apps/test-doc-browser?term-id=1'
                ),
                'title': '1'
            }
        )

    def test_sidebar_search_no_terms(self):
        self.request['term-id'] = '1'
        self.request['sidebar-search'] = u'Quaive®'
        self.assertEqual(self.view.terms(), [])

    def test_flattened_term_tokens(self):
        self.assertEquals(
            list(self.view.flattened_tokens()),
            ['1.1.1', '1.1', '1', '2.1', '2']
        )
        self.request['term-id'] = '1'
        self.assertEquals(list(self.view.flattened_tokens()), ['1.1.1', '1.1'])
        self.request['term-id'] = '1.1'
        self.assertEquals(list(self.view.flattened_tokens()), ['1.1.1'])

    def test_sidebar_search_text_query(self):
        self.request['term-id'] = '1'
        self.request.form['sidebar-search'] = u'Unique1dot1'
        self.assertEqual(len(self.view.items()), 1)
        self.assertEqual(self.view.items()[0]['id'], 'one_dot_one')

    def test_sidebar_search_term_query(self):
        self.request['term-id'] = '1'
        self.request.form['sidebar-search'] = u'1.1'
        self.assertEqual(len(self.view.items()), 1)
        self.assertEqual(self.view.items()[0]['id'], 'one_dot_one')


class TestTaxonomySearchTile(TaxonomyViewsTestBase):

    def setUp(self):
        super(TestTaxonomySearchTile, self).setUp()
        self.tile = getMultiAdapter(
            (self.app, self.request), name='grouped_taxonomy_search.tile')

    def test_top_level_search_results(self):
        login(self.portal, TEST_USER_NAME)
        self.request['term-id'] = '1'
        self.request['vocabulary'] = 'testvocab'
        self.assertTrue(self.tile.search_results().total_results == 1)
        result_obj = self.tile.search_results().results.next().getObject()
        self.assertEqual(result_obj, self.doc1)

    def test_second_level_search_results(self):
        login(self.portal, TEST_USER_NAME)
        self.request['term-id'] = '1.1'
        self.request['vocabulary'] = 'testvocab'
        self.assertTrue(self.tile.search_results().total_results == 1)
        result_obj = self.tile.search_results().results.next().getObject()
        self.assertEqual(result_obj, self.doc1_1)
