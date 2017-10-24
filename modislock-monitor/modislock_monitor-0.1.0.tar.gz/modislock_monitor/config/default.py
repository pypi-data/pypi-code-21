# coding: utf-8

import os


class Config(object):
    """Base config class

    """
    # Debugging output
    DEBUG = False

    MONITOR_SYSTEMD = 'modis-monitor'

    # Version
    MONITOR_VERSION = 0.1

    # Number of max readers
    MAX_SLAVES = 4

    # Root path of project
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://modismon:l3j4lkjlskjd@localhost/modislock"
    SQLALCHEMY_POOL_RECYCLE = 600
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Python version check
    REQUIRED_PYTHON_VER = (3, 5, 0)

    # Celery
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    RESET_PIN = 23
    STATUS_PIN = 24
    READER_PIN = {'READER1': 17, 'READER2': 18, 'READER3': 27, 'READER4': 22}
    DOOR_PIN = {'DOOR1': 20, 'DOOR2': 21}
    SERIAL_PORT = {'RPI_PORT': '/dev/ttyAMA0', 'PC_PORT': 'loop://'}

    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'modislock@gmail.com'
    MAIL_PASSWORD = 'mypassword'
    MAIL_DEFAULT_SENDER = 'modislock@gmail.com'
    MAIL_SUBJECT_PREFIX = 'Modis Lock:'