# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from quaive.resources.ploneintranet.testing import QUAIVE_RESOURCES_PLONEINTRANET_INTEGRATION_TESTING  # noqa
from zope.component import getUtility

import unittest


class TestSetup(unittest.TestCase):
    """Test that quaive.resources.ploneintranet is properly installed."""

    layer = QUAIVE_RESOURCES_PLONEINTRANET_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if quaive.resources.ploneintranet is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('quaive.resources.ploneintranet')
        )

    def test_browserlayer(self):
        """Test that IThemeSpecific is registered."""
        from quaive.resources.ploneintranet.interfaces import (
            IThemeSpecific
        )
        from plone.browserlayer import utils
        self.assertIn(IThemeSpecific, utils.registered_layers())

    def test_theme_installed(self):
        from plone.app.theming.utils import getCurrentTheme
        self.assertEqual('ploneintranet.theme', getCurrentTheme())

    def test_resources(self):
        resources = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertIn('ploneintranet', resources)
        bundles = getUtility(IRegistry).collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles")
        self.assertIn('ploneintranet', bundles)


class TestUninstall(unittest.TestCase):

    layer = QUAIVE_RESOURCES_PLONEINTRANET_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['quaive.resources.ploneintranet'])

    def test_product_uninstalled(self):
        """Test if quaive.resources.ploneintranet is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('quaive.resources.ploneintranet')
        )

    def test_browserlayer_removed(self):
        """Test that IThemeSpecific is removed."""
        from quaive.resources.ploneintranet.interfaces import IThemeSpecific
        from plone.browserlayer import utils
        self.assertNotIn(IThemeSpecific, utils.registered_layers())

    def test_theme_reset(self):
        from plone.app.theming.utils import getCurrentTheme
        self.assertEqual('barceloneta', getCurrentTheme())

    def test_resources_removed(self):
        resources = getUtility(IRegistry).collectionOfInterface(
            IResourceRegistry, prefix="plone.resources")
        self.assertNotIn('ploneintranet', resources)
        bundles = getUtility(IRegistry).collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles")
        self.assertNotIn('ploneintranet', bundles)
