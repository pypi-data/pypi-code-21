# -*- coding: utf-8 -*-
"""Test utilities."""
import unittest2 as unittest

from plone import api

from collective.querynextprev.utils import (
    expire_session_data, first_common_item, get_next_items, get_previous_items, clean_query)
from collective.querynextprev.testing import COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING  # noqa #pylint: disable=C0301


class TestUtils(unittest.TestCase):

    """Test NextPrevNavigationViewlet."""

    layer = COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING

    def setUp(self):
        portal = api.portal.get()
        self.request = portal.REQUEST

    def tearDown(self):
        if hasattr(self.request, 'SESSION'):
            del self.request.SESSION

    def test_expire_session_data(self):
        """Test expire_session_data function."""
        request = self.request
        request.SESSION = {}
        expire_session_data(request)
        self.assertEqual(request.SESSION, {})

        request.SESSION = {
            'foo': 'bar',
            'querynextprev.foo': 'bar',
            'querynextprev.bar': 'foo',
        }
        expire_session_data(request)
        self.assertEqual(request.SESSION, {'foo': 'bar'})

    def test_first_common_item(self):
        """Test first common item util."""
        l1 = [4, 5, 6, 7]
        l2 = [1, 2, 6, 7]

        self.assertEqual(
            first_common_item(l1, l2),
            6)

        l1 = [1, 2, 4, 5, 6, 7]
        l2 = [1, 2, 6, 7]
        self.assertEqual(
            first_common_item(l1, l2),
            1)

        l1 = [4, 5, 6, 7]
        l2 = [1, 2]
        self.assertIsNone(
            first_common_item(l1, l2))

        l1 = [1]
        l2 = [1]
        self.assertEqual(
            first_common_item(l1, l2),
            1)

    def test_get_next_items(self):
        """Test get_next_items function."""
        l = range(40)
        index = 19
        self.assertEqual(
            get_next_items(l, index),
            range(20, 30)
        )

        index = 35
        self.assertEqual(
            get_next_items(l, index),
            range(36, 40)
        )

        self.assertEqual(
            get_next_items(l, index, include_index=True),
            range(35, 40)
        )

    def test_get_previous_items(self):
        """Test get_previous_items function."""
        l = range(40)
        index = 21
        self.assertEqual(
            get_previous_items(l, index),
            range(11, 21)
        )

        index = 5
        self.assertEqual(
            get_previous_items(l, index),
            range(5)
        )

        self.assertEqual(
            get_previous_items(l, index, include_index=True),
            range(6)
        )

    def test_clean_query(self):
        query = {'sort_order': 'descending', 'Language': ['fr', ''], 'sort_on': 'created',
                 'facet.field': ['', u'review_state', u'treating_groups', u'assigned_user', u'recipient_groups',
                                 u'mail_type'],
                 'b_size': 24, 'b_start': 0, 'portal_type': {'query': ['dmsincomingmail']}}
        self.assertDictEqual(clean_query(query), {'sort_order': 'descending', 'Language': ['fr', ''],
                                                  'sort_on': 'created', 'portal_type': {'query': ['dmsincomingmail']}})
