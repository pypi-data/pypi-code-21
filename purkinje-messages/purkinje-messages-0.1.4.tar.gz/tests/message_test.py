# -*- coding: utf-8 -*-

"""Test cases for messages"""
from __future__ import absolute_import
from builtins import str
import json
import sys
import pytest
from datetime import datetime
from mock import Mock
import logging
import purkinje_messages.message as sut

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


@pytest.fixture
def mock_date(monkeypatch):
    m = Mock()
    m.now.return_value = datetime(2014, 2, 1, 8, 9, 10)
    monkeypatch.setattr(sut,
                        'datetime',
                        m)
    m.isoformat = datetime.isoformat


@pytest.fixture
def tc_start_event(mock_date):
    return sut.TestCaseStartEvent()


@pytest.fixture
def connection_termination_event(mock_date):
    return sut.ConnectionTerminationEvent()


@pytest.fixture
def tc_finished_event(mock_date):
    return sut.TestCaseFinishedEvent(
        file='/dummydir/dummy_test.py',
        name='tc_1',
        verdict=sut.Verdict.PASS,
        duration=5,
        suite_hash='668a86604fc7028f2d9ea4016ae0bf7c')


@pytest.fixture
def session_started_event(mock_date):
    return sut.SessionStartedEvent(
        suite_name='testhost: /abc/xyz',
        suite_hash='668a86604fc7028f2d9ea4016ae0bf7c',
        tc_count=10
    )


@pytest.fixture
def session_terminated_event(mock_date):
    return sut.SessionTerminatedEvent(
        suite_hash='668a86604fc7028f2d9ea4016ae0bf7c'
    )


def test_tc_start_event_unicode(tc_start_event):
    expected = "tc_started: [2014-02-01T08:09:10] {}"
    assert str(
        tc_start_event) == expected


def test_term_unicode(connection_termination_event):
    expected = ('terminate_connection: '
                "[2014-02-01T08:09:10] {}")
    assert str(connection_termination_event) == expected


def test_tc_finished_unicode(tc_finished_event):
    expected = ('tc_finished: [2014-02-01T08:09:10]'
                ' {duration: 5, file: /dummydir/dummy_test.py, '
                'name: tc_1, '
                'suite_hash: 668a86604fc7028f2d9ea4016ae0bf7c'
                ', verdict: passed}')
    assert str(
        tc_finished_event) == expected


def test_ses_start_unicode(session_started_event):
    expected = ('session_started: '
                '[2014-02-01T08:09:10] {suite_hash:'
                ' 668a86604fc7028f2d9ea4016ae0bf7c,'
                ' suite_name: testhost: /abc/xyz, tc_count: 10}')
    assert str(
        session_started_event) == expected


def test_ses_term_unicode(session_terminated_event):
    expected = ('session_terminated: '
                '[2014-02-01T08:09:10] {suite_hash:'
                ' 668a86604fc7028f2d9ea4016ae0bf7c}')
    assert str(
        session_terminated_event) == expected

# @pytest.skip('needs mock')
#  def test_timestamp(tc_start_event):
#     assert isinstance(tc_start_event.timestamp, datetime)


def test_tc_start_event_serialize(tc_start_event):
    serialized = tc_start_event.serialize()
    expected = {'type': 'tc_started',
                'timestamp': '2014-02-01T08:09:10',
                }
    assert json.loads(serialized) == expected


def test_connection_termination_serialize(connection_termination_event):
    serialized = connection_termination_event.serialize()
    expected = {'type': 'terminate_connection',
                'timestamp': '2014-02-01T08:09:10',
                }
    assert json.loads(serialized) == expected


def test_tc_finished_event_serialize(tc_finished_event):
    serialized = tc_finished_event.serialize()
    expected = {'type': 'tc_finished',
                'timestamp': '2014-02-01T08:09:10',
                'verdict': 'passed',
                'name': 'tc_1',
                'file': '/dummydir/dummy_test.py',
                'duration': 5,
                'suite_hash': '668a86604fc7028f2d9ea4016ae0bf7c'
                }
    assert json.loads(serialized) == expected


