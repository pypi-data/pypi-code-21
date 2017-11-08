""" Base test cases
"""
from plone.testing import z2
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
#from plone.app.testing import applyProfile

class EEAFixture(PloneSandboxLayer):
    """ Custom fixture
    """

    def setUpZope(self, app, configurationContext):
        """ Setup Zope
        """
        import eea.forms
        self.loadZCML(package=eea.forms)
        z2.installProduct(app, 'eea.forms')

    def tearDownZope(self, app):
        """ Uninstall Zope
        """
        z2.uninstallProduct(app, 'eea.forms')

    def setUpPloneSite(self, portal):
        """ Setup Plone
        """
        #applyProfile(portal, 'eea.forms:default')

EEAFIXTURE = EEAFixture()
FUNCTIONAL_TESTING = FunctionalTesting(bases=(EEAFIXTURE,),
            name='EEAForms:Functional')
