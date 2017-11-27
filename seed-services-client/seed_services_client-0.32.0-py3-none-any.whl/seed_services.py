from demands import HTTPServiceClient, JSONServiceClient
from requests.adapters import HTTPAdapter

from .__version__ import __version__ as client_version


class SeedHTTPAdapter(HTTPAdapter):
    """
    HTTPAdapter child class to implement global timeouts
    """

    def __init__(self, timeout=None, *args, **kwargs):
        self.timeout = timeout
        super(SeedHTTPAdapter, self).__init__(*args, **kwargs)

    def send(self, *args, **kwargs):
        kwargs['timeout'] = self.timeout
        return super(SeedHTTPAdapter, self).send(*args, **kwargs)


class SeedServicesApiClient(object):
    """
    Base API client for seed services.

    :param str auth_token:
        An access token.

    :param str api_url:
        The full URL of the API.

    :param JSONServiceClient session:
        An instance of JSONServiceClient to use

    :param HTTPServiceClient session_https:
        An instance of HTTPServiceClient to use

    :param retries:
        (optional) The number of times to retry an HTTP request

    :param timeout:
        (optional) The number of seconds for a request to timeout,
        defaults to 65 seconds

    """

    def __init__(self, auth_token, api_url, session=None, session_http=None,
                 retries=0, timeout=65):

        headers = {
            'Authorization': 'Token ' + auth_token,
            'User-Agent': 'seed-services-client v{0}'.format(client_version),
        }

        if session is None:
            session = JSONServiceClient(url=api_url,
                                        headers=headers)
        self.session = session

        if session_http is None:
            session_http = HTTPServiceClient(url=api_url,
                                             headers=headers)

        self.session_http = session_http

        http_adapter_kwargs = {}

        if retries > 0:
            http_adapter_kwargs['max_retries'] = retries

        if timeout is not None:
            http_adapter_kwargs['timeout'] = timeout

        http = SeedHTTPAdapter(**http_adapter_kwargs)
        https = SeedHTTPAdapter(**http_adapter_kwargs)
        self.session.mount('http://', http)
        self.session.mount('https://', https)
