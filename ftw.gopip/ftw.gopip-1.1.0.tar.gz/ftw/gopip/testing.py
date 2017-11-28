from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from pkg_resources import get_distribution
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig


IS_PLONE_5_OR_GREATER = get_distribution('Plone').version >= '5'


class FtwLayer(PloneSandboxLayer):
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

        if not IS_PLONE_5_OR_GREATER:
            # The tests will fail with a
            # `ValueError: Index of type DateRecurringIndex not found` unless
            # the product 'Products.DateRecurringIndex' is installed.
            z2.installProduct(app, 'Products.DateRecurringIndex')

    def setUpPloneSite(self, portal):
        if IS_PLONE_5_OR_GREATER:
            applyProfile(portal, 'plone.app.contenttypes:default')
        applyProfile(portal, 'ftw.gopip:default')


FTW_FIXTURE = FtwLayer()
FTW_FUNCTIONAL = FunctionalTesting(
    bases=(FTW_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.gopip:functional")
