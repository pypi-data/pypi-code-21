import copy
import urllib.parse
from typing import Dict, Tuple

from fizzgun.fizzgun_exception import FizzgunException

DEFAULT_PORTS = {
    'http': 80,
    'https': 443
}


class HttpRequestBuilder(object):
    """Immutable builder of Fizzgun's http request dictionaries"""

    def __init__(self):
        self._method = None
        self._scheme = None
        self._host = None
        self._port = None
        self._path = None
        self._query = None
        self._headers = []
        self._http_version = 'HTTP/1.1'
        self._body = ''

    @classmethod
    def new_from(cls, request_dict: Dict) -> 'HttpRequestBuilder':
        """Creates a new builder instance with the given initial state"""
        request_builder = HttpRequestBuilder()
        return request_builder._copy_with(**request_dict)

    def with_method(self, method: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request method"""
        return self._copy_with(method=method)

    def with_scheme(self, scheme: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request scheme"""
        return self._copy_with(scheme=scheme)

    def with_url(self, url: str) -> 'HttpRequestBuilder':
        """
        Returns a new builder instance with updated scheme, host, port, path, and query extracted from the given url
        """
        u = urllib.parse.urlparse(url)
        return self._copy_with(scheme=u.scheme, host=u.hostname, port=u.port, path=u.path, query=u.query)

    def with_host(self, host: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request host"""
        return self._copy_with(host=host)

    def with_port(self, port: int) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request port"""
        return self._copy_with(port=port)

    def with_path(self, path: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request path"""
        return self._copy_with(path=path)

    def with_query(self, query: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request query string"""
        return self._copy_with(query=query)

    def with_query_args(self, *query_args: Tuple[str, str]) -> 'HttpRequestBuilder':
        """
        Returns a new builder instance with a query string built from the given arguments
        """
        query = urllib.parse.urlencode(query_args, doseq=True)
        return self.with_query(query)

    def with_http_version(self, http_version: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request http version"""
        return self._copy_with(http_version=http_version)

    def with_header(self, name: str, value: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given header name and value"""
        request_builder = self._copy_with()
        request_builder._headers.append((name, value))
        return request_builder

    def without_header(self, name: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given header removed (if it exists)"""
        headers = [(hn, hv) for (hn, hv) in self._headers if hn.lower() == name.lower()]
        return self._copy_with(headers=headers)

    def with_headers(self, *headers: Tuple[str, str]) -> 'HttpRequestBuilder':
        """Returns a new builder instance with all the given headers added"""
        request_builder = self._copy_with()
        request_builder._headers.extend((h[0], h[1]) for h in headers)
        return request_builder

    def with_body(self, body: str) -> 'HttpRequestBuilder':
        """Returns a new builder instance with the given request body"""
        return self._copy_with(body=body)

    def build(self) -> Dict:
        """Return a request dictionary representation build from the state of this builder"""
        self._validate()
        port = self._port or DEFAULT_PORTS.get(self._scheme, 80)
        print(self._scheme, port)
        return {
            'method': self._method,
            'scheme': self._scheme,
            'host': self._host,
            'port': port,
            'path': self._path,
            'query': self._query,
            'headers': copy.deepcopy(self._headers),
            'http_version': self._http_version,
            'body': self._body
        }

    def _validate(self):
        if not self._method:
            raise FizzgunException('Request method must be defined')
        if not self._scheme or self._scheme.lower() not in DEFAULT_PORTS:
            raise FizzgunException('Unsupported request scheme: %s' % self._scheme)
        if not self._host:
            raise FizzgunException('Request host must be defined')
        if not self._path:
            raise FizzgunException('Request path must be defined')

    def _copy_with(self, **kwargs) -> 'HttpRequestBuilder':
        new = self.__class__()
        new._method = kwargs.get('method', self._method)
        new._scheme = kwargs.get('scheme', self._scheme)
        new._host = kwargs.get('host', self._host)
        new._port = kwargs.get('port', self._port)
        new._path = kwargs.get('path', self._path)
        new._query = kwargs.get('query', self._query)
        new._http_version = kwargs.get('http_version', self._http_version)
        new._headers = copy.deepcopy(kwargs.get('headers', self._headers))
        new._body = kwargs.get('body', self._body)
        return new
