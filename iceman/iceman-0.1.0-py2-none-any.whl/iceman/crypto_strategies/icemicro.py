# -*- coding: utf-8 -*-
"""icemicro module
"""
import base64

from iceman.crypto_strategies.strategy import Strategy

from icecore import icecore

class Icemicro(Strategy):
    """Icecore Strategy implementation

    :param preshared_key: symmetric encryption key
    :type preshared_key: str
    """
    def __init__(self, preshared_key):
        preshared_key = self.augment_preshared_key(preshared_key)
        encoded_key = base64.b64encode(preshared_key)
        cipher_suite = icecore.ICEBlockCipher(encoded_key) #pylint: disable=maybe-no-member
        self.cipher_suite = cipher_suite

    def augment_preshared_key(self, preshared_key):
        """ensures preshared key is at least 2048 characters in lenth
        """
        multiple = 2048 / len(preshared_key)
        return preshared_key * multiple

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
