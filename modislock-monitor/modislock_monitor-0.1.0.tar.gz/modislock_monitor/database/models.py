# coding: utf-8

from sqlalchemy import Column, ForeignKey, Integer, Unicode, Enum, TIMESTAMP, Boolean, TIME
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User table

    Defines login information but is also referenced in all available protocols

    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Unicode(50), nullable=False)
    last_name = Column(Unicode(50), nullable=False)
    email = Column(Unicode(50), unique=True)
    password = Column(Unicode(128))
    is_admin = Column(Boolean, nullable=False, default=0)

    # Relationships
    rules = relationship('Rules', cascade='all, delete-orphan')
    pin_key = relationship('PinKey', cascade='all, delete-orphan')
    rfid_key = relationship('RfidKey', cascade='all, delete-orphan')
    event = relationship('Events', cascade='all, delete-orphan')
    otp_key = relationship('OtpKey', cascade='all, delete-orphan')
    u2f_key = relationship('U2fKey', cascade='all, delete-orphan')
    hotp_key = relationship('HotpKey', cascade='all, delete-orphan')

    def __repr__(self):
        return "User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, " \
               "password={self.password}, email={self.email}, is_admin={self.is_admin})".format(self=self)


class Rules(Base):
    """Individual key rules

    """
    __tablename__ = 'rules'

    id_rules = Column(Integer, primary_key=True, autoincrement=True)
    days = Column(TINYINT(unsigned=True))
    start_time = Column(TIME)
    end_time = Column(TIME)
    readers = Column(TINYINT(unsigned=True))
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "Rules(id_rules={self.id_rules}, days={self.days}, " \
               "start_time={self.start_time}, end_time={self.end_time}, " \
               "readers={self.readers})".format(self=self)


