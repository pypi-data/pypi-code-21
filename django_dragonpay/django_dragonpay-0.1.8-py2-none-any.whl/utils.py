import base64
import random
import string
from Crypto import Random
from Crypto.Cipher import AES
from hashlib import sha1, sha256

from django_dragonpay import settings


def get_dragonpay_digest(str_or_list):
    '''The DragonPay digest is a concatination of the values passed and
    the DRAGONPAY_PASSWORD, joined by a colon(":").'''

    if isinstance(str_or_list, list) or isinstance(str_or_list, tuple):
        # The given parameter is list or tuple, convert it to a valid
        # digestible message by joining it with colons
        str_or_list = ':'.join(str_or_list)

    # Append the MERCHANT_PASSWORD to the string and return the sha1 digest
    return sha1(
        str_or_list + ':' + settings.DRAGONPAY_PASSWORD).hexdigest()


# http://stackoverflow.com/a/21928790
class AESCipher(object):
    '''Cipher helper class used to encrypt and decrypt data via AES CBC.'''

    def __init__(self):
        self.bs = 32
        self.key = sha256(settings.SECRET_KEY.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(
            cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (
            self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]


def encrypt_data(message):
    cipher = AESCipher()
    return cipher.encrypt(message)


def decrypt_data(message):
    cipher = AESCipher()
    return cipher.decrypt(message)


def generate_txn_id():
    '''Generates a random transaction id.'''

    return ''.join([random.choice(
        string.hexdigits) for i in range(settings.DRAGONPAY_TXN_LENGTH)])
