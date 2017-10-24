# encoding: utf-8

import binascii
import codecs
import re

# Encryption
from Crypto.Cipher import AES
from yubico_client import Yubico
from yubico_client.yubico_exceptions import InvalidClientIdError
from yubico_client.yubico_exceptions import InvalidValidationResponse
from yubico_client.yubico_exceptions import SignatureVerificationError
from yubico_client.yubico_exceptions import StatusCodeError

# Database
from .base import BaseValidator
from modislock_monitor.database import OtpKey, OtpCloudService, Database
from sqlalchemy.exc import OperationalError, IntegrityError, InternalError

# Logging
from modislock_monitor.extensions import log


class OTPValidate(BaseValidator):
    """OTP Validation

    Main OTP validation object. Performs local and remote OTP validation.

    """
    PROTOCOL = 'OTP'
    _CRC_OK_RESIDUAL = 0xf0b8

    def __init__(self):
        self.__user_id = None

    def _mod_hex_decode(self, string):
        """MOD Hex decoding

        :param str string:
        :returns: bytes decoded from string

        """
        modhex = ''.join(dict([('cbdefghijklnrtuv'[i],
                                '0123456789abcdef'[i]) for i in range(16)]).get(chr(j), '?') for j in range(256))
        return bytes.fromhex(string.translate(modhex))

    @staticmethod
    def _crc(data):
        """CRC Check

        :param bytearry data:
        :returns: int CRC number
        """
        crc = 0xffff
        for b in data:
            crc ^= (int(b) & 0xff)
            for j in range(0, 8):
                n = crc & 1
                crc >>= 1
                if n != 0:
                    crc ^= 0x8408
        return crc

    @property
    def protocol(self):
        """Protocol Name

        :returns: Protocol name

        """
        return self.PROTOCOL

    def validate(self, key1=None, key2=None):
        """Validates the OTP Key

        :param bytearray key1: On first validation this key is used
        :param bytearray key2: This key is the response to the secret key
        :returns: result of query, challenge if needed, user id of person who owns the key

        """
        result = self.VALIDATION_NOT_FOUND

        # Check length of key.
        if (len(key1) <= 32) or (len(key1) > 48):
            result = self.VALIDATION_ERROR
            return (result, None), None

        # Match the userid and token from OTP string
        match = re.search('([cbdefghijklnrtuv]{0,16})([cbdefghijklnrtuv]{32})', str(key1, 'utf-8'))
        userid, token = match.groups()

        with Database() as db:
            query = db.session.query(OtpKey)\
                .filter(OtpKey.key == userid)\
                .first()

            if query is None:
                return (result, None), None
            else:
                self.__user_id = query.user_id

            if not query.enabled:
                result = self.VALIDATION_DENIED
                return (result, None), self.__user_id

            if query.remote_server:
                """
                Yubico Client validation, uses YubicoClient version 1.9.1 and above. Expects string for otp key.
                """
                cloud_query = db.session.query(OtpCloudService) \
                    .filter(OtpCloudService.otp_key_key == userid) \
                    .first()

                if cloud_query is None:
                    result = self.VALIDATION_DENIED
                else:
                    client = Yubico(cloud_query.yubico_user_name, cloud_query.yubico_secret_key)

                    try:
                        valid_key = client.verify(key1.decode())
                    except StatusCodeError as e:
                        result = self.VALIDATION_ERROR
                    except InvalidClientIdError as e:
                        result = self.VALIDATION_ERROR
                    except InvalidValidationResponse as e:
                        result = self.VALIDATION_ERROR
                    except SignatureVerificationError as e:
                        result = self.VALIDATION_ERROR
                    else:
                        result = self.VALIDATION_OK if valid_key is True else self.VALIDATION_DENIED
            else:
                """
                Local server validation happens here
                """
                aes = AES.new(bytes.fromhex(query.aeskey), AES.MODE_ECB)
                plaintext = codecs.encode(aes.decrypt(self._mod_hex_decode(token)), 'hex_codec')

                counter = int(plaintext[14:16] + plaintext[12:14] + plaintext[22:24], 16)
                time = int(plaintext[20:22] + plaintext[18:20] + plaintext[16:18], 16)
                private_identity = plaintext[:12].decode('utf_8')
                crc = self._crc(binascii.unhexlify(plaintext[:32]))

                if (query.private_identity != private_identity) or (crc != self._CRC_OK_RESIDUAL) or \
                        (query.time >= time and (query.counter >> 8) == (counter >> 8)):
                    result = self.VALIDATION_DENIED
                else:
                    result = self.VALIDATION_OK
                    query.counter = counter
                    query.time = time

                    try:
                        db.session.commit()
                    except (OperationalError, IntegrityError, InternalError) as e:
                        log.debug('Unable to commit otp key update: {}'.format(e.args[1]))
                        db.session.rollback()
                        result = self.VALIDATION_ERROR

        return (result, None), self.__user_id
