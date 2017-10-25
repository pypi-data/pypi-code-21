import collections
import copy
import json
from typing import Dict, List, Any

import fizzgun.util


class HttpRequest(object):
    """
    Wraps a dict-like request specification and provides utilities around it
    """

    def __init__(self, request_spec):
        self._r = request_spec

    @property
    def value(self) -> Dict:
        """Request dictionary representation"""
        return copy.deepcopy(self._r)

    @property
    def method(self) -> str:
        """The request method"""
        return self._r['method'].upper()

    @property
    def url(self) -> str:
        """The full request url (scheme://host:port/path?query)"""
        return "%s://%s:%d%s" % (self.scheme, self.host, self.port, self.path_with_query)

    @property
    def scheme(self) -> str:
        """The scheme section of the request URL"""
        return self._r['scheme'].lower()

    @property
    def host(self) -> str:
        """The host section of the request URL"""
        return self._r['host']

    @property
    def port(self) -> int:
        """The port section of the request URL"""
        return self._r['port']

    @property
    def path(self) -> str:
        """The path section of the request URL"""
        return self._r['path']

    @property
    def query(self) -> str:
        """The query string part of the request URL"""
        return self._r['query']

    @property
    def query_args(self) -> Dict[str, List[str]]:
        """Returns the parsed query string arguments"""
        return fizzgun.util.parse_qs(self.query or '', keep_blank_values=True)

    @property
    def path_with_query(self) -> str:
        """The request path + query string (if any)"""
        if self.query is not None:
            return "%s?%s" % (self.path, self.query)
        return self.path

    @property
    def body(self) -> str:
        """The request body"""
        return self._r.get('body')

    @property
    def json_body(self) -> Any:
        """The body parsed as json"""
        return json.loads(self._r['body'], object_pairs_hook=collections.OrderedDict)

    @property
    def form_urlencoded_body(self) -> Dict[str, List[str]]:
        """The body parsed as a urlencoded form"""
        return fizzgun.util.parse_qs(self._r['body'], keep_blank_values=True)

    @property
    def headers(self) -> Dict[str, str]:
        """The request headers"""
        headers = self._r.get('headers', [])
        return dict((name.lower(), value) for name, value in headers)

    @property
    def endpoint(self) -> str:
        """The host:port tuple for this request"""
        return "%s:%s" % (self.host, self.port)

    def content_type_includes(self, content_type_substr: str) -> bool:
        """
        Returns True if the given string is a substring of the Content-Type header value
        """
        for hn, hv in self._r.get('headers', []):
            if hn.lower() == 'content-type':
                return content_type_substr.lower() in hv.lower()
        return False

    def has_header(self, header: str) -> bool:
        """Returns True if the given header name (case insensitive) is included in the requests' headers"""
        return any(True for hn, hv in self._r.get('headers', []) if hn.lower() == header.lower())

    def has_body(self) -> bool:
        """Returns True if the request has a non-empty body"""
        if self._r.get('body'):
            return True
        return False
