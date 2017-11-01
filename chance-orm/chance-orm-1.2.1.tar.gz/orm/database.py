#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 02.02.2017
"""Database Connection
"""
import logging

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from orm.base import DBBase


LOGGER = logging.getLogger(__name__)
BASE = declarative_base(cls=DBBase)


class DBSessionMaker(object):
    """An instance of sessionmaker.
    """
    def __init__(self, user, password, host, port, database, rollback=False):
        """Initialize connection with given config filename.

        Initialize the ``engine`` with user, password, host, port
        and database. If any exception raised by ``create_engine`` will be
        logged and no engine will be created. If the exception is created
        successfully, a ``metadata`` is created with ``engine`` to create a
        ``sessionmaker`` which can create ``session`` later

        Args:
            user: a str
            password: a str
            host: a str
            port: a str
            database: a str
            rollback: indicating whether rollback after closed, default False.
        """
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._database = database
        self.metadata = None
        self.connection = None
        self.trans = None
        self.session_maker = None
        self._rollback = rollback

    def connect(self):
        """Connect database
        """
        try:
            engine = create_engine(
                "mysql+mysqldb://{0}:{1}@{2}:{3}/{4}?charset=utf8".format(
                    self._user, self._password, self._host, self._port,
                    self._database,
                ),
                pool_recycle=3600, encoding="utf8",
            )
        except Exception, e:
            LOGGER.exception(e)
        else:
            LOGGER.info("Successfully Build Connection")
            self.metadata = MetaData(bind=engine)
            self.connection = engine.connect()
            self.trans = self.connection.begin()
            self.session_maker = sessionmaker(bind=self.connection)

    def save(self):
        """Save and commit transaction and connection
        """
        self.trans.commit()
        self.connection.close()

    def rollback(self):
        """Rollback transaction and close connection
        """
        self.trans.rollback()
        self.connection.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is None and not self._rollback:
            self.save()
            LOGGER.debug("Connection exit in normal")
        elif exc_value is not None:
            self.rollback()

            LOGGER.exception(exc_value)
            raise exc_value
        else:
            self.rollback()
            LOGGER.debug("Connection rollback")


class DBSession(object):
    """Encapsulate the session to be used in with statement.
    """
    def __init__(self, session_maker):
        """Initialize class with given session maker.

        Args:
            session_maker: sessionmaker
        """
        self.session_maker = session_maker

    def __enter__(self):
        """Method called before get into the with clause.

        Return the session created by given session_maker.

        Args:
            config_file: a ``String`` representing the config filename.
        """
        self._session = self.session_maker()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Method called when exit the with clause or exception raised.

        Commit the session if no exception raised, or rollback.

        Args:
            exc_type: a ``class`` representing the type of raised Exception.
            exc_val: raised exception.
            exc_tb: the traceback of raised exception.

        Raised:
            Any exceptions raised in the with clause.
        """
        if exc_type is None:
            LOGGER.debug("Session exit in normal")
            self._session.commit()
        else:
            LOGGER.error("Session exit with exception!")
            LOGGER.exception(exc_val)

            self._session.rollback()
            self._session.close()
            raise exc_val
        self._session.close()
