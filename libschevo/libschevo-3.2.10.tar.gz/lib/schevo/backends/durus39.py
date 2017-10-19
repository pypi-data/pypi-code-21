"""Durus backend."""

# Copyright (c) 2001-2009 ElevenCraft Inc.
# See LICENSE for details.

import os
import sys

# Set Durus logging level before importing rest of Durus.
from durus.logger import logger
from logging import DEBUG
logger.setLevel(DEBUG)

from durus.btree import BTree
from durus.connection import Connection
from durus.error import ConflictError
from durus.file_storage import FileStorage
from durus.persistent_dict import PersistentDict
from durus.persistent_list import PersistentList

import xdserver.client

from schevo.error import DatabaseFileLocked

from backend_test_classes import (
    Durus_TestMethods_CreatesDatabase,
    Durus_TestMethods_CreatesSchema,
    Durus_TestMethods_EvolvesSchemata,
#     Xdserver_TestMethods_CreatesDatabase,
#     Xdserver_TestMethods_CreatesSchema,
#     Xdserver_TestMethods_EvolvesSchemata,
    )

__all__ = ['DurusBackend', 'XdserverBackend']

if sys.platform == 'win32':
    import pywintypes
    FileLockedError = pywintypes.error
else:
    FileLockedError = IOError


def _random_filename():
    f = File(prefix='schevodurus')
    n = f.get_name()
    f.close()
    return n

DEFAULT_CACHE_SIZE = 100000


class DurusBackend(object):
    """Schevo backend that directly uses Durus 3.9.

    NOTE: A Durus connection should be used by a process or thread for
    only one Schevo database instance, and should not be used for
    other purposes.  Create a new Durus connection instance for each
    Schevo database instance.
    """


    description = __doc__.splitlines()[0].strip()
    backend_args_help = """
    Use "durus:///:temp:" for a temporary file with a random name.

    cache_size=%d(int)
        Maximum number of objects to keep in the cache.

    storage=None (durus.storage.Storage instance)
        An existing Durus storage instance to use.
    """ % DEFAULT_CACHE_SIZE

    __test__ = False

    BTree = BTree
    PDict = PersistentDict
    PList = PersistentList

    conflict_exceptions = (ConflictError,)

    TestMethods_CreatesDatabase = Durus_TestMethods_CreatesDatabase
    TestMethods_CreatesSchema = Durus_TestMethods_CreatesSchema
    TestMethods_EvolvesSchemata = Durus_TestMethods_EvolvesSchemata

    def __init__(self,
                 database,
                 cache_size=DEFAULT_CACHE_SIZE,
                 storage=None,
                 ):
        if database == ':temp:':
            database = _random_filename()
        self.database = database
        self.cache_size = cache_size
        self.storage = storage
        self.is_open = False
        self.open()

    @classmethod
    def usable_by_backend(cls, filename):
        """Return (`True`, *additional backend args*) if the named
        file is usable by this backend, or `False` if not."""
        # Get first 128 bytes of file.
        f = open(filename, 'rb')
        try:
            try:
                header = f.read(128)
            except IOError:
                if sys.platform == 'win32':
                    raise DatabaseFileLocked()
                else:
                    raise
        finally:
            f.close()
        # Look for Durus shelf storage signature and
        # durus module signature.
        if 'durus.persistent_dict' in header:
            if header[:7] == 'SHELF-1':
                return (True, {})
        return False

    @property
    def has_db(self):
        """Return `True` if the backend contains a Schevo database."""
        return self.get_root().has_key('SCHEVO')

    def close(self):
        """Close the underlying storage (and the connection if
        needed)."""
        self.storage.close()
        self.is_open = False

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def get_root(self):
        """Return the backend's `root` object."""
        return self.conn.get_root()

    def open(self):
        """Open the underlying storage based on initial arguments."""
        if not self.is_open:
            # Find or create storage.
            if self.storage is None:
                try:
                    self.storage = FileStorage(self.database)
                    self.storage.shelf.file.obtain_lock()
                except FileLockedError, e:
                    print e
                    raise DatabaseFileLocked()
            # Connect to storage.
            self.conn = Connection(
                self.storage, cache_size=self.cache_size)
            self.is_open = True

    def pack(self):
        """Pack the underlying storage."""
        self.conn.pack()

    def rollback(self):
        """Abort the current transaction."""
        self.conn.abort()


class XdserverBackend(DurusBackend):
    """Schevo backend that directly uses Xdserver 3.9."""

    description = __doc__.splitlines()[0].strip()
  
    __test__ = False

    BTree = BTree
    PDict = PersistentDict
    PList = PersistentList

    conflict_exceptions = (ConflictError,)

#     TestMethods_CreatesDatabase = Xdserver_TestMethods_CreatesDatabase
#     TestMethods_CreatesSchema = Xdserver_TestMethods_CreatesSchema
#     TestMethods_EvolvesSchemata = Xdserver_TestMethods_EvolvesSchemata

    def __init__(self,
                 database,
                 cache_size=DEFAULT_CACHE_SIZE,
                 host=xdserver.client.DEFAULT_HOST,
                 port=xdserver.client.DEFAULT_PORT,
                 client=None,
                 ):
        self.database = database
        self.cache_size = cache_size
        self.host = host
        self.port = port
        self.client = client
        self.is_open = False
        self.open()
        
        self.backend_args_help = """
    cache_size=%d(int)
        Maximum number of objects to keep in the cache.

    client=None (xdserver.client.Client instance)
        An existing client connection to use; overrides host and port in URL.
    """ % DEFAULT_CACHE_SIZE

    @classmethod
    def usable_by_backend(cls, filename):
        """Return (`True`, *additional backend args*) if the named
        file is usable by this backend, or `False` if not."""
        return False

    @property
    def has_db(self):
        """Return `True` if the backend contains a Schevo database."""
        return self.get_root().has_key('SCHEVO')

    def close(self):
        """Close the underlying storage (and the connection if
        needed)."""
        self.storage.close()
        self.is_open = False

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def get_root(self):
        """Return the backend's `root` object."""
        return self.conn.get_root()

    def open(self):
        """Open the underlying storage based on initial arguments."""
        if not self.is_open:
            # Find or create storage.
            if self.client is not None:
                self.storage = self.client.storage(self.database)
            elif None not in (self.host, self.port):
                self.client = xdserver.client.Client(self.host, self.port)
                self.storage = self.client.storage(self.database)
            # Connect to storage.
            self.conn = Connection(
                self.storage, cache_size=self.cache_size)
            self.is_open = True

    def pack(self):
        """Pack the underlying storage."""
        self.conn.pack()

    def rollback(self):
        """Abort the current transaction."""
        self.conn.abort()