def test_session_started_serialize(session_started_event):
    serialized = session_started_event.serialize()
    expected = {'type': 'session_started',
                'timestamp': '2014-02-01T08:09:10',
                'suite_name': u'testhost: /abc/xyz',
                'suite_hash': u'668a86604fc7028f2d9ea4016ae0bf7c',
                'tc_count': 10
                }
    assert json.loads(serialized) == expected


def test_session_terminated_serialize(session_terminated_event):
    serialized = session_terminated_event.serialize()
    expected = {'type': 'session_terminated',
                'timestamp': '2014-02-01T08:09:10',
                'suite_hash': u'668a86604fc7028f2d9ea4016ae0bf7c',
                }
    assert json.loads(serialized) == expected


def test_parse_tc_start():
    event_json = ('{"type": "tc_started",'
                  ' "timestamp": "2014-02-01T08:09:11"}')
    event = sut.Event.parse(event_json)
    assert event['timestamp'] == '2014-02-01T08:09:11'


def test_parse_connection_termination():
    event_json = ('{"type": "terminate_connection",'
                  ' "timestamp": "2014-02-01T08:09:10"}')
    sut.Event.parse(event_json)


def test_parse_tc_finished():
    event_json = ('{"type": "tc_finished",'
                  ' "timestamp": "2014-02-01T08:09:10",'
                  ' "verdict": "passed",'
                  ' "file": "/dummydir/dummy_test.py",'
                  ' "name": "tc_1", '
                  ' "duration": 5, '
                  ' "suite_hash": "668a86604fc7028f2d9ea4016ae0bf7c"'
                  ' }')
    sut.Event.parse(event_json)


def test_parse_session_started():
    event_json = ('{"type": "session_started",'
                  ' "timestamp": "2014-02-01T08:09:10",'
                  ' "suite_name": "testhost: /abc/xyz",'
                  ' "suite_hash": "668a86604fc7028f2d9ea4016ae0bf7c",'
                  ' "tc_count": 10'
                  '}')
    sut.Event.parse(event_json)


def test_parse_session_terminated():
    event_json = ('{"type": "session_terminated",'
                  ' "timestamp": "2014-02-01T08:09:10",'
                  ' "suite_hash": "668a86604fc7028f2d9ea4016ae0bf7c"}')
    sut.Event.parse(event_json)


def test_parse_incorrect_syntax():
    with pytest.raises(ValueError):
        sut.Event.parse('xyz')


def test_parse_unknown_event_type():
    event_json = ('{"type": "unknown_type",'
                  ' "timestamp": "2014-02-01T08:09:10"}')
    with pytest.raises(sut.MessageException):
        sut.Event.parse(event_json)


def test_parse_missing_attribute():
    event_json = '{"type": "tc_finished"}'
    with pytest.raises(sut.MessageException):
        sut.Event.parse(event_json)


def test_getitem(tc_start_event):
    assert tc_start_event['timestamp'] \
        == '2014-02-01T08:09:10'


def test_register_eventclass():
    assert sut.MsgType.TC_STARTED in sut.EVENT_REGISTRY


def test_register_eventclass_valid_class():
    dummy_event_id = 12345

    @sut.register_eventclass(dummy_event_id)
    class MyEvent(sut.Event):

        def __init__(self):
            schema = {}
            super(MyEvent, self).__init__(schema,
                                          type='dummy_type')
    assert dummy_event_id in sut.EVENT_REGISTRY
    assert sut.EVENT_REGISTRY[dummy_event_id] == MyEvent


def test_register_eventclass_invalid_class():
    with pytest.raises(sut.MessageException):
        dummy_event_id = 12345

        @sut.register_eventclass(dummy_event_id)
        class C:
            pass


def test_msg_type():
    assert sut.MsgType.TERMINATE_CONNECTION == 'terminate_connection'


def test_message_exception():
    sut.MessageException()
