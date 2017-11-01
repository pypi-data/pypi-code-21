# -*- coding: utf-8 -*-

import logging as log
from functools import wraps
from time import sleep

# from pymongo.errors import ServerSelectionTimeoutError, NotMasterError  # pymongo 3+

from .connection import Connection, DbResources


def transaction(db_name=None, master_=True):
    """
    This function returns decorator that provides access to db connection in decorated method (or function)

    :param db_name:
        Name of db we are connecting to

    :param master_:
        Flag to create either master or slave
    :type master_:
        bool
    """

    def decorator(function):

        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            # except (ServerSelectionTimeoutError, NotMasterError) as exc:  # pymongo 3+
            except Exception as exc:  # pylint: disable=broad-except
                log.fatal('MONGO FATAL ERROR: %s', repr(exc))
                sleep_seconds = 0.1
                log.info('SLEEPING FOR %s SECONDS BEFORE RETRY', sleep_seconds)
                sleep(sleep_seconds)
                return function(*args, **kwargs)

        @wraps(function)
        def method_wrapper(self, *args, **kwargs):
            """
            This is used when decorating method inside class
            """
            _db_name = db_name or getattr(self, 'DATABASE_NAME', None)
            self.connection = Connection.master(_db_name) if master_ else Connection.slave(_db_name)
            return wrapper(self, *args, **kwargs)

        @wraps(function)
        def function_wrapper(*args, **kwargs):
            """
            This is used when decorating function
            """
            connection = Connection.master(db_name) if master_ else Connection.slave(db_name)
            return wrapper(DbResources(connection=connection), *args, **kwargs)
        return method_wrapper if callable(function) else function_wrapper
    return decorator

master = transaction(master_=True)  # pylint: disable=invalid-name
slave = transaction(master_=False)  # pylint: disable=invalid-name
