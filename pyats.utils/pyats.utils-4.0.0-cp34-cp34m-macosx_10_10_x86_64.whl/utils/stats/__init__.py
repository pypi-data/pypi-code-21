import os
import sys
import getpass
import logging
import platform
import httplib2
import mimetypes
import traceback

from time import time
from datetime import datetime, timezone
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

# limit imports
__all__ = ['StatsMonitor', 'CesMonitor']

# this application name
APPLICATION = 'pyATS'

# static information from environment
HOST = platform.node()
USER = getpass.getuser()


class BaseStats(object):
    '''BaseStats

    Base class to be inherited by all statistics collection related apis. All
    inherited subclasses should implement the _post() api.

    '''

    def post(self, *args, **kwargs):
        '''post

        Post API that handles the error checking and results returns from stats
        related subclasses. Internally invokes _post() function to get things
        going.

        Arguments
        ---------
            args, kwargs: arguments to be propagated to _post() api.

        Returns
        -------
            Nothing. All exceptions are suppressed and logged via logger.debug()

        '''

        try:
            result = self._post(*args, **kwargs)

            logger.debug('%s result: %s' % (type(self).__name__, str(result)))
        except Exception:
            logger.debug('%s exception: %s' % (type(self).__name__, 
                                               traceback.format_exc()))

    def _post(self):
        '''_post

        API to be implemented by the subclass implementer.
        '''

        raise NotImplementedError


class StatsMonitor(BaseStats):

    # tracking server
    STATS_SERVER = 'http://pyats-ci.cisco.com'
    STATS_PORT = 80
    STATS_URL = '%s:%s/metrics/appUsage/storeStats' % (STATS_SERVER, STATS_PORT)
    STATS_TIMEOUT = 5
    STATS_HEADER = {'Content-type': 'application/x-www-form-urlencoded'}

    def __init__(self, user = USER,
                       server = HOST,
                       instance = sys.prefix,
                       tcltree = os.environ.get('AUTOTEST', '')):

        self.user = user
        self.server = server
        self.instance = instance
        self.tcltree = tcltree

    def _post(self):        
        http = httplib2.Http(timeout = self.STATS_TIMEOUT)

        return http.request(uri = self.STATS_URL,
                            method = 'POST',
                            body = urlencode(dict(user = self.user,
                                                  application = APPLICATION,
                                                  server = self.server,
                                                  installPath = self.instance,
                                                  tclATSPath = self.tcltree)),
                            headers = self.STATS_HEADER)



class CesMonitor(BaseStats):
    "Class for posting information to CES-monitor"

    # CES info
    CES_HOST = 'xml.cisco.com'
    CES_PATH = 'monitor/xml/create.svc'
    CES_TIMEOUT = 5
    CES_URL = 'http://{host}/{path}'.format(host = CES_HOST, path = CES_PATH)

    def __init__(self,
                 user = USER,
                 interface_name = 'CLI',
                 action = '',
                 host = HOST,
                 application = APPLICATION,
                 starttime = None):

        self.user = user
        self.interface = interface_name
        self.host = host
        self.action = action
        self.application = application
        self.starttime = starttime or time()

    def _post(self, duration = None):
        "Post results based on preferred method"
        
        # wrap duration into integer
        duration = int(duration or self.starttime - time())

        # convert time.time() into a datetime then format it
        # note that CES requires UTC time, offset not allowed
        starttime = datetime.utcfromtimestamp(self.starttime)
        
        # format the xml
        xml = '''\
<?xml version="1.0" encoding="ISO-8859-1"?>
<Monitor xsi:schemaLocation="http://xml.cisco.com/monitor/namespace \
http://xml.cisco.com/monitor/xsd/Monitor.xsd" \
xmlns="http://xml.cisco.com/monitor/namespace" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
     <Call>
        <StartTime>{starttime}</StartTime>
        <User>{self.user}</User>
        <Action>{self.action}</Action>
        <Duration>{duration}</Duration>
        <Application>{self.application}</Application>
        <Interface>{self.interface}</Interface>
        <Host>{self.host}</Host>
    </Call>
</Monitor>'''.format(self = self, 
                     duration = duration, 
                     starttime = starttime.strftime('%Y-%m-%dT%T+00:00'))

        logger.debug('CesMonitor XML: %s' % xml)

        content_type, body = self.encode_multipart_formdata([], [['xmldata', 
                                                                  'xmldata', 
                                                                  xml]])

        headers = {'content-type': content_type, 
                   'content-length': str(len(body))}

        logger.debug('CesMonitor headers: %s' % headers)
        logger.debug('CesMonitor body: %s' % body)

        http = httplib2.Http(timeout = self.CES_TIMEOUT)

        return http.request(uri = self.CES_URL,
                            method = 'POST',
                            headers = headers,
                            body = body)


    def encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be
        uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append(\
                'Content-Disposition: form-data; name="%s"; filename="%s"'\
                        % (key, filename))
            L.append('Content-Type: %s' % self.get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body

    def get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


# list of classes to be auto-posted
_auto_postit = [StatsMonitor, ]

# auto-post when this module is imported
[cls().post() for cls in _auto_postit]
