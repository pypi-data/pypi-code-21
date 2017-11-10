import re
import time

import pytest

from dmu_utils.logging.duration import Duration


class CustomException(Exception):
    pass


def assert_logged(logger_method_mock, message_re):
    logger_method_mock.assert_called_once()
    args, kwargs = logger_method_mock.call_args
    assert len(args) == 1
    assert isinstance(args[0], basestring)
    assert re.match(message_re, args[0])


def test_as_decorator():

    collector = []

    @Duration(lambda x: None)
    def decorated():
        collector.append(True)

    decorated()

    assert collector


def test_as_context_manager():

    collector = []

    with Duration(lambda x: None):
        collector.append(True)

    assert collector


def test_log_message_as_decorator(mocker):

    logger_method_mock = mocker.Mock()

    collector = []

    @Duration(logger_method_mock)
    def decorated():
        collector.append(True)

    decorated()

    assert collector
    assert_logged(logger_method_mock, r'decorated\(\) is done in ')


def test_log_custom_message_as_decorator(mocker):

    logger_method_mock = mocker.Mock()

    collector = []

    @Duration(logger_method_mock, 'custom')
    def decorated():
        collector.append(True)

    decorated()

    assert collector
    assert_logged(logger_method_mock, 'custom is done in ')


def test_log_message_with_args_as_decorator(mocker):

    logger_method_mock = mocker.Mock()

    collector = []

    @Duration(logger_method_mock, log_args=True)
    def decorated(arg1, kwarg1):
        collector.append(True)

    decorated(5, kwarg1='string')

    assert collector
    assert_logged(logger_method_mock, r"decorated\(5, kwarg1='string'\) is done in ")


def test_log_message_as_context_manager(mocker):
    logger_method_mock = mocker.Mock()

    collector = []

    with Duration(logger_method_mock, 'append'):
        collector.append(True)

    assert collector
    assert_logged(logger_method_mock, 'append is done in ')


def test_log_exception_as_decorator(mocker):

    logger_method_mock = mocker.Mock()

    @Duration(logger_method_mock)
    def decorated():
        raise CustomException('Test')

    with pytest.raises(CustomException):
        decorated()

    assert_logged(logger_method_mock,
                  r"decorated\(\) is done in [0-9.]+? seconds with CustomException\('Test',\)")


def test_log_exception_as_context_manager(mocker):
    logger_method_mock = mocker.Mock()

    with pytest.raises(CustomException):
        with Duration(logger_method_mock):
            raise CustomException('Test')

    assert_logged(logger_method_mock,
                  r"block is done in [0-9.]+? seconds with CustomException\('Test',\)")


def test_correct_duration_as_decorator(mocker):

    logger_method_mock = mocker.Mock()

    @Duration(logger_method_mock)
    def decorated():
        time.sleep(0.01)

    decorated()

    assert_logged(logger_method_mock, r'decorated\(\) is done in [0-9.]+? seconds')
    m = re.match(r'decorated\(\) is done in ([0-9.]+?) seconds',
                 logger_method_mock.call_args[0][0])
    duration = float(m.group(1))
    assert 0.01 <= duration < 0.011


def test_correct_duration_as_context_manager(mocker):
    logger_method_mock = mocker.Mock()

    with Duration(logger_method_mock):
        time.sleep(0.01)

    assert_logged(logger_method_mock, r"block is done in [0-9.]+? seconds")
    m = re.match(r'block is done in ([0-9.]+?) seconds', logger_method_mock.call_args[0][0])
    duration = float(m.group(1))
    assert 0.01 <= duration < 0.011
