# encoding: utf-8

from struct import unpack
from .base import BaseValidator
from modislock_monitor.database import PinKey, Database


class PINValidate(BaseValidator):
    """PIN Validator

    This validator is used to validate PIN codes only.

    """
    PROTOCOL = 'PIN'

    def __init__(self):
        self.__user_id = None

    @property
    def protocol(self):
        """Protocol of validator

        :returns: Protocol name

        """
        return self.PROTOCOL

    def validate(self, key1=None, key2=None):
        """Validates the key

        :param bytearray key1: On first validation this key is used
        :param bytearray key2: This key is the response to the secret key
        :returns: result of query, challenge if needed, user id of person who owns the key

        """
        count = '>' + str(len(key1)) + 'B'  # Get the count of digits and then produce the fmt
        keycode = int(''.join(map(str, unpack(count, key1))))  # Cnvt tuple to str then int

        with Database() as db:
            query = db.session.query(PinKey).filter(PinKey.key == keycode).first()

            if query is None:
                result = self.VALIDATION_NOT_FOUND
            else:
                result = self.VALIDATION_OK if query.enabled == 1 else self.VALIDATION_DENIED
                self.__user_id = query.user_id

        return (result, None), self.__user_id
