# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from quaive.app.taxonomy.testing import QUAIVE_APP_TAXONOMY_INTEGRATION_TESTING
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that quaive.app.taxonomy is properly installed."""

    layer = QUAIVE_APP_TAXONOMY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if quaive.app.taxonomy is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'quaive.app.taxonomy'))

    def test_browserlayer(self):
        """Test that IQuaiveAppTaxonomyLayer is registered."""
        from quaive.app.taxonomy.interfaces import (
            IQuaiveAppTaxonomyLayer)
        from plone.browserlayer import utils
        self.assertIn(IQuaiveAppTaxonomyLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = QUAIVE_APP_TAXONOMY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['quaive.app.taxonomy'])

    def test_product_uninstalled(self):
        """Test if quaive.app.taxonomy is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'quaive.app.taxonomy'))

    def test_browserlayer_removed(self):
        """Test that IQuaiveAppTaxonomyLayer is removed."""
        from quaive.app.taxonomy.interfaces import IQuaiveAppTaxonomyLayer
        from plone.browserlayer import utils
        self.assertNotIn(IQuaiveAppTaxonomyLayer, utils.registered_layers())
