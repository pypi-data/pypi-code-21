# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.z3cform.select2


class CollectiveZ3CformSelect2Layer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.z3cform.select2)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.z3cform.select2:default')


COLLECTIVE_Z3CFORM_SELECT2_FIXTURE = CollectiveZ3CformSelect2Layer()


COLLECTIVE_Z3CFORM_SELECT2_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_Z3CFORM_SELECT2_FIXTURE,),
    name='CollectiveZ3CformSelect2Layer:IntegrationTesting'
)


COLLECTIVE_Z3CFORM_SELECT2_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_Z3CFORM_SELECT2_FIXTURE,),
    name='CollectiveZ3CformSelect2Layer:FunctionalTesting'
)


COLLECTIVE_Z3CFORM_SELECT2_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_Z3CFORM_SELECT2_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveZ3CformSelect2Layer:AcceptanceTesting'
)
