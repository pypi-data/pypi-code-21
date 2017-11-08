""" Base test cases
"""
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_eea_relations():
    """Set up the additional products. """
    fiveconfigure.debug_mode = True
    import eea.relations
    zcml.load_config('configure.zcml', eea.relations)
    fiveconfigure.debug_mode = False

    PloneTestCase.installPackage('eea.relations')

setup_eea_relations()
PloneTestCase.setupPloneSite(extension_profiles=('eea.relations:demo',))

class EEARelationsFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Base class for functional tests for the 'EEA Relations' product.
    """
