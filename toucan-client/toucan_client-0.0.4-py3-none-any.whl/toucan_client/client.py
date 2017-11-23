import logging

import requests

logger = logging.getLogger(__name__)


class ToucanClient:
    """
    Small client for sending request to a Toucan Toco back end.
    The constructor's mandatory parameter is the API base url. One can pass
    a small app name or a list of small app names, a token or an auth object
    for authentication.

    >>> # Example: Fetch etl config
    >>> client = ToucanClient('https://api.some.project.com')
    >>> small_app = client['my-small-app']
    >>> etl_config = small_app.config.etl.get()
    >>>
    >>> # Example: send a post request with some json data
    >>> response = small_app.config.etl.put(json={'DATA_SOURCE': ['example']})
    >>> # response.status_code equals 200 if everything went well
    """

    EXTRACTION_CACHE_PATH = 'extraction_cache'

    def __init__(self, base_route, **kwargs):
        # type: (str) -> SmallAppRequester
        self.__dict__['_path'] = []
        self.__dict__['kwargs'] = kwargs
        self.__dict__['stage'] = ''
        self.__dict__['_dfs'] = None
        self.__dict__['_cache_path'] = None

        self.__dict__['base_route'] = base_route
        if base_route.endswith('/'):
            self.__dict__['base_route'] = base_route[:-1]

    @property
    def method(self):
        # type: () -> str
        return self._path[-1]

    @property
    def options(self):
        # type: () -> str
        if self.stage:
            return '?stage={}'.format(self.stage)
        return ''

    @property
    def route(self):
        # type: () -> str
        route = '/'.join([self.base_route] + self._path[:-1])
        route += self.options

        self.__dict__['_path'] = []
        return route

    def __getattr__(self, key):
        self._path.append(key)
        return self

    def __setattr__(self, key, value):
        if key == 'stage':
            self.__dict__['stage'] = value
        else:
            self.kwargs[key] = value

    def __call__(self):
        # type: () -> requests.Response
        method, route = self.method, self.route
        func = getattr(requests, method)
        return func(route, **self.kwargs)
