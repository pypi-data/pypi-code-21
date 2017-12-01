import contextlib
import unittest.mock

import pytest

import error_boundary

from . import django_stub, raven_stub


class SomeException(Exception):
    pass


class SomeOtherException(Exception):
    pass


def always_raise(*args, **kwargs):
    raise RuntimeError


@pytest.fixture
def TestBoundary():
    """Get a fresh ErrorBoundary subclass with mock loggers."""

    class TestBoundary(error_boundary.ErrorBoundary):
        loggers = [unittest.mock.MagicMock(), unittest.mock.MagicMock()]

    return TestBoundary


def assert_propagates(boundary, exception_cls=SomeException):
    with pytest.raises(exception_cls):
        with boundary:
            raise exception_cls()


def assert_suppresses(boundary, exception_cls=SomeException):
    with boundary:
        raise exception_cls()


def test_no_exception(TestBoundary):
    """If no exception happened, nothing should be raised and nothing should
    be logged."""
    with TestBoundary() as test_boundary:
        pass
    for logger in TestBoundary.loggers:
        logger.assert_not_called()
    assert test_boundary.exc_info is None


def test_suppressed_exception(TestBoundary):
    """If an exception was caught and suppressed, it should be logged and
    'exc_info' should be set."""
    test_boundary = TestBoundary()
    assert_suppresses(test_boundary)
    assert test_boundary.exc_info[0] is SomeException
    assert type(test_boundary.exc_info[1]) is SomeException
    for logger in test_boundary.loggers:
        logger.assert_called_once_with(test_boundary.exc_info)


def test_dont_catch_argument(TestBoundary):
    """Test the 'dont_catch' argument."""
    test_boundary = TestBoundary(dont_catch=[SomeOtherException])
    assert_suppresses(test_boundary)
    assert_propagates(test_boundary, SomeOtherException)
    for logger in test_boundary.loggers:
        logger.assert_called_once_with(test_boundary.exc_info)


def test_loggers_argument(TestBoundary):
    """Test the 'loggers' argument."""
    mylogger = unittest.mock.MagicMock()
    test_boundary = TestBoundary(loggers=[mylogger])
    assert_suppresses(test_boundary)
    mylogger.assert_called_once_with(test_boundary.exc_info)
    for logger in test_boundary.__class__.loggers:
        logger.assert_not_called()


def test_default_logger():
    """Test the default logging based logger."""
    test_boundary = error_boundary.ErrorBoundary()
    with unittest.mock.patch(
            'error_boundary.default_logging_logger.exception') as mock_log:
        assert_suppresses(test_boundary)
    mock_log.assert_called_once_with(
        'Error boundary', exc_info=test_boundary.exc_info)


@unittest.mock.patch.dict('sys.modules', raven=raven_stub)
def test_raven_logger():
    """Test the Django Raven logger."""
    test_boundary = error_boundary.ErrorBoundary(
        loggers=[error_boundary.django_raven_logger])
    with unittest.mock.patch(
            'raven.contrib.django.raven_compat.models.client',
            create=True) as mock_client:
        assert_suppresses(test_boundary)
    mock_client.captureException.assert_called_once_with(
        exc_info=test_boundary.exc_info)


def test_broken_logger():
    """An exception in an error boundary logger should be logged with the
    internal logger and not propagate.
    """
    with unittest.mock.patch(
            'error_boundary._internal_logger') as mock_internal_logger:
        assert_suppresses(error_boundary.ErrorBoundary(loggers=[always_raise]))
    mock_internal_logger.exception.assert_called_once_with(
        'Error in error boundary logger %r', always_raise)


def test_broken___exit__():
    """An exception in any of the overwritten methods should be handled
    gracefully.
    """

    @contextlib.contextmanager
    def _test(broken_method):
        class BrokenErrorBoundary(error_boundary.ErrorBoundary):
            exec(broken_method + ' = always_raise')

        with unittest.mock.patch(
                'error_boundary._internal_logger') as mock_internal_logger:
            yield BrokenErrorBoundary
            mock_internal_logger.exception.assert_called_once_with(
                "ERROR BOUNDARY ERROR in 'BrokenErrorBoundary.__exit__'")

    # Log and ignore failures in the on_no_exception hook.
    with _test('on_no_exception') as BrokenErrorBoundary:
        with BrokenErrorBoundary():
            pass

    # If we can't determine if an exception should be propagated, default to
    # propagating it.
    with _test('should_propagate_exception') as BrokenErrorBoundary:
        assert_propagates(BrokenErrorBoundary(dont_catch=[SomeException]))

    # Log and ignore failures in the on_propagate_exception hook.
    with _test('on_propagate_exception') as BrokenErrorBoundary:
        assert_propagates(BrokenErrorBoundary(dont_catch=[SomeException]))

    # Log and ignore failures in the on_suppress_exception hook.
    with _test('on_suppress_exception') as BrokenErrorBoundary:
        assert_suppresses(BrokenErrorBoundary())


def test_ProductionErrorBoundary():
    assert_suppresses(error_boundary.ProductionErrorBoundary(True))
    assert_propagates(error_boundary.ProductionErrorBoundary(False))


@unittest.mock.patch.dict('sys.modules', django=django_stub)
def test_DjangoSettingErrorBoundary():
    # Test the default 'not DEBUG' setting.
    with unittest.mock.patch('django.conf.settings', DEBUG=True, create=True):
        assert_propagates(error_boundary.DjangoSettingErrorBoundary())
    with unittest.mock.patch('django.conf.settings', DEBUG=False, create=True):
        assert_suppresses(error_boundary.DjangoSettingErrorBoundary())

    # Test custom setting.
    with unittest.mock.patch(
            'django.conf.settings', CUSTOM_SETTING=False, create=True):
        assert_propagates(
            error_boundary.DjangoSettingErrorBoundary('CUSTOM_SETTING'))
    with unittest.mock.patch(
            'django.conf.settings', CUSTOM_SETTING=True, create=True):
        assert_suppresses(
            error_boundary.DjangoSettingErrorBoundary('CUSTOM_SETTING'))
