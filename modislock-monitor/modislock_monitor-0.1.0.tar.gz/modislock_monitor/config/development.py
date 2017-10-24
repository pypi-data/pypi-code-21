# coding: utf-8
from .default import Config


class DevelopmentConfig(Config):
    # App config
    DEBUG = True

    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://modismon:l3j4lkjlskjd@127.0.0.1/modislock"
    SQLALCHEMY_ECHO = True

