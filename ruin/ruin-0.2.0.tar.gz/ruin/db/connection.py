# -*- coding: utf-8 -*-

import os

from .mongo_proxy import get_mongo_proxy


class BaseConnection:
    """
    This takes care of connecting to db
    """

    DEFAULT_DB_NAME = 'db'

    @classmethod
    def init(cls, *args, **kwargs):
        """
        Setting up names for multiple db connections

        :param args:
            If provided, we expect single argument with name of the database

        :param kwargs:
            Possible to use only if args are unused
        """

        if args and len(args) == 1 and not kwargs:
            cls.configs = {cls.DEFAULT_DB_NAME: args[0]}
        elif args and kwargs or len(args) > 1:
            raise ValueError('Bad parameters. Use one arg or kwargs.')
        else:
            cls.configs = kwargs

        cls._masters = {}
        cls._masters_pids = {}
        cls._slaves = {}
        cls._slaves_pids = {}

    @classmethod
    def master(cls, db_name=None):
        """
        Returns connection to master/primary

        New connection for each worker
        If worker has connection already, return that

        :param db_name:
            Name of db we are connecting to
        """
        db_name = db_name or cls.DEFAULT_DB_NAME
        pid = os.getpid()
        if cls._masters.get(db_name) is None or cls._masters_pids.get(db_name) != pid:
            cls._masters[db_name] = cls.get_connection('MASTER', db_name=db_name)
            cls._masters_pids[db_name] = pid
        # log.debug('Connection MASTER {}, {}, {}, {}'.format(db_name, os.getpid(), pid, id(cls._masters[db_name])))
        return cls._masters[db_name]

    @classmethod
    def slave(cls, db_name=None):
        """
        Returns connection to slave/secondary

        New connection for each worker
        If worker has connection already, return that

        :param db_name:
            Name of db we are connecting to
        """
        db_name = db_name or cls.DEFAULT_DB_NAME
        pid = os.getpid()
        if cls._slaves.get(db_name) is None or cls._slaves_pids.get(db_name) != pid:
            cls._slaves[db_name] = cls.get_connection('SLAVE', db_name=db_name)
            cls._slaves_pids[db_name] = pid
        # log.debug('Connection SLAVE {}, {}, {} , {}'.format(db_name, os.getpid(), pid, id(cls._slaves[db_name])))
        return cls._slaves[db_name]

    @classmethod
    def get_connection(cls, prefix, db_name=None):
        """
        Abstract method which really creates the connection to db

        Classes inheriting from this class must implement this method

        :param prefix:
             MASTER / SLAVE

        :param db_name:
            Name of db we are connecting to
        """
        raise NotImplementedError()


class Connection(BaseConnection):
    """
    Create connection to MongoDB
    """

    read_prefs = {
        'MASTER': 'primary',
        'SLAVE': 'secondaryPreferred',
    }

    @classmethod
    def get_connection(cls, prefix, db_name=None):
        """
        Returns connction to master or slave - depending on prefix

        :param prefix:
            MASTER / SLAVE

        :param db_name:
            Name of db we are connecting to

        :return:
            Connection to db

        :rtype:
            :class:`mongo_proxy.MongoProxy`
        """
        return get_mongo_proxy(cls.configs[db_name or cls.DEFAULT_DB_NAME], client_kwargs={'readPreference': cls.read_prefs[prefix]})


class DbResources:
    """
    Crate for encapsulating resources neede for DB connection

    If you add new type of database, just add resources (cursor for MySql for example)
    """
    connection = None

    def __init__(self, connection=None):
        self.connection = connection
