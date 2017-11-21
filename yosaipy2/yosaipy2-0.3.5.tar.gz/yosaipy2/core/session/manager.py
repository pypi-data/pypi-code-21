#!/usr/bin/env python
# -*- coding: utf-8 -*-
from yosaipy2.core import (
    SessionSettings,
    InvalidSessionException,
)
from session import session_tuple, SimpleSession, SessionKey
from session import NativeSessionHandler
from yosaipy2.core.utils.utils import get_logger
from typing import Dict
import abcs as session_abcs


class DelegatingSession(session_abcs.Session):
    """
    A DelegatingSession is a client-tier representation of a server side
    Session.  This implementation is basically a proxy to a server-side
    NativeSessionManager, which will return the proper results for each
    method call.

    A DelegatingSession will cache data when appropriate to avoid a remote
    method invocation, only communicating with the server when necessary and
    if write-through session caching is implemented.

    Of course, if used in-process with a NativeSessionManager business object,
    as might be the case in a web-based application where the web classes
    and server-side business objects exist in the same namespace, a remote
    method call will not be incurred.
    """

    def __init__(self, session_manager, sessionkey):
        # type: (NativeSessionManager, SessionKey) -> None
        super(DelegatingSession, self).__init__()
        self.session_key = sessionkey
        self.session_manager = session_manager
        self._start_timestamp = None
        self._host = None
        self.stop_session_callback = None  # is set by Subject owner

    @property
    def session_id(self):
        return self.session_key.session_id

    @session_id.setter
    def session_id(self, v):
        raise Exception("do not support set of session id")

    @property
    def start_timestamp(self):
        if not self._start_timestamp:
            self._start_timestamp = self.session_manager.get_start_timestamp(self.session_key)
        return self._start_timestamp

    @property
    def last_access_time(self):
        return self.session_manager.get_last_access_time(self.session_key)

    @property
    def idle_timeout(self):
        return self.session_manager.get_idle_timeout(self.session_key)

    @idle_timeout.setter
    def idle_timeout(self, timeout):
        self.session_manager.set_idle_timeout(self.session_key, timeout)

    @property
    def absolute_timeout(self):
        return self.session_manager.get_absolute_timeout(self.session_key)

    @absolute_timeout.setter
    def absolute_timeout(self, timeout):
        self.session_manager.set_absolute_timeout(self.session_key, timeout)

    @property
    def host(self):
        if not self._host:
            self._host = self.session_manager.get_host(self.session_key)

        return self._host

    def touch(self):
        self.session_manager.touch(self.session_key)

    def stop(self, identifiers):
        self.session_manager.stop(self.session_key, identifiers)
        try:
            self.stop_session_callback()
        except TypeError:
            msg = "DelegatingSession has no stop_session_callback set."
            self._logger.debug(msg)

    @property
    def internal_attribute_keys(self):
        return self.session_manager.get_internal_attribute_keys(self.session_key)

    def get_internal_attribute(self, attribute_key):
        return self.session_manager.get_internal_attribute(
            self.session_key,
            attribute_key
        )

    def get_internal_attributes(self):
        return self.session_manager.get_internal_attributes(self.session_key)

    def set_internal_attribute(self, attribute_key, value=None):
        # unlike shiro, yosai doesn't support removing keys when value is None
        self.session_manager.set_internal_attribute(
            self.session_key,
            attribute_key,
            value
        )

    def set_internal_attributes(self, key_values):
        # unlike shiro, yosai doesn't support removing keys when value is None
        self.session_manager.set_internal_attributes(self.session_key, key_values)

    def remove_internal_attribute(self, attribute_key):
        return self.session_manager.remove_internal_attribute(self.session_key,
                                                              attribute_key)

    def remove_internal_attributes(self, to_remove):
        return self.session_manager.remove_internal_attributes(self.session_key,
                                                               to_remove)

    @property
    def attribute_keys(self):
        return self.session_manager.get_attribute_keys(self.session_key)

    def get_attribute(self, attribute_key):
        if attribute_key:
            return self.session_manager.get_attribute(self.session_key, attribute_key)
        return None

    def get_attributes(self, attribute_keys):
        if attribute_keys:
            return self.session_manager.get_attributes(self.session_key, attribute_keys)
        return None

    def set_attribute(self, attribute_key, value):
        if all([attribute_key, value]):
            self.session_manager.set_attribute(
                self.session_key,
                attribute_key,
                value
            )

    def set_attributes(self, attributes):
        if attributes:
            self.session_manager.set_attributes(self.session_key, attributes)

    def remove_attribute(self, attribute_key):
        if attribute_key:
            return self.session_manager.remove_attribute(self.session_key, attribute_key)

    def remove_attributes(self, attribute_keys):
        if attribute_keys:
            return self.session_manager.remove_attributes(self.session_key, attribute_keys)

    def __repr__(self):
        return "{0}(session_id: {1})".format(self.__class__.__name__, self.session_id)


