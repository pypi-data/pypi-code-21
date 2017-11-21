"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
import time
import collections
import pytz
import datetime
from typing import Optional
from session_store import CachingSessionStore
import abcs as session_abcs
from yosaipy2.core.utils.utils import get_logger
from yosaipy2.core import (
    AbsoluteExpiredSessionException,
    ExpiredSessionException,
    IdleExpiredSessionException,
    InvalidSessionException,
    StoppedSessionException,
)

SessionKey = collections.namedtuple('SessionKey', 'session_id')

session_tuple = collections.namedtuple('session_tuple', ['identifiers', 'session_id'])


class SimpleSession(session_abcs.ValidatingSession):
    def __init__(self, absolute_timeout, idle_timeout, host=None):
        super(SimpleSession, self).__init__()
        self.attributes = {}
        self.internal_attributes = {
            'run_as_identifiers_session_key': None,
            'authenticated_session_key': None,
            'identifiers_session_key': None
        }
        self.is_expired = None

        self.stop_timestamp = None
        self.start_timestamp = round(time.time() * 1000)  # milliseconds

        self.last_access_time = self.start_timestamp

        self.absolute_timeout = absolute_timeout
        self.idle_timeout = idle_timeout

        self.host = host
        self._logger = get_logger()

    @property
    def attribute_keys(self):
        return self.attributes.keys()

    @property
    def internal_attribute_keys(self):
        if self.internal_attributes is None:
            return None
        return set(self.internal_attributes)  # a set of keys

    @property
    def is_stopped(self):
        return bool(self.stop_timestamp)

    def touch(self):
        self.last_access_time = round(time.time() * 1000)

    def stop(self):
        self.stop_timestamp = round(time.time() * 1000)

    def expire(self):
        self.stop()
        self.is_expired = True

    @property
    def is_valid(self):
        return not self.is_stopped and not self.is_expired

    @property
    def is_absolute_timed_out(self):
        current_time = round(time.time() * 1000)
        abs_expir = self.start_timestamp + self.absolute_timeout

        if current_time > abs_expir:
            return True

        return False

    @property
    def is_idle_timed_out(self):
        current_time = round(time.time() * 1000)

        idle_expir = self.last_access_time + self.idle_timeout
        if current_time > idle_expir:
            return True

        return False

    def is_timed_out(self):
        """
        determines whether a Session has been inactive/idle for too long a time
        OR exceeds the absolute time that a Session may exist
        """
        if self.is_expired:
            return True

        if not self.last_access_time:
            msg = ("session.last_access_time for session with id [{}] is null. This value must be "
                   "set at least once, preferably at least upon instantiation. Please check the {} "
                   "implementation and ensure self value will be set (perhaps in the constructor?)"
                   ).format(str(self.session_id), self.__class__.__name__)
            raise ValueError(msg)

        try:
            if self.is_absolute_timed_out:
                return True

            if self.is_idle_timed_out:
                return True

        except AttributeError:
            msg = "Timeouts not set for session with id [{}]. Session is not considered expired."
            msg = msg.format(str(self.session_id))
            self._logger.debug(msg)

        return False

    def validate(self):
        if self.is_stopped:
            msg = ("Session with id [{}] has been explicitly stopped.  No further interaction under "
                   "this session is allowed.").format(str(self.session_id))
            raise StoppedSessionException(msg)

        if self.is_timed_out():
            self.expire()

            # throw an exception explaining details of why it expired:
            idle_timeout_min = self.idle_timeout / 1000 // 60
            absolute_timeout_min = self.absolute_timeout / 1000 // 60

            currenttime = datetime.datetime.now(pytz.utc).isoformat()
            session_id = str(self.session_id)

            msg = ("Session with id [{}] has expired. Last access time: {}. Current time: {}. "
                   "Session idle timeout is set to {} seconds ({} minutes) and "
                   "absolute timeout is set to {} seconds ({} minutes)").format(
                session_id, str(self.last_access_time), currenttime,
                str(self.idle_timeout / 1000), str(idle_timeout_min),
                str(self.absolute_timeout / 1000), str(absolute_timeout_min)
            )

            self._logger.debug(msg)

            if self.is_absolute_timed_out:
                raise AbsoluteExpiredSessionException(msg)

            raise IdleExpiredSessionException(msg)

    def get_internal_attribute(self, key):
        if not self.internal_attributes:
            return None
        return self.internal_attributes.get(key)

    def set_internal_attribute(self, key, value=None):
        self.internal_attributes[key] = value

    def set_internal_attributes(self, key_values):
        self.internal_attributes.update(key_values)

    def remove_internal_attribute(self, key):
        if not self.internal_attributes:
            return None
        else:
            return self.internal_attributes.pop(key, None)

    def remove_internal_attributes(self, to_remove):
        return [self.remove_internal_attribute(key) for key in to_remove]

    def get_attribute(self, key):
        return self.attributes.get(key)

    def get_attributes(self, keys):
        """
        :param keys: the keys of attributes to get from the session
        :type keys: list of strings

        :returns: a dict containing the attributes requested, if they exist
        """
        result = {}
        for k in keys:
            if k not in self.attributes:
                pass
            result[k] = self.attributes[k]
        return result

    def set_attribute(self, key, value):
        self.attributes[key] = value

    # new to yosai is the bulk setting/getting/removing
    def set_attributes(self, attributes):
        """
        :param attributes: the attributes to add to the session
        :type attributes: dict
        """
        self.attributes.update(attributes)

    def remove_attribute(self, key):
        return self.attributes.pop(key, None)

    # new to yosai
    def remove_attributes(self, keys):
        """
        :param keys: the keys of attributes to remove from the session
        :type keys: list of strings

        :returns: a list of popped attribute values
        """
        return [self.attributes.pop(key, None) for key in keys]

    def __eq__(self, other):
        if self is other:
            return True
        if isinstance(other, session_abcs.ValidatingSession):
            return (
                self.session_id == other.session_id and
                self.idle_timeout == other.idle_timeout and
                self.absolute_timeout == other.absolute_timeout and
                self.start_timestamp == other.start_timestamp and
                self.attributes == other.attributes and
                self.internal_attributes == other.internal_attributes
            )
        return False

    def __repr__(self):
        return ("{}(session_id: {}, start_timestamp: {}, stop_timestamp: {}, last_access_time: {},"
                "idle_timeout: {}, absolute_timeout: {}, is_expired: {},"
                "host: {}, attributes:{}, internal_attributes: {})").format(
            self.__class__.__name__,
            self.session_id, self.start_timestamp,
            self.stop_timestamp, self.last_access_time,
            self.idle_timeout, self.absolute_timeout,
            self.is_expired, self.host, self.attributes,
            self.internal_attributes
        )

    def __getstate__(self):
        return {
            'session_id': self.session_id,
            'start_timestamp': self.start_timestamp,
            'stop_timestamp': self.stop_timestamp,
            'last_access_time': self.last_access_time,
            'idle_timeout': self.idle_timeout,
            'absolute_timeout': self.absolute_timeout,
            'is_expired': self.is_expired,
            'host': self.host,
            'internal_attributes': self.internal_attributes,
            'attributes': self.attributes
        }

    def __setstate__(self, state):
        self.session_id = state['session_id']
        self.start_timestamp = state['start_timestamp']
        self.stop_timestamp = state['stop_timestamp']
        self.last_access_time = state['last_access_time']
        self.idle_timeout = state['idle_timeout']
        self.absolute_timeout = state['absolute_timeout']
        self.is_expired = state['is_expired']
        self.host = state['host']
        self.internal_attributes = state['internal_attributes']
        self.attributes = state['attributes']


