# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.querynextprev.testing import COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that collective.querynextprev is properly installed."""

    layer = COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.querynextprev is installed with portal_quickinstaller."""  # noqa
        self.assertTrue(
            self.installer.isProductInstalled('collective.querynextprev'))

    def test_browserlayer(self):
        """Test that ICollectiveQuerynextprevLayer is registered."""
        from collective.querynextprev.interfaces import ICollectiveQuerynextprevLayer  # noqa
        from plone.browserlayer import utils
        self.assertIn(ICollectiveQuerynextprevLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.querynextprev'])

    def test_product_uninstalled(self):
        """Test if collective.querynextprev is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('collective.querynextprev'))
