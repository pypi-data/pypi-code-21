# -*- coding: utf-8 -*-
from collective.sortedlisting.interfaces import ISortableCollection
from collective.sortedlisting.testing import COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class SortableCollectionIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='SortableCollection')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='SortableCollection')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(ISortableCollection.providedBy(obj))

    def test_adding(self):
        obj = api.content.create(
            container=self.portal,
            type='SortableCollection',
            id='SortableCollection',
        )
        self.assertTrue(ISortableCollection.providedBy(obj))
