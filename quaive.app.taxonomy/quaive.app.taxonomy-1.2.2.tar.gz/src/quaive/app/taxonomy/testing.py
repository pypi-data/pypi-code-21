# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.testing import z2

import quaive.app.taxonomy


class QuaiveAppTaxonomyLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import ploneintranet.layout
        self.loadZCML(package=ploneintranet.layout)
        self.loadZCML(package=quaive.app.taxonomy)
        self.loadZCML(package=quaive.app.taxonomy.tests)

    def setUpPloneSite(self, portal):
        ps = api.portal.get_tool('portal_setup')
        ps.runImportStepFromProfile(
            'profile-ploneintranet.suite:full', 'plone.app.registry')
        applyProfile(portal, 'ploneintranet.layout:default')
        applyProfile(portal, 'ploneintranet.search:default')
        ps.runImportStepFromProfile(
            'profile-ploneintranet.workspace:default', 'catalog')
        applyProfile(portal, 'quaive.app.taxonomy:default')
        applyProfile(portal, 'quaive.app.taxonomy.tests:testing')
        setRoles(portal, TEST_USER_ID, ['Manager'])

QUAIVE_APP_TAXONOMY_FIXTURE = QuaiveAppTaxonomyLayer()


QUAIVE_APP_TAXONOMY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(QUAIVE_APP_TAXONOMY_FIXTURE,),
    name='QuaiveAppTaxonomyLayer:IntegrationTesting'
)


QUAIVE_APP_TAXONOMY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(QUAIVE_APP_TAXONOMY_FIXTURE,),
    name='QuaiveAppTaxonomyLayer:FunctionalTesting'
)


QUAIVE_APP_TAXONOMY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        QUAIVE_APP_TAXONOMY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='QuaiveAppTaxonomyLayer:AcceptanceTesting'
)
