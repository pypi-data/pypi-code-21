# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from collective.sortedlisting.testing import COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.sortedlisting is properly installed."""

    layer = COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.sortedlisting is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.sortedlisting'))

    def test_browserlayer(self):
        """Test that ICollectiveSortedlistingLayer is registered."""
        from collective.sortedlisting.interfaces import (
            ICollectiveSortedlistingLayer)
        from plone.browserlayer import utils
        self.assertIn(
            ICollectiveSortedlistingLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_SORTEDLISTING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.sortedlisting'])

    def test_product_uninstalled(self):
        """Test if collective.sortedlisting is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.sortedlisting'))

    def test_browserlayer_removed(self):
        """Test that ICollectiveSortedlistingLayer is removed."""
        from collective.sortedlisting.interfaces import \
            ICollectiveSortedlistingLayer
        from plone.browserlayer import utils
        self.assertNotIn(
           ICollectiveSortedlistingLayer,
           utils.registered_layers())

    def test_hiddenprofiles(self):
        """ Test uninstall profile is hidden
        """
        from collective.sortedlisting.setuphandlers import HiddenProfiles
        hidden_profiles = HiddenProfiles().getNonInstallableProfiles()
        self.assertIn('collective.sortedlisting:uninstall', hidden_profiles)
