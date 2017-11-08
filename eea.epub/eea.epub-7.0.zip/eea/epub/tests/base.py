""" Base module for epub tests
"""
import os
import tempfile
from Products.Five import fiveconfigure as metaconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Zope2.App.zcml import load_config
import eea.epub
import eea.downloads

PATH = tempfile.mkdtemp(prefix='eea.epub.', suffix='.tests.epub')
TEMP = tempfile.mkdtemp(prefix='eea.epub.', suffix='.tests.tmp')

@onsetup
def setup_epub():
    """ setup epub test
    """
    metaconfigure.debug_mode = True
    load_config('configure.zcml', eea.epub)
    load_config('configure.zcml', eea.downloads)
    metaconfigure.debug_mode = False

    os.environ["EEADOWNLOADS_PATH"] = PATH
    os.environ["EEACONVERTER_TEMP"] = TEMP
    os.environ["EEADOWNLOADS_NAME"] = 'downloads'
    PloneTestCase.installPackage('eea.downloads')

setup_epub()
PloneTestCase.setupPloneSite(extension_profiles=('eea.epub:default',))

class EpubFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ EpubFunctionalTestCase class
    """
