# -*- coding: utf-8 -*-
from collective.sortedlisting.testing import COLLECTIVE_SORTEDLISTING_FUNCTIONAL_TESTING   # noqa
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser

import unittest


query = [{
    'i': 'Title',
    'o': 'plone.app.querystring.operation.string.contains',
    'v': 'SC Test',
}]


class SortedCollectionFunctionalTest(unittest.TestCase):

    layer = COLLECTIVE_SORTEDLISTING_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_sortedlisting_tile(self):
        """
        """
        browser = Browser(self.layer['app'])
        auth = 'Basic {0}:{1}'.format(TEST_USER_NAME, TEST_USER_PASSWORD)
        browser.addHeader('Authorization', auth)
        browser.open(
            self.portal.absolute_url() +
            '/@@collective.sortablequerystring.contentlisting')
        expected = '<p class="discreet">There are currently no items in this folder.</p>'  # noqa
        self.assertIn(expected, browser.contents)

    def test_added_classes(self):
        browser = Browser(self.layer['app'])
        auth = 'Basic {0}:{1}'.format(TEST_USER_NAME, TEST_USER_PASSWORD)
        browser.addHeader('Authorization', auth)
        browser.open(
            self.portal.absolute_url() +
            '/@@collective.sortablequerystring.contentlisting')
        expected = '<p class="discreet">There are currently no items in this folder.</p>'  # noqa
        self.assertIn(expected, browser.contents)

# EOF