class Events(Base):
    __tablename__ = 'events'

    id_event = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    event_time = Column(TIMESTAMP, default=func.now(), nullable=False)
    event_type = Column(Enum('USER_CREATED', 'ACCESS', 'DENIED'), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reader_settings_id_reader = Column(Integer, ForeignKey('reader_settings.id_reader'),
                                       default=0,
                                       nullable=False)
    reader_settings = relationship('ReaderSettings')

    def __repr__(self):
        return "Events(id_event={self.id_event}, event_time={self.event_time}, event_type={self.event_type}, " \
               "user_id={self.user_id}, reader_settings_id_reader={self.reader_settings_id_reader})".format(self=self)


class PinKey(Base):
    """PinCode

    Table holds the protocol PIN. Is used for pin codes and references the user they are assigned to.

    """
    __tablename__ = 'pin_key'

    key = Column(Integer, primary_key=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "PinKey(key={self.key}, enabled={self.enabled}, created_on={self.created_on}," \
               " user_id={self.user_id})".format(self=self)


class RfidKey(Base):
    """RFIDCode

    Table holds the protocol for RFID tags. References back to user they are assigned to.

    """
    __tablename__ = 'rfid_key'

    key = Column(Unicode(128), primary_key=True, unique=True, nullable=False)
    enabled = Column(Boolean, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "RfidKey(key={self.key}, enabled={self.enabled}, created_on={self.created_on}," \
               " user_id={self.user_id})".format(self=self)


class OtpKey(Base):
    __tablename__ = 'otp_key'

    key = Column(Unicode(16), primary_key=True, nullable=False, index=True)
    private_identity = Column(Unicode(16), nullable=False)
    aeskey = Column(Unicode(32), nullable=False)
    enabled = Column(Boolean, nullable=False, default=1)
    counter = Column(Integer, nullable=False, default=1)
    time = Column(Integer, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    remote_server = Column(Boolean, default=0)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    # Relationships
    otp_cloud_service = relationship('OtpCloudService', cascade='all, delete-orphan')

    def __repr__(self):
        return "OtpKey(key={self.key}, private_identity={self.private_identity}, " \
               "aeskey={self.aeskey}, enabled={self.enabled}, counter={self.counter}, " \
               "time={self.time}, remote_server={self.remote_server}, created_on={self.created_on}, " \
               "user_id={self.user_id})".format(self=self)


class OtpCloudService(Base):
    __tablename__ = 'otp_cloud_service'

    cloud_id = Column(Integer, primary_key=True, autoincrement=True)
    yubico_user_name = Column(Unicode(45), nullable=True)
    yubico_secret_key = Column(Unicode(45), nullable=True)
    # Foreign keys
    otp_key_key = Column(Unicode(16), ForeignKey('otp_key.key'), nullable=False)

    def __repr__(self):
        return "OtpCloudService(cloud_id={self.cloud_id}, yubico_user_name={self.yubico_user_name}, " \
               "yubico_secret_key={self.yublico_secret_key}, " \
               "otp_key_key={self.otp_key_key})".format(self=self)


class TotpKey(Base):
    __tablename__ = 'totp_key'

    key = Column(Integer, primary_key=True, unique=True)
    secret = Column(Unicode(40))
    period = Column(TINYINT, nullable=False, default=30)
    enabled = Column(Boolean, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "TtopKey(key={self.key}, secret={self.secret}, " \
               "period={self.counter}, enabled={self.enabled}, " \
               "created_on={self.created_on})".format(self=self)


class HotpKey(Base):
    __tablename__ = 'hotp_key'

    key = Column(Integer, primary_key=True, unique=True, index=True)
    secret = Column(Unicode(40))
    counter = Column(Integer, nullable=False, default=1)
    enabled = Column(Boolean, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "HtopKey(key={self.key}, secret={self.secret}, " \
               "counter={self.counter}, enabled={self.enabled}, " \
               "created_on={self.created_on})".format(self=self)


class U2fKey(Base):
    __tablename__ = 'u2f_key'

    key = Column(Integer, primary_key=True, nullable=False)
    handle = Column(Unicode(128), nullable=False, unique=True)
    public_key = Column(Unicode(128), nullable=False)
    counter = Column(Integer, nullable=False)
    transports = Column(Enum('BT', 'BLE', 'NFC', 'USB'))
    enabled = Column(Boolean, nullable=False, default=1)
    created_on = Column(TIMESTAMP, default=func.now(), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "U2fKey(key={self.key}, handle={self.handle}, public_key={self.public_key}, " \
               "counter={self.counter}, transports={self.transports}, enabled={self.enabled}, " \
               "created_on={self.created_on}, user_id={self.user_id})".format(self=self)


class ReaderSettings(Base):
    __tablename__ = 'reader_settings'

    id_reader = Column(Integer, primary_key=True)
    location_name = Column(Unicode(20), nullable=False)
    location_direction = Column(Enum('NONE', 'EXIT', 'ENTRY'), nullable=False)
    settings_id_settings = Column(Integer, ForeignKey('settings.id_settings'), nullable=False)

    def __repr__(self):
        return 'ReaderSettings(id_reader={self.id_reader}, ' \
               'location_direction={self.location_direction},' \
               'settings_id_settings={self.settings_id_settings})'.format(self=self)


class ReaderStatus(Base):
    __tablename__ = 'reader_status'

    id_status = Column(Integer, primary_key=True)
    status = Column(Enum('DISCONNECTED', 'CONNECTED', 'ERROR'), nullable=False)
    updated_on = Column(TIMESTAMP, default=func.now(), onupdate=func.now())

    reader_id_reader = Column(Integer, ForeignKey('reader_settings.id_reader'), nullable=False)

    def __repr__(self):
        return "ReaderStatus(id_status={self.id_status}, status={self.status}, updated_on={self.updated_on}, " \
               "reader_id_reader={self.reader_id_reader})".format(self=self)


class Sensors(Base):
    __tablename__ = 'sensors'

    id_sensors = Column(Integer, primary_key=True)
    name = Column(Unicode(45), unique=True, nullable=False)
    units = Column(Unicode(45), nullable=False)
    locations_id_locations = Column(Integer, ForeignKey('locations.id_locations'), nullable=False)

    # Relationships
    readings = relationship('Readings', cascade='all, delete-orphan')

    def __repr__(self):
        return "Sensors(id_sensors={self.id_sensors}, name={self.name}, units={self.units}," \
               "locations_id_locations={self.locations_id_locations})".format(self=self)


class Locations(Base):
    __tablename__ = 'locations'

    id_locations = Column(Integer, primary_key=True)
    name = Column(Unicode(45), unique=True)

    def __repr__(self):
        return "Locations(id_locations={self.id_locations}, name={self.name})".format(self=self)


class Readings(Base):
    __tablename__ = 'readings'

    id_readings = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, nullable=False, default=func.now())
    value = Column(Unicode(10), nullable=False)
    sensors_id_sensors = Column(Integer, ForeignKey('sensors.id_sensors'), nullable=False)

    def __repr__(self):
        return "Readings(id_readings={self.id_readings}, timestamp={self.timestamp}, value={self.value}," \
               "sensors_id_sensors={self.sensors_id_sensors})".format(self=self)


class Settings(Base):
    __tablename__ = 'settings'

    id_settings = Column(Integer, primary_key=True, autoincrement=True)
    settings_name = Column(Unicode(45), unique=True)
    units = Column(Unicode(45), nullable=False)
    # Foreign keys
    settings_group_name = Column(Enum('WEB', 'READERS', 'MONITOR', 'RULES'), nullable=False)

    def __repr__(self):
        return "Settings(id_settings={self.id_settings}, settings_name={self.settings_name}, " \
               "units={self.units})".format(self=self)


class SettingsValues(Base):
    __tablename__ = 'settings_values'

    id_values = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    value = Column(Unicode(45), nullable=False)

    settings_id_settings = Column(Integer, ForeignKey('settings.id_settings'), nullable=False)

    def __repr__(self):
        return "SettingsValues(id_values={self.id_values}, value={self.value}, " \
               "settings_id_settings={self.settings_id_settings})".format(self=self)
