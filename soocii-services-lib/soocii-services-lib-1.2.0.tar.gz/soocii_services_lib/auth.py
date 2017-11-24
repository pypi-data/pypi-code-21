import base64
import binascii
import json  # import simplejson if json not work
import time

import os
from Crypto import Random
from Crypto.Cipher import AES

blockSize = 16


def _decode_token(token, secret_key):
    # decode token by base64 and split to cipherText and iv.
    decode_string = base64.urlsafe_b64decode(token)
    cipher_text, iv = decode_string[blockSize:], decode_string[:blockSize]

    # convert the pre-defined secret from hex string.
    bin_secret = binascii.unhexlify(secret_key)

    # decrypt the encrypt string by the secret key.
    cert_aes = AES.new(bin_secret, AES.MODE_CBC, iv)
    data = cert_aes.decrypt(cipher_text)

    # PKCS#7 style unpadding
    raw = data[:-ord(data[len(data) - 1:])]

    return raw


def _generate_token(raw, secret_key):
    # determine a random IV
    iv = Random.new().read(blockSize)

    # PKCS#7 style padding
    length = blockSize - (len(raw) % blockSize)
    raw += chr(length) * length

    # convert the pre-defined secret from hex string
    bin_secret = binascii.unhexlify(secret_key)

    # encrypt the padded base string by the secret, which is different for each product.
    cert_aes = AES.new(bin_secret, AES.MODE_CBC, iv)
    cipher_text = cert_aes.encrypt(raw)

    # put iv in front of the cipher text, and encode them by base64
    token = base64.urlsafe_b64encode(iv + cipher_text)

    return token


class AccessTokenValidationFail(Exception): pass


class RefreshTokenValidationFail(Exception): pass


def _get_token_info():
    return {
        "access": {
            "secret_key": os.getenv('ACCESS_TOKEN_SECRET', 'None'),
            "age": 43200,
            "exception": AccessTokenValidationFail
        },
        "refresh": {
            "secret_key": os.getenv('REFRESH_TOKEN_SECRET', 'None'),
            "age": 604800,
            "exception": RefreshTokenValidationFail
        },
    }


def decode_access_token(token, check_timestamp=True):
    info = _get_token_info()['access']

    if not token:
        raise info["exception"]

    token = json.loads(_decode_token(token, info["secret_key"]).decode('utf-8'))

    if check_timestamp and token["timestamp"] + info["age"] < int(time.time()):
        raise info["exception"]

    return token


def generate_access_token(pid, uid, id, uuid, lang='EN-US', device_type=''):
    token = _generate_token(json.dumps({
        "pid": pid,
        "uid": uid,
        "id": id,
        "uuid": uuid,
        "timestamp": int(time.time()),
        "lang": lang,
        "device_type": device_type
    }, ensure_ascii=False), _get_token_info()["access"]["secret_key"])

    return token


def generate_refresh_token(access_token):
    token = _generate_token(json.dumps({
        "access_token": access_token,
        "timestamp": int(time.time()),
    }, ensure_ascii=False), _get_token_info()["refresh"]["secret_key"])

    return token
