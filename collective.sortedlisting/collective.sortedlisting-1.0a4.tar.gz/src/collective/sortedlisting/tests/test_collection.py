# -*- coding: utf-8 -*-
from collections import OrderedDict
from collective.sortedlisting.behavior import ISortableCollectionBehavior
from collective.sortedlisting.behavior import SortableCollectionBehavior
from collective.sortedlisting.browser.collection import SortableCollectionView
from collective.sortedlisting.testing import COLLECTIVE_SORTEDLISTING_FUNCTIONAL_TESTING   # noqa
from collective.sortedlisting.testing import COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING  # noqa
from collective.sortedlisting.widget import SortableQueryStringWidget
from plone import api
from plone.app.contenttypes.tests.test_collection import PloneAppCollectionClassTest       # noqa
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing import z2

import unittest


class PloneCollectionTest(PloneAppCollectionClassTest):

    layer = COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.collection = api.content.create(
            self.portal, 'SortableCollection', id='collection')

    def test_bbb_selectedViewFields(self):
        pass


query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.contains',
    'v': 'SC Test',
}]


class SortedCollectionTest(unittest.TestCase):

    layer = COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.add_content()

    def add_content(self):
        self.sc = api.content.create(
            self.portal, 'SortableCollection', id='sc')
        self.sc.query = query
        self.sc.reindexObject()

        self.uids = OrderedDict()

        testdoc = api.content.create(
            self.portal, 'Document', title='SC Test Doc')
        testdoc.reindexObject()
        self.uids[testdoc.getId()] = api.content.get_uuid(testdoc)

        testnewsitem = api.content.create(
            self.portal, 'News Item', title='SC Test News Item')
        testnewsitem.reindexObject()
        self.uids[testnewsitem.getId()] = api.content.get_uuid(testnewsitem)

        testevent = api.content.create(
            self.portal, 'Event', title='SC Test Event')
        testevent.reindexObject()
        self.uids[testevent.getId()] = api.content.get_uuid(testevent)

    def test_behavior_batch(self):
        results = ISortableCollectionBehavior(self.sc).results(batch=True)
        self.assertEqual(len(results), 3)

    def test_behavior_sorting(self):
        behavior = ISortableCollectionBehavior(self.sc)
        behavior.sorting = self.uids.values()
        self.assertEqual(
            [item.uuid() for item in behavior.results(batch=False)],
            self.uids.values()
        )
        self.assertEqual(
            behavior.results(batch=False),
            self.sc.results(batch=False)
        )

    def test_view_behavior(self):
        view = SortableCollectionView(self.sc, self.layer['request'])
        self.assertIsInstance(
            view.collection_behavior, SortableCollectionBehavior)

    def test_widget(self):
        widget = SortableQueryStringWidget(self.layer['request'])
        self.assertEqual(widget._base_args(),
            {
                'pattern': 'sortablequerystring',
                'value': u'',
                'name': None,
                'pattern_options':
                {
                    'previewCountURL': 'http://nohost/plone/@@querybuildernumberofresults',    # noqa
                    'previewURL': 'http://nohost/plone/@@sortable_querybuilder_html_results',  # noqa
                    'indexOptionsUrl': 'http://nohost/plone/@@qsOptions'
                }
            }
        )


class SortedCollectionFunctionalTest(unittest.TestCase):

    layer = COLLECTIVE_SORTEDLISTING_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_add_collection(self):
        browser = z2.Browser(self.layer['app'])
        browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        portal_url = self.portal.absolute_url()
        browser.open(portal_url)
        browser.getLink(
            url='{0}/++add++SortableCollection'.format(portal_url)).click()
        widget = 'form.widgets.IDublinCore.title'
        browser.getControl(name=widget).value = 'My sortable collection'
        widget = 'form.widgets.IDublinCore.description'
        browser.getControl(name=widget).value = 'This is sortable.'
        widget = 'form.widgets.IRichText.text'
        browser.getControl(name=widget).value = 'Lorem Ipsum'
        widget = 'form.widgets.IShortName.id'
        browser.getControl(name=widget).value = 'my-special-collection'
        browser.getControl('Save').click()
        self.assertTrue(browser.url.endswith('my-special-collection/view'))
        self.assertIn('My sortable collection', browser.contents)
        self.assertIn('This is sortable.', browser.contents)
        self.assertIn('Lorem Ipsum', browser.contents)

# EOF
