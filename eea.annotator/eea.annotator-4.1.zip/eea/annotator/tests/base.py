""" Testing
"""
from plone.testing import z2
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting

class EEAFixture(PloneSandboxLayer):
    """ EEA Testing Policy
    """
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import eea.annotator
        import eea.icons
        self.loadZCML(package=eea.annotator)
        self.loadZCML(package=eea.icons)
        z2.installProduct(app, 'eea.annotator')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'eea.annotator')

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        self.applyProfile(portal, 'eea.annotator:default')

        # Login as manager
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # Create testing environment
        portal.invokeFactory("Folder", "sandbox", title="Sandbox")

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
                                       name='EEAAnnotator:Functional')
