# coding=utf-8
from plone import api
from quaive.resources.ploneintranet.interfaces import IThemeSpecific
from quaive.resources.ploneintranet.testing import QUAIVE_RESOURCES_PLONEINTRANET_INTEGRATION_TESTING  # noqa
import unittest2 as unittest
from zope.interface import alsoProvides


class TestSetup(unittest.TestCase):
    """Test that quaive.resources.ploneintranet is properly installed."""

    layer = QUAIVE_RESOURCES_PLONEINTRANET_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request'].clone()
        alsoProvides(self.request, IThemeSpecific)

    def test_main_template_macros(self):
        """Test if main_template works good."""
        view = api.content.get_view(
            'main_template',
            self.portal,
            self.request,
        )
        self.assertListEqual(
            sorted(view.macros.names),
            ['content', 'master', 'statusmessage', 'webstats_js']
        )

    def test_main_template_call(self):
        """Test if main_template works good."""
        view = api.content.get_view(
            'main_template',
            self.portal,
            self.request,
        )
        view()
