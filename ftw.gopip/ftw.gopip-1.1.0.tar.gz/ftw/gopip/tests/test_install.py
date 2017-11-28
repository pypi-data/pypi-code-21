from ftw.builder import Builder
from ftw.builder import create
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.gopip.testing import IS_PLONE_5_OR_GREATER
from operator import attrgetter
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
from zope.configuration import xmlconfig
import transaction


class PloneWithBuilder(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'ftw.gopip')

    def setUpPloneSite(self, portal):
        if IS_PLONE_5_OR_GREATER:
            applyProfile(portal, 'plone.app.contenttypes:default')


PLONE_WITH_BUILDER_FIXTURE = PloneWithBuilder()
PLONE_WITH_BUILDER_FUNCTIONAL = FunctionalTesting(
    bases=(PLONE_WITH_BUILDER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.gopip:plone_with_builder:functional")


class TestInstallAndUninstallRoundtrip(TestCase):
    layer = PLONE_WITH_BUILDER_FUNCTIONAL

    def setUp(self):
        super(TestCase, self).setUp()
        self.portal = self.layer['portal']
        self.grant('Manager')

        create(Builder('folder').titled(u'two'))
        one = create(Builder('folder').titled(u'One'))
        create(Builder('folder').titled(u'three'))
        self.portal.moveObjectsByDelta(['one', 'two', 'three'],
                                       -len(self.portal.objectIds()))
        self.portal.plone_utils.reindexOnReorder(self.portal)

        create(Builder('folder').titled(u'b1').within(one))
        create(Builder('folder').titled(u'c1').within(one))
        create(Builder('folder').titled(u'a1').within(one))
        one.moveObjectsByDelta(['a1', 'b1', 'c1'],
                               -len(one.objectIds()))

    def test_installing_and_uninstall_does_not_break_index_behaviour(self):
        self.assert_correct_ordering()
        applyProfile(self.portal, 'ftw.gopip:default')
        self.assert_correct_ordering()
        applyProfile(self.portal, 'ftw.gopip:uninstall')
        self.assert_correct_ordering()

    def assert_correct_ordering(self):
        self.assert_order('one', 'a1',
                          'two', 'b1',
                          'three', 'c1')

    def assert_order(self, *expected_ordered_ids):
        catalog = getToolByName(self.portal, 'portal_catalog')
        brains = catalog({'sort_on': 'getObjPositionInParent'})
        got_ordered_ids = tuple(map(attrgetter('getId'), brains))
        self.assertEquals(expected_ordered_ids, got_ordered_ids)

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
