"""Client library for Direqt Ads API."""
import json
import logging
import urllib
import urllib2

logger = logging.getLogger(__name__)

# Endpoint used by default for API requests.
_DEFAULT_ENDPOINT = 'https://ads.direqt.io'
# user-agent used by default when making API requests.
_DEFAULT_USER_AGENT = 'unknown'
# Supported ad formats
_AD_FORMAT_RBM10 = 'RBMV1.0'
_DEFAULT_AD_FORMAT = _AD_FORMAT_RBM10
_VALID_AD_FORMATS = [_AD_FORMAT_RBM10]


class DireqtClient(object):
    """Client for the Direqt ad server."""

    def __init__(self, api_key, ad_format=_DEFAULT_AD_FORMAT, user_agent=_DEFAULT_USER_AGENT, **kwargs):
        """Initializes a DireqtClient.

        Args:
            api_key: A string containing your Direqt API key.
            format: Must be 'RBMv1.0'
            user_agent: An arbitrary string containing only ASCII characters
                that will be used to identify your application. If not set,
                defaults to "unknown".
            **kwargs: Optional keyword arguments.

        Keyword Arguments:
            None defined.
        """
        super(DireqtClient, self).__init__()

        if ad_format not in _VALID_AD_FORMATS:
            raise NotImplementedError(
                'The provided ad format "%s" is invalid. Accepted formats are: %s'
                % (format, _VALID_AD_FORMATS))

        self.api_key = api_key
        self.fmt = ad_format
        self.user_agent = user_agent
        self.endpoint = kwargs.get('endpoint', _DEFAULT_ENDPOINT)

    def fetch(self, ad_unit, session="", **kwargs):
        """Fetch an ad from the Direqt Ads API.

        Args:
            placement: A string referencing a placement defined for your project.
            session: A string identifying the current user session.
        """
        params = {
            'key': self.api_key,
            'format': self.fmt,
            'adUnit': ad_unit,
            'session': session
        }
        valid_keys = (key for key in kwargs if key not in ['key', 'format', 'adUnit', 'session'])
        for key in valid_keys:
            params[key] = kwargs[key]

        url = self.endpoint + "/fetch?" + urllib.urlencode(params)
        request = urllib2.Request(url, data="")
        try:
            response = urllib2.urlopen(request)
            if response.code == 200:
                body = response.read()
                payload = json.loads(body)['payload']
                return payload
        except urllib2.URLError, e:
            logger.warning('Failed to load ad: ' + e.message)
            return {}

        return json.loads(response.read())
