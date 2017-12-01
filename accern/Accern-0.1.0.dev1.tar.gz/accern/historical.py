"""Python library for Accern API.

Core client functionality, common across all API requests (including performing
HTTP requests).
"""

try:
    import requests
except ImportError:
    requests = None

from accern import error, http_client, util
from accern.util import six, urlsplit, urlunsplit, urlencode

api_base = "http://feed-staging.accern.com/v4/stream"


def _api_encode(data):
    for key, value in six.iteritems(data):
        key = util.utf8(key)
        if value is None:
            continue
        elif isinstance(value, list):
            yield (key, ",".join(value))
        else:
            yield (key, util.utf8(value))


class Historical(object):
    """Perform requests to the Accern API web services."""

    def __init__(self, client=None, token=None):
        """Intialize with params.

        :param client: default http client. Optional
        :param token: Accern API token. Required.
        """
        self.api_base = api_base
        self.token = token
        self._client = client or http_client.new_default_http_client()

    def _build_api_headers(self, api_key, method):
        headers = {
            'Authorization': 'Token token=%s' % (api_key)
        }
        return headers

    def _build_api_url(self, url, query):
        scheme, netloc, path, base_query, fragment = urlsplit(url)
        if base_query:
            query = '%s&%s' % (base_query, query)
        return urlunsplit((scheme, netloc, path, query, fragment))

    def request(self, method=None, params=None):
        """Perform HTTP GET/POST with credentials.

        :param url: URL path for the request. Should begin with a slash.

        :param params: HTTP GET parameters.

        :raises ApiError: when the API returns an error.
        :raises Timeout: if the request timed out.
        :raises TransportError: when something went wrong while trying to
            exceute a request.
        """
        if self.token:
            my_token = self.token
        else:
            from accern import token
            my_token = token

        if my_token is None:
            raise error.AuthenticationError('No Token provided')

        abs_url = '%s' % (self.api_base)
        if params is None:
            params = {'token': my_token}
        else:
            params['token'] = my_token
        encoded_params = urlencode(list(_api_encode(params or {})))

        if method == 'get':
            if params:
                abs_url = self._build_api_url(abs_url, encoded_params)
            post_data = None
        elif method == 'post':
            return 'post not implemented yet'
        else:
            raise error.APIConnectionError('Unrecognized HTTP method %r' % (method))

        headers = self._build_api_headers(my_token, method)
        rbody, rcode, rheaders = self._client.request(method, abs_url, headers, post_data)
        return rbody, rcode, rheaders

    def save(self, method, output):
        resp = self.request_raw(method)
        jsonData = util.json.loads(resp.text)
        with open(output, 'w') as outfile:
            util.json.dump(jsonData, outfile)
