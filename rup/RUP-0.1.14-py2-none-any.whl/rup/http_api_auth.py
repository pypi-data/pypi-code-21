from requests.auth import AuthBase
from base64 import b64encode


class HTTPApiAuth(AuthBase):
    """Attaches HTTP Basic Authentication to the given Request object."""

    def __init__(self, key):
        self.key = key

    def __eq__(self, other):
        return all([
            self.key == getattr(other, 'key', None),
        ])

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        key = self.key

        if isinstance(key, str):
            key = key.encode('latin1')

        r.headers['Authorization'] = 'Basic ' + b64encode(key).strip()
        return r