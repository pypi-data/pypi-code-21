""" Google API
"""
import urllib
import logging
from eventlet.green import urllib2
from eea.google.api.exception import GoogleClientError
logger = logging.getLogger('eea.google.api')

class Connection(object):
    """ Google connection
    """
    def __init__(self, token):
        self.token = token
        self.authdomain = 'https://www.google.com'
        self.domain = 'https://www.googleapis.com'

    @property
    def headers(self):
        """ Request headers
        """
        return {
            'User-Agent': 'eea.google.api',
            'Authorization': 'AuthSub token="%s"' % self.token,
        }

    @property
    def status(self):
        """ Validate token
        """
        scope = '/accounts/AuthSubTokenInfo'
        try:
            response = self(scope)
        except GoogleClientError, err:
            return (403, err)
        return response.code, response.msg

    def token2session(self):
        """ Replace single call token with a session one.
        """
        scope = '/accounts/AuthSubSessionToken'
        try:
            response = self(scope)
        except GoogleClientError, err:
            logger.exception(err)
            return None

        data = response.readlines()
        token = [item.strip() for item in data
                 if item.lower().strip().startswith('token')]

        if not token:
            logger.exception('\n'.join(data))
            return None
        token = token[0].split('=')
        if not len(token) > 1:
            logger.exception('\n'.join(data))
            return None

        self.token = token[1]
        return self.token

    def request(self, scope, data=None, method='POST'):
        """ Safely call. Returns None if any error occurs.
        """
        try:
            return self(scope, data, method)
        except GoogleClientError:
            return None

    def __call__(self, scope, data=None, method='POST'):
        """ Query Google
        """
        if data:
            data = urllib.urlencode(data)

        if method != 'POST':
            scope = '%s?%s' % (scope, data)
            data = None

        domain = self.domain
        #fix for AuthSub auth in 2.4 API
        #should migrate to OAuth 2.0
        if 'AuthSub' in scope:
            domain = self.authdomain
        request = urllib2.Request(domain + scope,
                                  data=data, headers=self.headers)
        try:
            response = urllib2.urlopen(request, timeout=10)
        except urllib2.HTTPError, err:
            logger.exception(err)
            raise GoogleClientError(err)
        except Exception, err:
            logger.exception(err)
            raise GoogleClientError(err)
        return response
