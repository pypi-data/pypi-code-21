#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os import urandom
from hashlib import sha256, sha512
from abc import abstractmethod
import abcs as session_abcs
from yosaipy2.core.utils.utils import get_logger


class AbstractSessionStore(session_abcs.SessionStore):
    """
    An abstract SessionStore implementation performs some sanity checks on
    session creation and reading and allows for pluggable Session ID generation
    strategies if desired.  The SessionStore.update and SessionStore.delete method
    implementations are left to subclasses.

    Session ID Generation
    ---------------------
    This class also allows for plugging in a SessionIdGenerator for
    custom ID generation strategies.  This is optional, as the default
    generator is probably sufficient for most cases.  Subclass implementations
    that do use a generator (default or custom) will want to call the
    generate_session_id(Session) method from within their do_create
    implementations.

    Subclass implementations that rely on the EIS data store to generate the ID
    automatically (e.g. when the session ID is also an auto-generated primary
    key), they can simply ignore the SessionIdGenerator concept
    entirely and just return the data store's ID from the do_create
    implementation.
    """

    def __init__(self):
        self._logger = get_logger()

    def create(self, session):
        session_id = self._do_create(session)
        self.verify_session_id(session_id)
        return session_id

    def read(self, session_id):
        session = self._do_read(session_id)
        if session is None:
            msg = "There is no session with id [" + str(session_id) + "]"
            raise ValueError(msg)
        return session

    @abstractmethod
    def _do_read(self, session_id):
        pass

    @abstractmethod
    def _do_create(self, session):
        pass

    @staticmethod
    def verify_session_id(session_id):
        if session_id is None:
            msg = "session_id returned from do_create implementation is None. Please verify the implementation."
            raise ValueError(msg)

    @staticmethod
    def generate_session_id():
        """
        :return: the new session instance for which an ID will be
                        generated and then assigned
        """
        return sha256(sha512(urandom(20)).digest()).hexdigest()


class MemorySessionStore(AbstractSessionStore):
    """
    Simple memory-based implementation of the SessionStore that stores all of its
    sessions in an in-memory dict.  This implementation does not page
    to disk and is therefore unsuitable for applications that could experience
    a large amount of sessions and would therefore result in MemoryError
    exceptions as the interpreter runs out of memory.  This class is *not*
    recommended for production use in most environments.

    Memory Restrictions
    -------------------
    If your application is expected to host many sessions beyond what can be
    stored in the memory available to the Python interpreter, it is highly
    recommended that you use a different SessionStore implementation using a
    more expansive or permanent backing data store.

    Instead, use a custom CachingSessionStore implementation that communicates
    with a higher-capacity data store of your choice (Redis, Memcached,
    file system, rdbms, etc).
    """

    def __init__(self):
        super(MemorySessionStore, self).__init__()
        self.sessions = {}

    def update(self, session):
        return self.store_session(session.session_id, session)

    def delete(self, session):
        try:
            self.sessions.pop(session.session_id)
        except AttributeError:
            msg = 'MemorySessionStore.delete None param passed'
            raise AttributeError(msg)
        except KeyError:
            msg = ('MemorySessionStore could not delete ', str(session.session_id),
                   'because it does not exist in memory!')
            self._logger.warning(msg)

    def store_session(self, session_id, session):
        """
        stores only if session doesn't already exist, returning the existing
        session (as default) otherwise
        """
        if session_id is None or session is None:
            msg = 'MemorySessionStore.store_session invalid param passed'
            raise ValueError(msg)

        return self.sessions.setdefault(session_id, session)

    def _do_create(self, session):
        session_id = self.generate_session_id()
        session.session_id = session_id
        self.store_session(session_id, session)
        return session_id

    def _do_read(self, session_id):
        return self.sessions.get(session_id)


class CachingSessionStore(AbstractSessionStore):
    """
    An CachingSessionStore is a SessionStore that provides a transparent caching
    layer between the components that use it and the underlying EIS
    (Enterprise Information System) session backing store (e.g.
    Redis, Memcached, filesystem, database, enterprise grid/cloud, etc).

    Yosai omits 'active sessions' related functionality, which is used in Shiro
    as a means to bulk-invalidate timed out sessions.  Rather than manually sift
    through a collection containing every active session just to find
    timeouts, Yosai lazy-invalidates idle-timeout sessions and relies on
    automatic expiration of absolute timeout within cache. Absolute timeout is
    set as the cache entry's expiration time.

    Unlike Shiro:
    - Yosai implements the CRUD operations within CachingSessionStore
    rather than defer implementation further to subclasses
    - Yosai comments out support for a write-through caching strategy
    - Yosai uses an IdentifierCollection with session caching as part of its
      caching strategy


    Write-Through Caching
    -----------------------
    Write-through caching is a caching pattern where writes to the cache cause
    writes to an underlying database (EIS). The cache acts as a facade to the
    underlying resource.

    All methods within CachingSessionStore are implemented to employ caching
    behavior while delegating cache write-through related operations
    to respective 'do' CRUD methods, which are to be implemented by subclasses:
    do_create, do_read, do_update and do_delete.

    Potential write-through caching strategies:
    ------------------------------------
    As of Postgresql 9.5, you can UPSERT session records

    Databases such as Postgresql offer what is known as foreign data wrappers
    (FDWs) that pipe data from cache to the database.

    Ref: https://en.wikipedia.org/wiki/Cache_%28computing%29#Writing_policies
    """

    def __init__(self):
        super(CachingSessionStore, self).__init__()
        self.cache_handler = None

    def _do_create(self, session):
        session_id = self.generate_session_id()
        session.session_id = session_id
        return session_id

    def create(self, session):
        """
        caches the session and caches an entry to associate the cached session
        with the subject
        """
        session_id = super(CachingSessionStore, self).create(session)  # calls _do_create and verify
        self._cache(session, session_id)
        return session_id

    def read(self, session_id):
        session = self._get_cached_session(session_id)
        return session

    def update(self, session):
        # type: (session_abcs.Session) -> None
        if session.is_valid:
            self._cache(session, session.session_id)
        else:
            self._uncache(session)

    def delete(self, session):
        self._uncache(session)

    def _get_cached_session(self, session_id):
        try:
            return self.cache_handler.get(domain='session', identifier=session_id)
        except AttributeError:
            self._logger.warning("no cache parameter nor lazy-defined cache")
        return None

    def _cache(self, session, session_id):
        self.cache_handler.set(
            domain='session',
            identifier=session_id,
            value=session
        )

    def _uncache(self, session):
        self.cache_handler.delete(domain='session', identifier=session.session_id)

    # intended for write-through caching:
    def _do_read(self, session_id):
        pass

    # intended for write-through caching:
    def _do_delete(self, session):
        pass

    # intended for write-through caching:
    def _do_update(self, session):
        pass


class SessionStorageEvaluator(object):
    """
    Global policy determining whether Subject sessions may be used to persist
    Subject state if the Subject's Session does not yet exist.
    """

    def __init__(self):
        self.session_storage_enabled = True

    def is_session_storage_enabled(self, subject=None):
        try:
            return bool(subject.get_session(False)) or self.session_storage_enabled
        except AttributeError:
            return self.session_storage_enabled
