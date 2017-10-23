from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.referencewidget.tests import builders
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class FtwReferenceWidgetLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.referencewidget.tests.views
        xmlconfig.file('configure.zcml',
                       ftw.referencewidget.tests.views,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'plone.app.registry:default')
        applyProfile(portal, 'ftw.referencewidget:default')
        applyProfile(portal, 'collective.z3cform.datagridfield:default')


FTW_REFERENCE_FIXTURE = FtwReferenceWidgetLayer()

FTW_REFERENCE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_REFERENCE_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.referencewidget:functional")
