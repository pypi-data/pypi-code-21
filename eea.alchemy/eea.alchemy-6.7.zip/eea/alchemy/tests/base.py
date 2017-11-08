""" Base test cases
"""
import logging
from Zope2.App import zcml
from plone.uuid.interfaces import IUUID
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from zope.component import provideUtility
from eea.alchemy.tests.fake import FakeAlchemyAPI, IAlchemyAPI
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
import eea.alchemy
try:
    import eea.relations
    EEA_RELATIONS = True
except ImportError:
    EEA_RELATIONS = False

logger = logging.getLogger('eea.alchemy.tests.base')

@onsetup
def setup_eea_alchemy():
    """ Set up the additional products.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True

    if EEA_RELATIONS:
        zcml.load_config('configure.zcml', eea.relations)
    zcml.load_config('configure.zcml', eea.alchemy)

    fiveconfigure.debug_mode = False

    if EEA_RELATIONS:
        ptc.installPackage('eea.relations')
    ptc.installPackage('eea.alchemy')

    provideUtility(FakeAlchemyAPI(), IAlchemyAPI)

extension_profiles = ('eea.alchemy:default',)
if EEA_RELATIONS:
    extension_profiles = ('eea.relations:default',) + extension_profiles

setup_eea_alchemy()
ptc.setupPloneSite(extension_profiles=extension_profiles)

class EEAAlchemyTestCase(ptc.PloneTestCase):
    """ Base class for integration tests for the 'EEA Alchemy' product.
    """

class EEAAlchemyFunctionalTestCase(ptc.FunctionalTestCase, EEAAlchemyTestCase):
    """ Base class for functional integration tests for
        the 'EEA Alchemy' product.
    """
    _sandbox = None
    _brain = None
    _page = None

    @property
    def sandbox(self):
        """ Sandbox
        """
        return self._sandbox

    @property
    def page(self):
        """ A page
        """
        return self._page

    @property
    def brain(self):
        """ Brain
        """
        return self._brain

    def afterSetUp(self):
        """ Setup
        """
        # login as Manager otherwise we don't have permission to create a
        # version
        self.setRoles(['Manager'])

        sid = self.folder.invokeFactory('Folder', id='sandbox')
        sandbox = self.folder._getOb(sid)
        eid = self.folder.invokeFactory('Event', id='an-event')
        eid = self.folder.invokeFactory('Event', id='new-event')
        pid = self.folder.invokeFactory('Document', id='new-article')

        page = self.folder._getOb(pid)
        # 14924 without this flag the page id will be changed on processForm
        page._at_rename_after_creation = False

        event = self.folder._getOb(eid)
        uid = IUUID(event)

        sandbox.processForm(data=1, metadata=1, values={
            'title': (
                "Formation of new land cover in the region of Valencia, Spain"
            ),
            'description': (
                "Urban sprawl 1990-2000 in the province of Venice "
                "using a 1 km x 1 km grid. See more: "
            ),
        })
        self._sandbox = sandbox

        sid = sandbox.getId()
        brains = self.portal.portal_catalog(getId=sid)
        self._brain = brains[0]

        page.processForm(data=1, metadata=1, values={
            'title': (
                "Formation of new land cover in the region of Valencia, Spain"
            ),
            'text': (
                "Urban sprawl 1990-2000 in the province of "
                "<a name=\"Venice\"></a>Venice "
                "using a 1 km x 1 km grid. See more: "
                ""
                "<a href='https://nohost/plone"
                "/Members/test_user_1_/new-article'>article</a> or "
                "<a href='/Members/test_user_1_/an-event'>event</a> or "
                "<a href='resolveuid/%s'>other event</a> or "
                "if you prefer this "
                "<a href='http://foobar.com/new-article'>"
                "external article</a>" % uid
            ),
        })

        self._page = page

        atool = IAlchemySettings(self.portal)
        atool.token = u'12345665766867'
