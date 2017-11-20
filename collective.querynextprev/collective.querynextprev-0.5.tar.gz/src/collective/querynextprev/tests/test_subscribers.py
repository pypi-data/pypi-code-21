# -*- coding: utf-8 -*-
"""Test subscribers."""
import unittest2 as unittest

from plone import api

from collective.querynextprev.subscribers import record_query_in_session
from collective.querynextprev.testing import COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING  # noqa #pylint: disable=C0301
from collective.querynextprev import QUERY, SEARCH_URL


class DummyEvent(object):
    pass


class TestSubscribers(unittest.TestCase):

    """Test subscribers."""

    layer = COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING

    def test_record_query_in_session(self):
        """Test record_query_in_session subscriber."""
        portal = api.portal.get()
        request = portal.REQUEST
        request.SESSION = {}
        event = DummyEvent()
        event.query = {'k': 'foobar'}
        record_query_in_session(portal, event)
        self.assertIn(QUERY, request.SESSION)
        self.assertIn(SEARCH_URL, request.SESSION)
