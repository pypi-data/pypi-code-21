# coding: utf-8
from .default import Config


class ProductionConfig(Config):
    # Db config
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://modismon:l3j4lkjlskjd@localhost/modislock"
    SQLALCHEMY_ECHO = False