"""icemicro module
"""
import base64
import hashlib

from iceman.crypto_strategies.strategy import Strategy

from icecore import icecore

class Icemicro(Strategy):
    """Icecore Strategy implementation

    :param preshared_key: symmetric encryption key
    :type preshared_key: str
    """
    def __init__(self, preshared_key):
        key_md5 = hashlib.md5(preshared_key).hexdigest()
        encoded_key = base64.b64encode(key_md5)
        cipher_suite = icecore.ICEBlockCipher(encoded_key) #pylint: disable=maybe-no-member
        self.cipher_suite = cipher_suite

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
