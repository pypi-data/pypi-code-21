# -*- coding: utf-8 -*-

"""Message/event type for communication with browser and test runner"""
from builtins import object
import logging
from datetime import datetime
from copy import deepcopy
import json
import abc
from future.utils import with_metaclass

from voluptuous import Schema, Required
from flotsam import collection_util as cu
import six

logger = logging.getLogger(__name__)


# Registry of all known event types
EVENT_REGISTRY = {}


class MessageException(Exception):

    """Message-related error
    """
    pass


class Verdict:

    """Test verdicts"""
    PASS = 'passed'
    FAIL = 'fail'

    # When the test could not be completed, e.g. beause
    # an unexpected exception was raised
    ERROR = 'error'


class MsgType(object):

    """Constants for messages"""
    TERMINATE_CONNECTION = 'terminate_connection'

    # Meta information about project under test
    PROJ_INFO = 'proj_info'

    SESSION_STARTED = 'session_started'
    SESSION_TERMINATED = 'session_terminated'

    TC_STARTED = 'tc_started'
    TC_FINISHED = 'tc_finished'

    # Premature abort
    ABORTED = 'aborted'

    # aborted due to an error
    ERROR = 'error'


@six.python_2_unicode_compatible
class Event(with_metaclass(abc.ABCMeta, object)):

    """An event for the browser"""

    def __init__(self, schema, **kwargs):
        """ :param schema: a voluptuous schema containing additional
                           constraints. Constraints are merged with
                           the base class constraints
        """
        timestamp = datetime.now()
        self.data = kwargs

        if 'timestamp' not in kwargs:
            # Don't override a timestamp that has been passed
            # explicitly (when parsing)
            self.data['timestamp'] = datetime.isoformat(
                timestamp)

        base_schema = {
            Required('type'): six.string_types[0],
            Required('timestamp'): six.string_types[0],
        }
        schema = deepcopy(schema)
        schema.update(base_schema)
        self._schema = Schema(schema, required=True)
        # print("##### %s >>>> %s", schema, self.data)

    def validate(self):
        """Schema validation of message contents
        """
        try:
            self._schema(self.data)
        except TypeError as e:
            raise MessageException('Validation failed: {0} ({1})'
                                   .format(e, self.data))

    def serialize(self):
        """Creates JSON representation of Event object.
           Triggers a validation
        """
        self.validate()
        self._serialize(self.data)
        return json.dumps(self.data)

    def __getitem__(self, key):
        """Access to message content dictionary
        """
        return self.data[key]

    @abc.abstractmethod
    def _serialize(self, body):
        """payload, to be filled with message type specific data """

    def __str__(self):
        remaining_data = deepcopy(self.data)
        del remaining_data['type']
        del remaining_data['timestamp']
        remaining_str = cu.pretty_dict(remaining_data)
        return u'{0}: [{1}] {2}'.format(self.data['type'],
                                        self.data['timestamp'],
                                        remaining_str)

    @staticmethod
    def parse(event_json):
        """Creates an appropriate event object from JSON representation
        """
        event_dict = json.loads(event_json)
        event_type = event_dict.get('type')
        if not event_type:
            raise MessageException('Missing event type')
        event_cls = EVENT_REGISTRY.get(event_type)
        if not event_cls:
            raise MessageException('Unknown event type {0}'.format(event_type))
        result = event_cls(**event_dict)
        result.validate()
        return result


def register_eventclass(event_id):
    """Decorator for registering event classes for parsing
    """
    def register(cls):
        if not issubclass(cls, Event):
            raise MessageException(('Cannot register a class that'
                                    ' is not a subclass of Event'))
        EVENT_REGISTRY[event_id] = cls
        logger.debug('######### Event registry is now: {0}'.format(
            EVENT_REGISTRY))
        return cls
    return register


@register_eventclass(MsgType.TC_STARTED)
class TestCaseStartEvent(Event):

    def __init__(self, **kwargs):
        schema = {}
        kwargs['type'] = MsgType.TC_STARTED
        super(TestCaseStartEvent, self).__init__(schema,
                                                 **kwargs)

    def _serialize(self, body):
        pass  # no extra data


@register_eventclass(MsgType.TC_FINISHED)
class TestCaseFinishedEvent(Event):

    def __init__(self, **kwargs):
        """Message fields:
            file:       name of file in which the test case is defined
            name:       name of test case (unique within file; not necessarily
                        globally unique)
            verdict:    outcome of test ('pass', 'fail', ... TODO)
            duration:   duration of execution, in milliseconds
            suite_hash: hash of suite_name for correlation (e.g. MD5)
        """
        schema = {Required('file'): six.string_types[0],
                  Required('name'): six.string_types[0],
                  Required('verdict'): six.string_types[0],
                  Required('duration'): int,
                  Required('suite_hash'): six.string_types[0]}
        kwargs['type'] = MsgType.TC_FINISHED
        super(TestCaseFinishedEvent, self).__init__(schema,
                                                    **kwargs)

    def _serialize(self, body):
        pass  # no extra data


@register_eventclass(MsgType.TERMINATE_CONNECTION)
class ConnectionTerminationEvent(Event):

    def __init__(self, **kwargs):
        schema = {}
        super(ConnectionTerminationEvent, self).__init__(
            schema,
            type=MsgType.TERMINATE_CONNECTION)

    def _serialize(self, body):
        pass


@register_eventclass(MsgType.SESSION_STARTED)
class SessionStartedEvent(Event):

    def __init__(self, **kwargs):
        """Message fields:
           suite_name: unique name identifying test suite. Should contain
                       host and directory.
           suite_hash: hash of suite_name for correlation (e.g. MD5)
           tc_count: number of test cases in suite. Set to -1 if number
                     is not known beforehand
        """
        schema = {Required('suite_name'): six.string_types[0],
                  Required('suite_hash'): six.string_types[0],
                  Required('tc_count'): int}
        kwargs['type'] = MsgType.SESSION_STARTED
        super(SessionStartedEvent, self).__init__(
            schema,
            **kwargs)

    def _serialize(self, body):
        pass


@register_eventclass(MsgType.SESSION_TERMINATED)
class SessionTerminatedEvent(Event):

    def __init__(self, **kwargs):
        """Message fields:
           suite_hash: hash of suite_name for correlation (e.g. MD5)
        """
        schema = {Required('suite_hash'): six.string_types[0]}
        kwargs['type'] = MsgType.SESSION_TERMINATED
        super(SessionTerminatedEvent, self).__init__(
            schema,
            **kwargs)

    def _serialize(self, body):
        pass
