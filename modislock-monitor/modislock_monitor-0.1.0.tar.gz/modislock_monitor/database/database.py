# coding: UTF-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Configuration
from ..extensions import mon_config


config = mon_config
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=config.DEBUG,
                       pool_pre_ping=True,
                       pool_recycle=3600,
                       pool_size=5)
session_maker = sessionmaker(bind=engine)


class Database(object):
    """Database session

    Holds the common session used in all database transactions
    """
    def __init__(self):
        self._session = scoped_session(session_maker)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.remove()

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        self._session = session

# class Database(object):
#     """Database session
#
#     Holds the common session used in all database transactions
#     """
#     def __init__(self):
#         self.connection_string = mon_config.SQLALCHEMY_DATABASE_URI
#         self.session = None
#
#     def __enter__(self):
#         engine = create_engine(self.connection_string, echo=mon_config.DEBUG)
#         Session = sessionmaker()
#         self.session = Session(bind=engine)
#         return self
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.session.close()
#
