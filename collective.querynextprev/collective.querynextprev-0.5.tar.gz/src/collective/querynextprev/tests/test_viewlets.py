# -*- coding: utf-8 -*-
import json
import unittest2 as unittest

from plone import api
from plone.app.testing import login, setRoles, TEST_USER_ID, TEST_USER_NAME

from collective.querynextprev import QUERY, SEARCH_URL, PREVIOUS_UIDS, NEXT_UIDS  # noqa #pylint: disable=C0301
from collective.querynextprev.browser.viewlets import NextPrevNavigationViewlet
from collective.querynextprev.tests import query, DummyView
from collective.querynextprev.testing import COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING  # noqa #pylint: disable=C0301


class TestNextPrevNavigationViewlet(unittest.TestCase):

    """Test NextPrevNavigationViewlet."""

    layer = COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING

    def setUp(self):
        portal = api.portal.get()
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        self.doc = api.content.create(
            id='mydoc', type='Document', container=portal)
        self.view = DummyView()
        portal.REQUEST.SESSION = {}
        self.portal = portal

    def test_no_query_set(self):
        portal = self.portal
        request = portal.REQUEST
        viewlet = NextPrevNavigationViewlet(self.doc, request, self.view)
        viewlet.update()
        session = request.SESSION
        for key in [QUERY, SEARCH_URL, PREVIOUS_UIDS, NEXT_UIDS]:
            self.assertNotIn(key, session)

        self.assertFalse(viewlet.is_navigable)

    def test_alone(self):
        portal = self.portal
        request = portal.REQUEST
        session = request.SESSION
        session[QUERY] = query
        viewlet = NextPrevNavigationViewlet(self.doc, request, self.view)
        viewlet.update()
        self.assertNotIn(QUERY, session)
        self.assertNotIn(PREVIOUS_UIDS, session)
        self.assertNotIn(NEXT_UIDS, session)
        self.assertFalse(viewlet.is_navigable)

    def test_maxresults(self):
        portal = self.portal
        request = portal.REQUEST
        session = request.SESSION
        api.content.create(id='mydoc2', type='Document', container=portal)
        session[QUERY] = query
        viewlet = NextPrevNavigationViewlet(self.doc, request, self.view)
        viewlet.update()
        self.assertIn(QUERY, session)
        self.assertIn(PREVIOUS_UIDS, session)
        self.assertIn(NEXT_UIDS, session)
        self.assertTrue(viewlet.is_navigable)
        # we set maxresults to 1
        api.portal.set_registry_record(name='collective.querynextprev.maxresults', value=1)
        self.assertIn(QUERY, session)
        viewlet.update()
        self.assertNotIn(QUERY, session)
        self.assertNotIn(PREVIOUS_UIDS, session)
        self.assertNotIn(NEXT_UIDS, session)
        self.assertFalse(viewlet.is_navigable)

    def test_one_after(self):
        """Test when there is a next item and no previous item."""
        portal = self.portal
        request = portal.REQUEST
        session = request.SESSION
        session[QUERY] = query
        doc1 = self.doc
        doc2 = api.content.create(
            id='mydoc2', type='Document', container=portal)
        viewlet = NextPrevNavigationViewlet(doc1, request, self.view)
        viewlet.update()
        self.assertEqual(session[QUERY], query)
        previous_uids = json.loads(session[PREVIOUS_UIDS])
        next_uids = json.loads(session[NEXT_UIDS])
        self.assertNotIn(doc1.UID(), previous_uids)
        self.assertNotIn(doc1.UID(), next_uids)
        self.assertNotIn(doc2.UID(), previous_uids)
        self.assertIn(doc2.UID(), next_uids)
        self.assertTrue(viewlet.is_navigable)

    def test_one_before(self):
        """Test when there is a previous item and no next item."""
        portal = self.portal
        request = portal.REQUEST
        session = request.SESSION
        session[QUERY] = query
        doc1 = self.doc
        doc2 = api.content.create(
            id='mydoc2', type='Document', container=portal)
        viewlet = NextPrevNavigationViewlet(doc2, request, self.view)
        viewlet.update()
        self.assertEqual(session[QUERY], query)
        previous_uids = json.loads(session[PREVIOUS_UIDS])
        next_uids = json.loads(session[NEXT_UIDS])
        self.assertIn(doc1.UID(), previous_uids)
        self.assertNotIn(doc1.UID(), next_uids)
        self.assertNotIn(doc2.UID(), previous_uids)
        self.assertNotIn(doc2.UID(), next_uids)
        self.assertTrue(viewlet.is_navigable)

    def test_window(self):
        """Test that 10 items before and 10 items after are kept in session."""
        portal = self.portal
        request = portal.REQUEST
        session = request.SESSION
        session[QUERY] = query
        for x in range(100):
            name = "mydoc-{}".format(x)
            api.content.create(id=name, type='Document', container=portal)

        viewlet = NextPrevNavigationViewlet(self.doc, request, self.view)
        viewlet.update()
        self.assertEqual(session[QUERY], query)
        previous_uids = json.loads(session[PREVIOUS_UIDS])
        next_uids = json.loads(session[NEXT_UIDS])
        self.assertEqual(len(previous_uids), 0)
        self.assertEqual(len(next_uids), 10)
        next_ = [api.content.get(UID=uid).getId() for uid in next_uids]
        self.assertEqual(
            next_,
            ['mydoc-0', 'mydoc-1', 'mydoc-2', 'mydoc-3', 'mydoc-4',
             'mydoc-5', 'mydoc-6', 'mydoc-7', 'mydoc-8', 'mydoc-9']
            )
        self.assertTrue(viewlet.is_navigable)

        doc = portal['mydoc-50']
        viewlet = NextPrevNavigationViewlet(doc, request, self.view)
        viewlet.update()
        self.assertEqual(session[QUERY], query)
        previous_uids = json.loads(session[PREVIOUS_UIDS])
        next_uids = json.loads(session[NEXT_UIDS])
        self.assertEqual(len(previous_uids), 10)
        self.assertEqual(len(next_uids), 10)
        self.assertTrue(viewlet.is_navigable)

        previous = [api.content.get(UID=uid).getId() for uid in previous_uids]
        self.assertEqual(
            previous,
            ['mydoc-49', 'mydoc-48', 'mydoc-47', 'mydoc-46', 'mydoc-45',
             'mydoc-44', 'mydoc-43', 'mydoc-42', 'mydoc-41', 'mydoc-40']
            )

        next_ = [api.content.get(UID=uid).getId() for uid in next_uids]
        self.assertEqual(
            next_,
            ['mydoc-51', 'mydoc-52', 'mydoc-53', 'mydoc-54', 'mydoc-55',
             'mydoc-56', 'mydoc-57', 'mydoc-58', 'mydoc-59', 'mydoc-60']
            )

    def test_context_not_in_results(self):
        """Test the case in which context is not in the results."""
        portal = self.portal
        request = portal.REQUEST
        query = json.dumps({
            'portal_type': 'Document',
            'sort_on': 'sortable_title',
            'SearchableText': 'Great title'
            })
        session = request.SESSION
        session[QUERY] = query
        docs = []
        for x in range(10):
            name = "mydoc-{}".format(x)
            doc = api.content.create(
                id=name, title="Great title",
                type='Document', container=portal)
            docs.append(doc)

        old_previous_uids = list(reversed([doc.UID() for doc in docs[:5]]))  # noqa #pylint: disable=C0301
        session[PREVIOUS_UIDS] = json.dumps(old_previous_uids)
        old_next_uids = [doc.UID() for doc in docs[8:]]
        session[NEXT_UIDS] = json.dumps(old_next_uids)
        viewlet = NextPrevNavigationViewlet(self.doc, request, self.view)
        viewlet.update()
        self.assertEqual(session[QUERY], query)
        self.assertTrue(viewlet.is_navigable)
        self.assertEqual(
            json.loads(session[PREVIOUS_UIDS]), old_previous_uids)
        self.assertEqual(
            json.loads(session[NEXT_UIDS]), old_next_uids)
        self.assertEqual(viewlet.previous_uids, old_previous_uids)
        self.assertEqual(viewlet.next_uids, old_next_uids)
