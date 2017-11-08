""" Base module for sparql tests
"""

import BaseHTTPServer
import threading

import eea.sparql
#port for mock http server
from eea.sparql.tests.mock_server import PORT
from eea.sparql.tests.mock_server import Handler

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
#
# Layered testing
#
from plone.testing import z2
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting


@onsetup
def setup_sparql():
    """Set up the additional products.
    """
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', eea.sparql)
    fiveconfigure.debug_mode = False

    ztc.installPackage('eea.sparql')


setup_sparql()
ptc.setupPloneSite(products=['eea.sparql'])


class SparqlFunctionalTestCase(ptc.FunctionalTestCase):
    """ Base class for functional integration tests for the Sparql product.
    """
    def setUp(self):
        """ Start the mock http server on port 8888
            Since we make only one request we can use handle_request
        """
        self.server = BaseHTTPServer.HTTPServer(("", PORT), Handler)
        self.server_thread = threading.Thread(target=self.server.handle_request)
        self.server_thread.start()

    def tearDown(self):
        """ Stop the mock http server """
        self.server.server_close()
        self.server_thread.join()

    def afterSetUp(self):
        """ After setup """
        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                roles, [])

class EEAFixture(PloneSandboxLayer):
    """ EEA Testing Policy
    """
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        self.loadZCML(package=eea.sparql)
        z2.installProduct(app, 'eea.sparql')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'eea.sparql')

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        applyProfile(portal, 'eea.sparql:default')

        # Login as manager
        setRoles(portal, TEST_USER_ID, ['Manager'])

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
                                       name='EEASparql:Functional')
