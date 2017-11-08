""" Base test cases
"""
import logging
import eea.geotags
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

logger = logging.getLogger('eea.geotags.tests.base')

PloneTestCase.installProduct('ATVocabularyManager')

@onsetup
def setup_eea_geotags():
    """Set up the additional products.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', eea.geotags)
    fiveconfigure.debug_mode = False

    PloneTestCase.installPackage('eea.alchemy')
    PloneTestCase.installPackage('eea.jquery')

setup_eea_geotags()
PloneTestCase.setupPloneSite(extension_profiles=('eea.geotags:default',
                                                 'eea.geotags:demo'))

class EEAGeotagsTestCase(PloneTestCase.PloneTestCase):
    """ Base class for integration tests for the 'EEA Geotags' product.
    """

class EEAGeotagsFunctionalTestCase(PloneTestCase.FunctionalTestCase,
                                   EEAGeotagsTestCase):
    """ Base class for functional integration tests for the
        'EEA Geotags' product.
    """
