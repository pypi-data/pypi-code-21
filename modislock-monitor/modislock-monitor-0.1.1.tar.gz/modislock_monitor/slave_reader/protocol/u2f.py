# encoding: utf-8

import os

from struct import unpack

# U2F Server Helpers
from hashlib import sha256
from base64 import urlsafe_b64decode, urlsafe_b64encode
import six
import re
import struct
from binascii import a2b_hex
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_der_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

# Database
from .base import BaseValidator
from modislock_monitor.database import U2fKey, Database
from sqlalchemy.exc import OperationalError, IntegrityError, InternalError

# Logging
from modislock_monitor.extensions import log

# String
from string import Template


challenge_tmp = Template('{"typ":"navigator.id.getAssertion","challenge":"$challenge","cid_pubkey":{"kty":"EC","crv":"P-256","x":"$x","y":"$y"},"origin":"$origin"}')


BASE64URL = re.compile(br'^[-_a-zA-Z0-9]*=*$')


def key_decode(data):
    """Key Decoding


    :param str data:
    :returns: base 64 decoded string

    """
    if isinstance(data, six.text_type):
        data = data.encode('ascii')
    if not BASE64URL.match(data):
        raise ValueError('Invalid character(s)')
    data += b'=' * (-len(data) % 4)
    return urlsafe_b64decode(data)


def key_encode(data):
    """Key Encoding

    :param str data: Encodes string into base 64
    :returns: base 64 encoded string

    """
    if isinstance(data, six.text_type):
        data = data.encode('ascii')
    return urlsafe_b64encode(data).replace(b'=', b'').decode('ascii')


class U2FValidate(BaseValidator):
    """U2F Validator

    """
    PROTOCOL = 'U2P'
    PUB_KEY_DER_PREFIX = a2b_hex('3059301306072a8648ce3d020106082a8648ce3d030107034200')

    def __init__(self):
        self.__user_id = None
        self.__request = dict()

    @property
    def protocol(self):
        """Protocol Name

        :returns: Protocol name

        """
        return self.PROTOCOL

    def validate(self, key1=None, key2=None):
        """Validates U2F

        :param bytearray key1: On first validation this key is used
        :param bytearray key2: This key is the response to the secret key
        :returns: result of query, challenge if needed, user id of person who owns the key

        """
        result = self.VALIDATION_NOT_FOUND
        request = None

        if key2 is None:
            count = '>' + str(len(key1)) + 'B'  # Get the count of digits and then produce the fmt
            keycode = int(''.join(map(str, unpack(count, key1))))  # Cnvt tuple to str then int

            with Database() as db:
                query = db.session.query(U2fKey).filter(U2fKey.key == keycode).first()

                if query is not None:
                    self.__user_id = query.user_id

                    if not query.enabled:
                        result = self.VALIDATION_DENIED
                    else:
                        # App ID
                        with open('/etc/hostname', 'r') as f:
                            s = f.read()
                        app_id = 'https://' + s.strip('\n') + '.local'

                        # Header
                        header = bytes([0x00, 0x02, 0x03, 0x00, 0x00, 0x00, 0x81,])
                        # Challenge
                        pub_key = key_decode(query.public_key)
                        x = key_encode(pub_key[1:33])
                        y = key_encode(pub_key[33:])
                        challenge = key_encode(os.urandom(32))
                        req_challenge = challenge_tmp.substitute(challenge=challenge,
                                                                 x=x,
                                                                 y=y,
                                                                 origin=app_id)
                        self.__request['challenge'] = sha256(req_challenge.encode('utf-8')).digest()
                        # App
                        self.__request['app_id'] = sha256(app_id.encode('utf-8')).digest()
                        # Handle
                        try:
                            self.__request['handle'] = key_decode(query.handle)
                        except ValueError:
                            result = self.VALIDATION_ERROR
                        else:
                            # Sign request
                            request = bytearray()
                            request.extend(header)
                            request.extend(self.__request['challenge'])
                            request.extend(self.__request['app_id'])
                            request.extend(bytes([len(self.__request['handle'])]))
                            request.extend(self.__request['handle'])
                            request.extend(bytes([0x00, 0x00]))

                            self.__request['publicKey'] = key_decode(query.public_key)
                            result = self.VALIDATION_FIRST
                    return (result, request), self.__user_id
                else:
                    return (result, None), self.__user_id
        else:
            if len(key2) < 77:
                result = self.VALIDATION_ERROR
                return (result, None), self.__user_id
            # Should already be in bytearray, but just in case
            buf = bytearray(key2)
            # User Presence
            user_presence = buf.pop(0)
            # Counter
            counter = struct.unpack('>I', buf[:4])[0]
            del buf[:4]
            # Signature
            signature = bytes(buf[:-2])
            # Status
            status = buf[-2:]

            try:
                pubkey = load_der_public_key(self.PUB_KEY_DER_PREFIX + self.__request['publicKey'], default_backend())
            except Exception:
                log.error('Loading of public key for U2F failed')
                result = self.VALIDATION_ERROR
            else:
                verifier = pubkey.verifier(signature, ec.ECDSA(hashes.SHA256()))
                verifier.update(self.__request['app_id'] +
                                six.int2byte(user_presence) +
                                struct.pack('>I', counter) +
                                self.__request['challenge'])
                try:
                    verifier.verify()
                except InvalidSignature:
                    result = self.VALIDATION_DENIED
                else:
                    with Database() as db:
                        query = db.session.query(U2fKey).filter(U2fKey.user_id == self.__user_id).first()
                        query.counter = counter

                        try:
                            db.session.commit()
                        except (OperationalError, IntegrityError, InternalError) as e:
                            db.session.rollback()
                            log.debug('Unabled to update U2F table: {}'.format(e.args[1]))
                            result = self.VALIDATION_ERROR
                        else:
                            result = self.VALIDATION_OK
            return (result, None), self.__user_id