class NativeSessionManager(session_abcs.NativeSessionManager):
    """
    Yosai's NativeSessionManager represents a massive refactoring of Shiro's
    SessionManager object model.  The refactoring is an ongoing effort to
    replace a confusing inheritance-based mixin object graph with a compositional
    design.  This compositional design continues to evolve.  Event handling can be
    better designed as it currently is done by the manager AND session handler.
    Pull Requests are welcome.

    Touching Sessions
    ------------------
    A session's last_access_time must be updated on every request.  Updating
    the last access timestamp is required for session validation to work
    correctly as the timestamp is used to determine whether a session has timed
    out due to inactivity.

    In web applications, the [Shiro Filter] updates the session automatically
    via the session.touch() method.  For non-web environments (e.g. for RMI),
    something else must call the touch() method to ensure the session
    validation logic functions correctly.
    """

    def __init__(self, settings, session_handler=NativeSessionHandler()):
        session_settings = SessionSettings(settings)
        self.absolute_timeout = session_settings.absolute_timeout
        self.idle_timeout = session_settings.idle_timeout
        self.event_bus = None
        self.session_handler = session_handler
        self._logger = get_logger()

    def apply_cache_handler(self, cachehandler):
        # no need for a local instance, just pass through
        self.session_handler.session_store.cache_handler = cachehandler

    def apply_event_bus(self, event_bus):
        self.session_handler.event_bus = event_bus
        self.event_bus = event_bus

    # -------------------------------------------------------------------------
    # Session Lifecycle Methods
    # -------------------------------------------------------------------------

    def start(self, session_context):
        """
        unlike shiro, yosai does not apply session timeouts from within the
        start method of the SessionManager but rather defers timeout settings
        responsibilities to the SimpleSession, which uses session_settings
        """
        session = self._create_session(session_context)

        self.session_handler.on_start(session, session_context)

        mysession = session_tuple(None, session.session_id)
        self.notify_event(mysession, 'SESSION.START')

        # Don't expose the EIS-tier Session object to the client-tier, but
        # rather a DelegatingSession:
        return self.create_exposed_session(session=session, context=session_context)

    def stop(self, session_key, identifiers):
        # type: (SessionKey, str) -> None
        session = self._lookup_required_session(session_key)
        try:
            msg = "Stopping session with id [{0}]".format(session.session_id)
            self._logger.debug(msg)

            session.stop()
            self.session_handler.on_stop(session, session_key)

            idents = session.get_internal_attribute('identifiers_session_key')

            if not idents:
                idents = identifiers

            mysession = session_tuple(idents, session_key.session_id)

            self.notify_event(mysession, 'SESSION.STOP')

        except InvalidSessionException:
            raise

        finally:
            # DG: this results in a redundant delete operation (from shiro).
            self.session_handler.after_stopped(session)

    # -------------------------------------------------------------------------
    # Session Creation Methods
    # -------------------------------------------------------------------------

    # consolidated with do_create_session:
    def _create_session(self, session_context):
        session = SimpleSession(self.absolute_timeout,
                                self.idle_timeout,
                                host=session_context.get('host'))
        msg = "Creating session. "
        self._logger.debug(msg)

        sessionid = self.session_handler.create_session(session)
        if not sessionid:  # new to yosai
            msg = 'Failed to obtain a sessionid while creating session.'
            raise ValueError(msg)
        return session

    # yosai.core.introduces the keyword parameterization
    def create_exposed_session(self, session, key=None, context=None):
        # shiro ignores key and context parameters
        return DelegatingSession(self, SessionKey(session.session_id))

    # -------------------------------------------------------------------------
    # Session Lookup Methods
    # -------------------------------------------------------------------------

    # called by mgt.ApplicationSecurityManager:
    def get_session(self, key):
        """
        :returns: DelegatingSession
        """
        # a SimpleSession:
        session = self.session_handler.do_get_session(key)
        if session:
            return self.create_exposed_session(session, key)
        else:
            return None

    # called internally:
    def _lookup_required_session(self, key):
        # type: (SessionKey) -> SimpleSession
        """
        :returns: SimpleSession
        """
        session = self.session_handler.do_get_session(key)
        if not session:
            msg = ("Unable to locate required Session instance based "
                   "on session_key [{}].").format(str(key))
            raise ValueError(msg)
        return session

    def is_valid(self, session_key):
        """
        if the session doesn't exist, _lookup_required_session raises
        """
        try:
            self.check_valid(session_key)
            return True
        except InvalidSessionException:
            return False

    def check_valid(self, session_key):
        return self._lookup_required_session(session_key)

    def get_start_timestamp(self, session_key):
        return self._lookup_required_session(session_key).start_timestamp

    def get_last_access_time(self, session_key):
        return self._lookup_required_session(session_key).last_access_time

    def get_absolute_timeout(self, session_key):
        return self._lookup_required_session(session_key).absolute_timeout

    def get_idle_timeout(self, session_key):
        return self._lookup_required_session(session_key).idle_timeout

    def set_idle_timeout(self, session_key, idle_time):
        session = self._lookup_required_session(session_key)
        session.idle_timeout = idle_time
        self.session_handler.on_change(session)

    def set_absolute_timeout(self, session_key, absolute_time):
        session = self._lookup_required_session(session_key)
        session.absolute_timeout = absolute_time
        self.session_handler.on_change(session)

    def touch(self, session_key):
        session = self._lookup_required_session(session_key)
        session.touch()
        self.session_handler.on_change(session)

    def get_host(self, session_key):
        return self._lookup_required_session(session_key).host

    def get_internal_attribute_keys(self, session_key):
        session = self._lookup_required_session(session_key)
        collection = session.internal_attribute_keys
        try:
            return tuple(collection)
        except TypeError:  # collection is None
            return tuple()

    def get_internal_attribute(self, session_key, attribute_key):
        return self._lookup_required_session(session_key). \
            get_internal_attribute(attribute_key)

    def get_internal_attributes(self, session_key):
        return self._lookup_required_session(session_key).internal_attributes

    def set_internal_attribute(self, session_key, attribute_key, value=None):
        session = self._lookup_required_session(session_key)
        session.set_internal_attribute(attribute_key, value)
        self.session_handler.on_change(session)

    def set_internal_attributes(self, session_key, key_values):
        session = self._lookup_required_session(session_key)
        session.set_internal_attributes(key_values)
        self.session_handler.on_change(session)

    def remove_internal_attribute(self, session_key, attribute_key):
        session = self._lookup_required_session(session_key)
        removed = session.remove_internal_attribute(attribute_key)

        if removed:
            self.session_handler.on_change(session)
        return removed

    def remove_internal_attributes(self, session_key, to_remove):
        session = self._lookup_required_session(session_key)
        removed = session.remove_internal_attributes(to_remove)

        if removed:
            self.session_handler.on_change(session)
        return removed

    def get_attribute_keys(self, session_key):
        collection = self._lookup_required_session(session_key).attribute_keys
        try:
            return tuple(collection)
        except TypeError:  # collection is None
            return tuple()

    def get_attribute(self, session_key, attribute_key):
        return self._lookup_required_session(session_key). \
            get_attribute(attribute_key)

    def get_attributes(self, session_key, attribute_keys):
        """
        :param session_key:
        :type attribute_keys: a list of strings
        """
        return self._lookup_required_session(session_key). \
            get_attributes(attribute_keys)

    def set_attribute(self, session_key, attribute_key, value=None):
        if value is None:
            self.remove_attribute(session_key, attribute_key)
        else:
            session = self._lookup_required_session(session_key)
            session.set_attribute(attribute_key, value)
            self.session_handler.on_change(session)

    # new to yosai
    def set_attributes(self, session_key, attributes):
        # type: (SessionKey, Dict) -> None
        session = self._lookup_required_session(session_key)
        session.set_attributes(attributes)
        self.session_handler.on_change(session)

    def remove_attribute(self, session_key, attribute_key):
        session = self._lookup_required_session(session_key)
        removed = session.remove_attribute(attribute_key)
        if removed is not None:
            self.session_handler.on_change(session)
        return removed

    def remove_attributes(self, session_key, attribute_keys):
        """
        :param session_key:
        :type attribute_keys: a list of strings
        """
        session = self._lookup_required_session(session_key)
        removed = session.remove_attributes(attribute_keys)
        if removed:
            self.session_handler.on_change(session)
        return removed

    def notify_event(self, session, topic):
        try:
            self.event_bus.send_message(topic, items=session)
        except AttributeError:
            msg = "Could not publish {} event".format(topic)
            raise AttributeError(msg)
