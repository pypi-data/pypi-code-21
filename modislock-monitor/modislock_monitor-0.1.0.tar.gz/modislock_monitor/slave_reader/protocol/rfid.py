# encoding: utf-8

from binascii import b2a_hex

from .base import BaseValidator
from modislock_monitor.database import RfidKey, Database


class RFIDValidate(BaseValidator):
    """RFID Validator

    Validates RFID keys

    """
    PROTOCOL = 'RFID'

    def __init__(self):
        self.__user_id = None

    @property
    def protocol(self):
        """Protocol Name

        :returns: Protocol name

        """
        return self.PROTOCOL

    def validate(self, key1=None, key2=None):
        """Validates RFID Key

        :param bytearray key1: On first validation this key is used
        :param bytearray key2: This key is the response to the secret key
        :returns: result of query, challenge if needed, user id of person who owns the key

        """
        keycode = b2a_hex(key1)

        with Database() as db:
            query = db.session.query(RfidKey).filter(RfidKey.key == keycode).first()

            if query is None:
                result = self.VALIDATION_NOT_FOUND
            else:
                result = self.VALIDATION_OK if query.enabled is True else self.VALIDATION_DENIED
                self.__user_id = query.user_id

        return (result, None), self.__user_id
