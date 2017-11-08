""" Base test cases
"""
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_eea_faceted_inheritance():
    """Set up the additional products.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True

    import eea.faceted.inheritance
    zcml.load_config('configure.zcml', eea.faceted.inheritance)
    zcml.load_config('configure.zcml', eea.faceted.inheritance.subtypes)
    fiveconfigure.debug_mode = False

setup_eea_faceted_inheritance()
ptc.setupPloneSite(extension_profiles=('eea.faceted.inheritance:default',))

class FacetedInheritanceFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for functional integration tests for eea.faceted.inheritance
    """
