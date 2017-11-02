import re
import requests
from confutil import Config
from configobj import ConfigObj
from ..response import Response

USER_AGENT = 'ptclient/2.3'
DEFAULT_VERSION = 'v2'


def iter_not_none(*args, **kwargs):
    if args:
        kwargs.update(args[0])
    for key in kwargs:
        if kwargs[key] is None:
            continue
        yield (key, kwargs[key])


class BaseClient:
    def __init__(self, config=None, username=None, apikey=None, uri=None,
                 raise_status=False, verbose=False, _user_agent=USER_AGENT):
        if config:
            self.config = ConfigObj(config)
        else:
            self.config = Config('passivetotal')
        self.uri = (
            uri or self.config.get('URI') or 'https://api.passivetotal.org/'
        )
        # strip trailing forward slashes
        self.uri = re.sub(r'/+$', '', self.uri)
        self.username = username or self.config.get('USERNAME')
        self.apikey = apikey or self.config.get('APIKEY')
        self.auth = (self.username, self.apikey)
        self.raise_status = raise_status
        self.verbose = verbose
        self._user_agent = _user_agent

    def _request(self, path, version=DEFAULT_VERSION, params=None, method=None,
                 data=None):
        method = (method or 'get').lower()
        params = params or {}
        url = self._build_url(path, version=version)
        if self.verbose:
            print('Querying {}'.format(url))
        request_method = getattr(requests, method)
        headers = {'User-Agent': self._user_agent}
        response = request_method(url, params=params, json=data, auth=self.auth,
                                  headers=headers)
        if self.verbose:
            print('{} response, status: {}'.format(response.url,
                                                   response.status_code))
        return Response(response, raise_status=self.raise_status, path=path)

    def _build_url(self, path, version=DEFAULT_VERSION):
        path = re.sub(r'^/+', '', path)
        return '{}/{}/{}'.format(self.uri, version, path)

    def get(self, path, params=None, data=None, version=DEFAULT_VERSION):
        return self._request(path, params=params, data=data, version=version,
                             method='get')

    def post(self, path, params=None, data=None, version=DEFAULT_VERSION):
        return self._request(path, params=params, data=data, version=version,
                             method='post')

    def put(self, path, params=None, data=None, version=DEFAULT_VERSION):
        return self._request(path, params=params, data=data, version=version,
                             method='put')

    def delete(self, path, params=None, data=None, version=DEFAULT_VERSION):
        return self._request(path, params=params, data=data, version=version,
                             method='delete')
