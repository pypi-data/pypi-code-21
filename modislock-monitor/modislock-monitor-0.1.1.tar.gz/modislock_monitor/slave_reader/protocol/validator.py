# encoding: utf-8

# Misc
from datetime import datetime
from frozendict import frozendict
from struct import unpack_from

# Database
from modislock_monitor.database import (Database, Events, PinKey, TotpKey, U2fKey, SettingsValues, Settings)
from modislock_monitor.tasks import send_async_msg
from sqlalchemy import and_
from sqlalchemy.exc import OperationalError, IntegrityError, InternalError
from .otp import OTPValidate
from .pin import PINValidate
from .rfid import RFIDValidate
from .totp import TOTPValidate
from .u2f import U2FValidate

# Threading
from threading import Thread

# Messaging
from .messaging import Message, MailServer

# Logging
from modislock_monitor.extensions import log


class Validator(object):
    """Base Validator

    Base validation that determines the protocol to used based on request.

    """
    VALIDATORS = frozendict({"PIN": PINValidate, "OTP": OTPValidate, "RFD": RFIDValidate,
                             "U2F": U2FValidate, "TOT": TOTPValidate})

    def __init__(self, address, message):
        self.__user_id = None
        self.__slave_id = address
        self.__first_validation = True

        if isinstance(message, (bytes, bytearray)):
            protocol = str(message[:3], encoding='utf-8')
            # 1. Check to see if protocol is in valid validators dictionary
            if protocol in self.VALIDATORS:
                # 2. If pin used in first validation, find which protocol that account is associated with
                if protocol in self.VALIDATORS.keys():
                    if protocol == 'PIN':
                        # Get the count of digits and then produce the fmt
                        count = '>' + str(len(message[3:])) + 'B'
                        try:
                            keycode = int(''.join(map(str, unpack_from(count, message, 3))))  # Cnvt tuple to str then int
                        except ValueError:
                            self.__callable = None
                        else:
                            with Database() as db:
                                if db.session.query(PinKey).filter(PinKey.key == keycode).first() is not None:
                                    self.__callable = self.VALIDATORS.get('PIN')
                                elif db.session.query(TotpKey).filter(TotpKey.key == keycode).first() is not None:
                                    self.__callable = self.VALIDATORS.get('TOT')
                                elif db.session.query(U2fKey).filter(U2fKey.key == keycode).first() is not None:
                                    self.__callable = self.VALIDATORS.get('U2F')
                                else:
                                    self.__callable = None
                    else:
                        self.__callable = self.VALIDATORS.get(protocol)
                else:
                    raise KeyError
            else:
                raise TypeError

            if self.__callable is not None:
                self.__callable = self.__callable()

    def validate(self, key):
        """Validate Request

        Validates the key against the protocol class type

        :param bytearray key:
        :returns: (result, challenge) user_id

        """
        if self.__callable is not None:
            result, self.__user_id = self.__callable.validate(key1=key if self.__first_validation else None,
                                                              key2=None if self.__first_validation else key)

            if (result[0] == self.__callable.VALIDATION_OK) or (result[0] == self.__callable.VALIDATION_DENIED):
                Thread(target=self.check_global_rules, args=(result[0])).start()
                Thread(target=self.event, args=(result[0])).start()
                self.event(result[0])
                return result
            elif result[0] == self.__callable.VALIDATION_NOT_FOUND:
                return result
            elif result[0] == self.__callable.VALIDATION_FIRST:
                self.__first_validation = False
                return result
            elif result[0] == self.__callable.VALIDATION_ERROR:
                Thread(target=self.check_global_rules, args=(result[0])).start()
                return result
        else:
            return None

    @property
    def valid(self):
        """Valid Validation request

        :returns: True if validation request is of a valid protocol or False if not found

        """
        return True if self.__callable is not None else False

    @staticmethod
    def check_global_rules(result):
        """Check global key rules

        1. Check global settings for rules
        2. Check local settings for overriding rules

        """
        rules = dict()
        notify = dict()
        current_time = datetime.now()

        with Database() as db:
            query = db.session.query(Settings) \
                .join(SettingsValues, Settings.id_settings == SettingsValues.settings_id_settings) \
                .filter(and_(Settings.settings_group_name == 'RULES', Settings.settings_name.like('GLOBAL%'))) \
                .with_entities(Settings.settings_name, Settings.units, SettingsValues.value) \
                .all()

            if query is not None:
                for rule in query:
                    rules[rule[0]] = int(rule[2]) if rule[1] == 'integer' else datetime.strptime(rule[2], '%H:%M:%S')
            else:
                return

            notification = db.session.query(Settings) \
                .join(SettingsValues, Settings.id_settings == SettingsValues.settings_id_settings) \
                .filter(and_(Settings.settings_group_name == 'RULES', Settings.settings_name.like('NOTIFY%'))) \
                .with_entities(Settings.settings_name, SettingsValues.value) \
                .all()

            if notification is not None:
                for rule in notification:
                    notify[rule[0]] = True if rule[1] == 'ENABLED' else False
            else:
                return

            if notify['NOTIFY_ON_DENIED'] or notify['NOTIFY_ON_AFTER_HOURS'] or notify['NOTIFY_ON_SYSTEM_ERROR']:
                mail_svr = MailServer()
                message = Message()

                if notify['NOTIFY_ON_DENIED'] and result == 'DENIED':
                    send_async_msg.delay(message.serialized, mail_svr.serialized)

                if notify['NOTIFY_ON_AFTER_HOURS'] and result == 'ACCESS' and \
                        (current_time > rules['GLOBAL_END_TIME'] or current_time < rules['GLOBAL_START_TIME']):
                    print('check hours send notification')

                if notify['NOTIFY_ON_SYSTEM_ERROR']:
                    print('Error and notify')

    def check_user_rules(self):
        """Check individual rules

        .. note:: Not yet implemented.

        :returns:
        """
        pass

    def event(self, event_type):
        """Event logging

        Logs event to database. Event can be of type ACCESS | DENIED. Records the location, time, user id, and action

        :param str event_type:
        """
        with Database() as db:
            query = Events(user_id=self.__user_id, event_type=event_type, reader_settings_id_reader=self.__slave_id)
            db.session.add(query)

            try:
                db.session.commit()
            except (OperationalError, IntegrityError, InternalError) as e:
                db.session.rollback()
                log.debug('Commit to event table failed: {}'.format(e.args[1]))
