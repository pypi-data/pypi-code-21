"""the main class."""
from random import randint
from time import time
from urllib.parse import urlencode

from hmac_signature import Signature


class QcloudAPI:
    """the class to generate correct api"""

    def __init__(self):
        self.parameters = {}
        self._url = ''
        self._method = ''

    def url(self, url):
        """set the url of the api"""
        self._url = url
        return self

    def action(self, action):
        """set action parameter"""
        self.parameters['Action'] = action
        return self

    def secret_id(self, secret_id):
        """set secretId parameter"""
        self.parameters['SecretId'] = secret_id
        return self

    def nonce(self, nonce=None):
        """set nonce parameter"""
        if nonce is None:
            nonce = randint(0, 10000)
        self.parameters['Nonce'] = nonce
        return self

    def timestamp(self, timestamp=None):
        """set timestamp parameter"""
        if timestamp is None:
            timestamp = int(time())
        self.parameters['Timestamp'] = timestamp
        return self

    def region(self, region):
        """set region parameter"""
        self.parameters['Region'] = region
        return self

    def custom(self, key, value):
        """set custom key-value parameter"""
        self.parameters[key] = value
        return self

    def method(self, method):
        """set HTTP request method"""
        self._method = method
        return self

    def signature_method(self, method='HmacSHA1'):
        """set hmac method"""
        self.parameters['SignatureMethod'] = method
        return self

    def append(self, params):
        """add multi key-value parameters"""
        self.parameters.update(params)
        return self

    def origin(self):
        """get the content to hmac method"""
        ordered = {key: self.parameters[key]
                   for key in sorted(self.parameters.keys())}
        params = urlencode(ordered).replace("%7B", "{").replace("%7D", "}")\
            .replace("%22", '"').replace("%3A", ":").replace("%2C", ",")
        return f'{self._method}{self._url}?{params}'

    def sign(self, key):
        """get the signature"""
        method = 'sha1' if self._method == 'HmacSHA1' else 'sha256'
        self.custom('Signature', Signature.create(
            key.encode(), method, self.origin().encode()).decode())
        return self

    def final(self):
        """get the final request address"""
        ordered = {key: self.parameters[key]
                   for key in sorted(self.parameters.keys())}
        return f'https://{self._url}?{urlencode(ordered)}'
