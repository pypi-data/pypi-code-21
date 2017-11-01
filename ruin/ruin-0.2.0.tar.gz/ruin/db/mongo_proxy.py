# -*- coding: utf-8 -*-

import time
import logging as log

import pymongo


def get_methods(*objs):
    return set(
        attr
        for obj in objs
        for attr in dir(obj)
        if not attr.startswith('_') and hasattr(getattr(obj, attr), '__call__')
    )

try:
    # will fail to import from older versions of pymongo
    from pymongo import MongoClient, MongoReplicaSetClient
except ImportError:
    MongoClient, MongoReplicaSetClient = None, None  # NOQA

EXECUTABLE_MONGO_METHODS = get_methods(
    pymongo.collection.Collection,
    pymongo.database.Database,
    pymongo.MongoReplicaSetClient,
    MongoClient,
    MongoReplicaSetClient,
    pymongo,
)


class Executable:  # pylint: disable=too-few-public-methods
    """
    Wrapper for Mongo methods, handling AutoReconnect exceptions
    """

    def __init__(self, method, logger, wait_time=None):
        self.method = method
        self.logger = logger
        self.wait_time = wait_time or 60

    def __call__(self, *args, **kwargs):
        """
        Handle AutoReconnect exception
        """
        start = time.time()
        i = 0
        while True:
            try:
                return self.method(*args, **kwargs)
            except pymongo.errors.AutoReconnect:
                end = time.time()
                delta = end - start
                if delta >= self.wait_time:
                    break
                self.logger.warning('AutoReconnecting, try {} ({} seconds)'.format(i, delta))
                time.sleep(pow(2, i))
                i += 1
        # Try one more time, but this time, if it fails, let the
        # exception bubble up to the caller.
        return self.method(*args, **kwargs)

    def __dir__(self):
        return dir(self.method)

    def __str__(self):
        return self.method.__str__()

    def __repr__(self):
        return self.method.__repr__()


class MongoProxy:  # pylint: disable=too-few-public-methods
    """
    Proxy for MongoDB connection.

    Called methods (find, insert, ..) are wrapped with :class:`Executable` so AutoReconnect exceptions are handled smoothly
    """

    def __init__(self, conn, logger=None, wait_time=None):
        """
        :param conn:
            Standard connection to db

        :param logger:
            Logger object

        :param wait_time:
            Timeout before reconnecting after AutoReconnect exception
        """
        if logger is None:
            # import logging
            # logger = logging.getLogger(__name__)
            logger = log.getLogger(__name__)

        self.conn = conn
        self.logger = logger
        self.wait_time = wait_time

    def __getitem__(self, key):
        """
        Create and get proxy for method, called with connection named `key`

        :param key:
            Connection name
        """
        item = self.conn[key]
        if hasattr(item, '__call__'):
            return MongoProxy(item, self.logger, self.wait_time)
        return item

    def __getattr__(self, key):
        """
        If `key` is name of executable method (find, insert, ..),
        this method is wrapped to instance of :class:`Executable`
        """

        attr = getattr(self.conn, key)
        if hasattr(attr, '__call__'):
            if key in EXECUTABLE_MONGO_METHODS:
                return Executable(attr, self.logger, self.wait_time)
            else:
                return MongoProxy(attr, self.logger, self.wait_time)
        return attr

    def __call__(self, *args, **kwargs):
        return self.conn(*args, **kwargs)

    def __dir__(self):
        return dir(self.conn)

    def __str__(self):
        return self.conn.__str__()

    def __repr__(self):
        return self.conn.__repr__()

    def __nonzero__(self):
        return True


def get_mongo_proxy(config, client_kwargs=None):
    """
    Returns Mongo Proxy

    :param config:
        Configi with connection details

        Must include:

        MONGO_USERNAME
        MONGO_PASSWORD
        MONGO_HOST
        MONGO_PORT
        MONGO_DBNAME

    :type config:
        dict

    :param client_kwargs:
        Additional config passed to :class:`pymongo.MongoClient` constructor during connection creation

    :type client_kwargs:
        dict
    """
    client_kwargs = client_kwargs or {}

    conn_str = 'mongodb://{}:{}@{}:{}/{}'.format(
        config['MONGO_USERNAME'],
        config['MONGO_PASSWORD'],
        config['MONGO_HOST'],
        config['MONGO_PORT'],
        config['MONGO_DBNAME'],
    )

    if config.get('MONGO_SOCKET_TIMEOUT'):
        client_kwargs['socketTimeoutMS'] = int(config['MONGO_SOCKET_TIMEOUT'])

    if config.get('MONGO_CONNECT_TIMEOUT'):
        client_kwargs['connectTimeoutMS'] = int(config['MONGO_CONNECT_TIMEOUT'])

    if config.get('MONGO_SERVER_SELECTION_TIMEOUT'):
        client_kwargs['serverSelectionTimeoutMS'] = int(config['MONGO_SERVER_SELECTION_TIMEOUT'])

    log.info('Mongo Connection: %s@%s:%s/%s %s', config['MONGO_USERNAME'], config['MONGO_HOST'], config['MONGO_PORT'], config['MONGO_DBNAME'], client_kwargs)
    client = MongoClient(conn_str, **client_kwargs)
    return MongoProxy(client[config['MONGO_DBNAME']])
