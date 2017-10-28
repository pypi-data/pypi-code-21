# -*- coding: utf-8 -*-
"""iceman/crypto_strategies/fernet.py
"""
import base64
from cryptography import fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from iceman.crypto_strategies.strategy import Strategy

class Fernet(Strategy):
    """Fernet Strategy implementation

    :param preshared_key: symmetric encryption key
    :type preshared_key: str
    """

    def __init__(self, preshared_key):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(preshared_key)
        encoded_key = base64.b64encode(digest.finalize())
        self.cipher_suite = fernet.Fernet(encoded_key)

    def encrypt(self, payload):
        """encrypts a given payload

        :param payload: the string to encrypt
        :type payload: str

        :returns: str -- the encrypted payload
        """
        return self.cipher_suite.encrypt(str(payload))

    def decrypt(self, token):
        """decrypts a given token

        :param token: the token to decrypt
        :type token: str

        :returns: str -- the decrypted token
        """
        return self.cipher_suite.decrypt(str(token))
