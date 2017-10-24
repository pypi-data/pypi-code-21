# encoding: utf-8

from struct import unpack

import onetimepass as otp

from .base import BaseValidator
from modislock_monitor.database import TotpKey, Database


class TOTPValidate(BaseValidator):
    """TOTP Validation

    This validator is used to validate PIN codes only.

    """
    PROTOCOL = 'TOT'

    def __init__(self):
        self.__user_id = None

    @property
    def protocol(self):
        """Name of Protocol

        :returns: Protocol name

        """
        return self.PROTOCOL

    def validate(self, key1=None, key2=None):
        """Validate the TOTP Key

        :param bytearray key1: On first validation this key is used
        :param bytearray key2: This key is the response to the secret key
        :returns: result of query, challenge if needed, user id of person who owns the key

        """
        result = BaseValidator.VALIDATION_NOT_FOUND

        if key2 is None:  # First validation
            count = '>' + str(len(key1)) + 'B'  # Get the count of digits and then produce the fmt
            keycode = int(''.join(map(str, unpack(count, key1))))  # Cnvt tuple to str then int

            with Database() as db:
                query = db.session.query(TotpKey).filter(TotpKey.key == keycode).first()

                if query is not None:
                    self.__user_id = query.user_id
                    result = BaseValidator.VALIDATION_FIRST
        else:  # Second validation of secret
            with Database() as db:
                query = db.session.query(TotpKey).filter(TotpKey.user_id == self.__user_id).first()

                password = otp.get_totp(query.secret)
                count = '>' + str(len(key2)) + 'B'  # Get the count of digits and then produce the fmt
                keycode = int(''.join(map(str, unpack(count, key2))))  # Cnvt tuple to str then int

                result = BaseValidator.VALIDATION_OK if password == keycode else BaseValidator.VALIDATION_DENIED

        return (result, None), self.__user_id
