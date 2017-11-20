# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import applyProfile


class QuaiveResourcesPloneintranetLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import plone.app.blocks
        self.loadZCML(package=plone.app.blocks)
        import quaive.resources.ploneintranet
        self.loadZCML(package=quaive.resources.ploneintranet)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'quaive.resources.ploneintranet:default')
        setRoles(portal, TEST_USER_ID, ('Member', 'Manager'))
        pw = api.portal.get_tool('portal_workflow')
        pw.setDefaultChain('simple_publication_workflow')
        pw.setChainForPortalTypes(('File',), 'simple_publication_workflow')

QUAIVE_RESOURCES_PLONEINTRANET_FIXTURE = QuaiveResourcesPloneintranetLayer()
QUAIVE_RESOURCES_PLONEINTRANET_INTEGRATION_TESTING = IntegrationTesting(
    bases=(QUAIVE_RESOURCES_PLONEINTRANET_FIXTURE, ),
    name="QuaiveResourcesPloneintranet:Integration"
)
