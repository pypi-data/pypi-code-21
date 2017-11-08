""" Base test cases
"""
from StringIO import StringIO
from cgi import FieldStorage

import os

from App.Common import package_home
from Products.Five import fiveconfigure
from Products.Five import zcml
# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from ZPublisher.HTTPRequest import FileUpload

product_globals = globals()


@onsetup
def setup_eea_faceted_tool():
    """Set up the additional products.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    fiveconfigure.debug_mode = True
    import Products.Five
    zcml.load_config('meta.zcml', Products.Five)

    import eea.faceted.tool
    zcml.load_config('configure.zcml', eea.faceted.tool)
    fiveconfigure.debug_mode = False

    ptc.installProduct('Five')

setup_eea_faceted_tool()
ptc.setupPloneSite(extension_profiles=('eea.faceted.tool:default',))

class FacetedTestCase(ptc.PloneTestCase):
    """Base class for integration tests for the 'Faceted Tool' product.
    """

class FacetedFunctionalTestCase(ptc.FunctionalTestCase, FacetedTestCase):
    """ Base class for functional integration tests
    for the 'Faceted Tool' product.
    """
    def loadfile(self, rel_filename, ctype='text/xml'):
        """ load a file
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, rel_filename])
        data = open(filename, 'r').read()

        fp = StringIO(data)
        fp.seek(0)

        header_filename = rel_filename.split('/')[-1]
        env = {'REQUEST_METHOD':'PUT'}
        headers = {'content-type' : ctype,
                   'content-length': len(data),
                   'content-disposition':
                        'attachment; filename=%s' % header_filename}

        fs = FieldStorage(fp=fp, environ=env, headers=headers)
        return FileUpload(fs)