class NativeSessionHandler(session_abcs.SessionHandler):
    def __init__(self,
                 session_store=CachingSessionStore(),
                 delete_invalid_sessions=True):
        self.delete_invalid_sessions = delete_invalid_sessions
        self.session_store = session_store
        self.event_bus = None

    def create_session(self, session):
        """
        :returns: a session_id string
        """
        return self.session_store.create(session)

    def delete(self, session):
        self.session_store.delete(session)

    def _retrieve_session(self, session_key):
        # type: (SessionKey) -> Optional[SimpleSession]
        session_id = session_key.session_id
        if session_id is None:
            msg = ("Unable to resolve session ID from SessionKey [{0}]."
                   "Returning null to indicate a session could not be "
                   "found.").format(session_key)
            self._logger.debug(msg)
            return None

        session = self.session_store.read(session_id)

        if session is None:
            # session ID was provided, meaning one is expected to be found,
            # but we couldn't find one:
            msg2 = "Could not find session with ID [{0}]".format(session_id)
            raise ValueError(msg2)

        return session

    def do_get_session(self, session_key):
        # type: (SessionKey) -> SimpleSession
        session_id = session_key.session_id
        msg = "do_get_session: Attempting to retrieve session with key " + str(session_id)
        self._logger.debug(msg)

        session = self._retrieve_session(session_key)

        if session is not None:
            self.validate(session, session_key)

        return session

    def validate(self, session, session_key):
        # type: (SimpleSession, SessionKey) -> None
        """
        session exception hierarchy:  invalid -> stopped -> expired
        """
        try:
            session.validate()
        except AttributeError:  # means it's not a validating session
            msg = ("The {0} implementation only supports Validating "
                   "Session implementations of the {1} interface.  "
                   "Please either implement this interface in your "
                   "session implementation or override the {0}"
                   ".do_validate(Session) method to validate.")
            msg = msg.format(self.__class__.__name__, 'ValidatingSession')
            raise AttributeError(msg)

        except ExpiredSessionException as ese:
            self.on_expiration(session, ese, session_key)
            raise ese

        except InvalidSessionException as ise:
            self.on_invalidation(session, ise, session_key)
            raise ise

    def on_start(self, session, session_context):
        """
        placeholder for subclasses to react to a new session being created
        """
        pass

    def on_stop(self, session, session_key):
        # session_key is used by the child class
        try:
            session.last_access_time = session.stop_timestamp
        except AttributeError:
            msg = "not working with a SimpleSession instance"
            self._logger.warning(msg)

        self.on_change(session)

    def after_stopped(self, session):
        if self.delete_invalid_sessions:
            self.delete(session)

    def on_expiration(self, session, expired_session_exception=None, session_key=None):
        if expired_session_exception and session_key:
            try:
                self.on_change(session)
                msg = "Session with id [{0}] has expired.".format(session.session_id)
                self._logger.debug(msg)

                identifiers = session.get_internal_attribute('identifiers_session_key')
                mysession = session_tuple(identifiers, session_key.session_id)
                self.notify_event(mysession, 'SESSION.EXPIRE')
            except:
                raise
            finally:
                self.after_expired(session)
        elif not expired_session_exception and not session_key:
            self.on_change(session)
        else:
            msg = "on_exception takes either 1 argument or 3 arguments"
            raise ValueError(msg)

    def after_expired(self, session):
        if self.delete_invalid_sessions:
            self.delete(session)

    def on_invalidation(self, session, ise, session_key):
        # session exception hierarchy:  invalid -> stopped -> expired
        if isinstance(ise, ExpiredSessionException):
            self.on_expiration(session, ise, session_key)
            return

        msg = "Session with id [{0}] is invalid.".format(session.session_id)
        self._logger.debug(msg)

        try:
            self.on_stop(session, session_key)
            identifiers = session.get_internal_attribute('identifiers_session_key')

            mysession = session_tuple(identifiers, session_key.session_id)
            self.notify_event(mysession, 'SESSION.STOP')
        except:
            raise
        # DG:  this results in a redundant delete operation (from shiro):
        finally:
            self.after_stopped(session)

    def on_change(self, session):
        self.session_store.update(session)

    def notify_event(self, session_info, topic):
        try:
            self.event_bus.send_message(topic, items=session_info)
        except AttributeError:
            msg = "Could not publish {} event".format(topic)
            raise AttributeError(msg)
