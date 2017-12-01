"""Accern: python library for Accern API.

Core client functionality, common across all API requests (including performing
HTTP requests).
"""

try:
    import requests
except ImportError:
    requests = None

api_base = "http://feed.accern.com"
api_version = "v4"


class Client(object):
    """Perform requests to the Accern API web services."""

    def __init__(self, key=None):
        """Intialize with params.

        :param key: Accern API key. Required.
        """
        if not key:
            raise ValueError("Must provide API key or enterprise credentials "
                             "when creating client.")

        self.session = requests.Session()
        self.key = key

    def request(self, url, params, base_url=api_base, version=api_version,
                requests_kwargs=None):
        """Perform HTTP GET/POST with credentials.

        :param url: URL path for the request. Should begin with a slash.

        :param params: HTTP GET parameters.

        :param base_url: The base URL for the request. Defaults to the Maps API
            server. Should not have a trailing slash.

        :param requests_kwargs: Same extra keywords arg for requests as per
            __init__, but provided here to allow overriding internally on a
            per-request basis.

        :raises ApiError: when the API returns an error.
        :raises Timeout: if the request timed out.
        :raises TransportError: when something went wrong while trying to
            exceute a request.
        """
        payload = {'token': self.key}
        resp = requests.get("http://{}/{}/alphas".format(api_base, "v4"),
                            params=payload)

        return resp
