# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.querynextprev


class CollectiveQuerynextprevLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.querynextprev)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.querynextprev:default')


COLLECTIVE_QUERYNEXTPREV_FIXTURE = CollectiveQuerynextprevLayer()


COLLECTIVE_QUERYNEXTPREV_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_QUERYNEXTPREV_FIXTURE,),
    name='CollectiveQuerynextprevLayer:IntegrationTesting'
)


COLLECTIVE_QUERYNEXTPREV_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_QUERYNEXTPREV_FIXTURE,),
    name='CollectiveQuerynextprevLayer:FunctionalTesting'
)


COLLECTIVE_QUERYNEXTPREV_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_QUERYNEXTPREV_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveQuerynextprevLayer:AcceptanceTesting'
)
