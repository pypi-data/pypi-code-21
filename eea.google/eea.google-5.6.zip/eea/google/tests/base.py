""" Base test cases
"""
import urllib
from StringIO import StringIO
from cgi import FieldStorage

import os
from zope.interface import implements

import eea.google
from eea.google.api import Connection
from eea.google.analytics.interfaces import IGoogleAnalyticsConnection
from App.Common import package_home
# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.Five import fiveconfigure as metaconfigure
from ZPublisher.HTTPRequest import FileUpload
from Zope2.App.zcml import load_config

product_globals = globals()

#
# Fake Google
#
class GoogleFakeConnection(Connection):
    """ Fake Google Connection """
    @property
    def status(self):
        """ Session status
        """
        if self.token == 'SINGLE_SESSION_TOKEN':
            self.token = 'EXPIRED_TOKEN'
            return 200, 'OK'

        if self.token == 'GOOD_TOKEN':
            return 200, 'OK'

        return 403, 'GoogleError: HTTP Error 403: Invalid AuthSub token.'

    def token2session(self):
        """ Token status
        """
        if self.token != 'SINGLE_SESSION_TOKEN':
            return None
        self.token = 'GOOD_TOKEN'
        return self.token

    def __call__(self, scope, data=None, method='GET'):
        data = urllib.urlencode(data)
        return StringIO('''<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom'
  xmlns:openSearch='http://a9.com/-/spec/opensearchrss/1.0/'
  xmlns:dxp='http://schemas.google.com/analytics/2009'>
  <id>http://www.google.com/analytics/...</id>
  <updated>2009-09-17T08:47:18.814-07:00</updated>
  <title type='text'>Some title</title>
  <link rel='self' type='application/atom+xml' href='...'/>
  <link rel='next' type='application/atom+xml' href='...'/>
  ...
  <entry>
    <id>http://www.google.com/analytics/feeds/data?%(data)s</id>
    <updated>2019-12-30T16:00:00.001-08:00</updated>
    <title type='text'>ga:pagePath=/data/downloads/6BTID0682R</title>
    <link rel='alternate' type='text/html' href='http://www.google.com/analytics'/>
    <dxp:dimension name='ga:pagePath' value='/data/downloads/6BTID0682R'/>
    <dxp:metric confidenceInterval='0.0' name='ga:pageviews' type='integer' value='1'/>
  </entry>
  ...
</feed>
''' % {'data': data})

class GoogleFakeAnalyticsConnection(object):
    """ Access Google Analytics
    """
    implements(IGoogleAnalyticsConnection)

    def __call__(self, token):
        self.connection = GoogleFakeConnection(token)
        return self.connection


@onsetup
def setup_eea_google():
    """Set up the additional products.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    metaconfigure.debug_mode = True
    load_config('configure.zcml', eea.google)
    metaconfigure.debug_mode = False

    from zope.component import provideUtility
    provideUtility(GoogleFakeAnalyticsConnection(), IGoogleAnalyticsConnection)

setup_eea_google()
PloneTestCase.setupPloneSite(extension_profiles=('eea.google:default',))

class GoogleTestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests for the 'Google Tool' product.
    """

class GoogleFunctionalTestCase(PloneTestCase.FunctionalTestCase,
                               GoogleTestCase):
    """Base class for functional integration tests for
       the 'Google Tool' product.
    """
    def loadfile(self, rel_filename, ctype='text/xml', zope=False):
        """ load a file
        """
        home = package_home(product_globals)
        filename = os.path.sep.join([home, rel_filename])
        data = open(filename, 'r').read()

        fp = StringIO(data)
        fp.seek(0)

        if not zope:
            return fp

        header_filename = rel_filename.split('/')[-1]
        env = {'REQUEST_METHOD':'PUT'}
        headers = {
            'content-type' : ctype,
            'content-length': len(data),
            'content-disposition':'attachment; filename=%s' % header_filename}

        fs = FieldStorage(fp=fp, environ=env, headers=headers)
        return FileUpload(fs)
