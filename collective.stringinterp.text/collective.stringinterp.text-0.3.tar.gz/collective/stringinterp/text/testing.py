from zope.configuration import xmlconfig

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import applyProfile


class StringInterpTextLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import collective.stringinterp.text
        xmlconfig.file('configure.zcml',
                       collective.stringinterp.text,
                       context=configurationContext)

STRING_INTERP_TEXT_FIXTURE = StringInterpTextLayer()
STRING_INTERP_TEXT_INTEGRATION_TESTING = \
    IntegrationTesting(bases=(STRING_INTERP_TEXT_FIXTURE, ),
                       name="StringInterpText:Integration")
STRING_INTERP_TEXT_SEMANTIC_FUNCTIONAL_TESTING = \
    FunctionalTesting(bases=(STRING_INTERP_TEXT_FIXTURE, ),
                       name="StringInterpText:Functional")
