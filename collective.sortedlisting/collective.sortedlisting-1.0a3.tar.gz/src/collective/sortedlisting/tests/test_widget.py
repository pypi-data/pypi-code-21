# -*- coding: utf-8 -*-
""" Tests BrowserViews of this package."""
from collective.sortedlisting.browser.querybuilder import QueryBuilder
from collective.sortedlisting.testing import COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.batching import Batch
from plone.uuid.interfaces import IUUID

import unittest


class TestView(unittest.TestCase):
    """Test the browser views of this package """

    layer = COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.query = [{
            'i': 'portal_type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Document',
        }]
        self.view = api.content.get_view(
            name='sortable_querybuilder_html_results',
            context=self.portal,
            request=self.request
        )

    def test_html_query_result_noresults(self):
        """ Test rendering of sorted html query result (with no results).
        """
        self.assertIn(
            '<strong id="search-results-number">0</strong> items matching your search terms.',  # noqa
            self.view.html_results(self.query)
        )

    def test_html_query_result_list(self):
        """ Test rendering of sorted html query result (with results).
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager', ])
        doc1 = api.content.create(self.portal, 'Document', title='A doc')
        doc1.reindexObject()
        self.assertIn(
            '<a href="http://nohost/plone/a-doc" class="state-private contenttype-document" data-uid="{0}">A doc</a>'.format(IUUID(doc1)), # noqa
            self.view.html_results(self.query)
        )

        # Test if a necessary css-class is added
        self.assertIn(
            '<ul class="searchResults sortedListing-results">',
            self.view.html_results(self.query)
        )

    def test_querybuilder_batch(self):
        """ Test querybuilder with batch
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager', ])
        sc = api.content.create(
            self.portal, 'SortableCollection', title='A sortable collection')
        qb = QueryBuilder(sc, self.layer['request'])
        results = qb(sc.query, batch=True)
        self.assertIsInstance(results, Batch)
        self.assertEqual(len(results), 0)

    def test_querybulider_default_batch(self):
        """ Test if it the results will be batched if it's not implicity given.
        """

        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

        # default batch size is 10 for querystring
        for counter in range(11):
            obj = api.content.create(self.portal, 'Document',
                                     title='A doc - {0}'.format(counter))
            obj.reindexObject()

        self.assertIn(
            '<a href="http://nohost/plone/a-doc-10" class="link-location">',
            self.view.html_results(self.query)
        )
