import contextlib
import logging

_internal_logger = logging.getLogger(__name__)

#: The default error boundary logger logs to a :class:`logging.Logger` with the
#: name `error_boundary`.
default_logging_logger = logging.getLogger('error_boundary')


class unknown_reason:
    """Dummy `propagate_reason` value used if
    :meth:`~ErrorBoundary.should_propagate_exception` raises an exception.
    """


def get_logging_logger(logger=None):
    """Get a Python :mod:`logging` based error boundary logger.

    This is the default error boundary logger.

    Args:
        logger (:class:`logging.Logger`, optional): The logger to use. Defaults
            to :obj:`default_logging_logger`.

    Returns:
        An error boundary logger.
    """
    if logger is None:
        logger = default_logging_logger

    def exc_logger(exc_info):
        logger.exception('Error boundary', exc_info=exc_info)

    return exc_logger


def django_raven_logger(exc_info):
    """Error boundary logger that sends errors to Sentry using Raven."""
    from raven.contrib.django.raven_compat.models import client
    client.captureException(exc_info=exc_info)


class ErrorBoundary(contextlib.ContextDecorator):
    """Error boundary context manager and decorator.

    Args:
        loggers (list, optional): List of error boundary loggers that
            exceptions are reported to. Defaults to only the
            :obj:`default_logging_logger`.
        dont_catch (list(Exception), optional): List of exception types that
            should not be suppressed. Defaults to none (suppress all
            exceptions).

    Attributes:
        loggers: See ``loggers`` argument.
        dont_catch: See ``dont_catch`` argument.
    """
    loggers = (get_logging_logger(), )

    def __init__(self, loggers=None, dont_catch=()):
        self.exc_info = None
        if loggers is not None:
            self.loggers = loggers
        self.dont_catch = tuple(dont_catch)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.exc_info = None
            try:
                self.on_no_exception()
            except:
                self._log_exit_error()
            return False

        exc_info = (exc_type, exc_val, exc_tb)

        try:
            propagate_reason = self.should_propagate_exception(exc_info)
        except:
            self._log_exit_error()
            propagate_reason = unknown_reason
        if propagate_reason:
            try:
                self.on_propagate_exception(propagate_reason, exc_info)
            except:
                self._log_exit_error()
            return False

        try:
            self.on_suppress_exception(exc_info)
        except:
            self._log_exit_error()
        self.exc_info = exc_info
        return True

    def _log_exit_error(self):
        _internal_logger.exception(
            "ERROR BOUNDARY ERROR in '%s.__exit__'" % self.__class__.__name__)

    def should_propagate_exception(self, exc_info):
        """Decide if the exception given by ``exc_info`` should be
        suppressed or propagated.

        If it should be suppressed, return a value that evaluates to false.

        If it should be propagated, return a value that evaluates to true. The
        reason is passed as first argument to :meth:`on_propagate_exception`.

        You can overwrite this method to fit your needs. The default behaviour
        is to suppress exceptions whose type is in :attr:`dont_catch`.

        Args:
            exc_info (tuple, see :func:`sys.exc_info`)

        Returns:
            A value that evaluates to false if the exception should be
            suppressed, otherwise a value that evaluates to true.
        """

        if issubclass(exc_info[0], self.dont_catch):
            return 'whitelist'

    def on_no_exception(self):
        """Hook that is called if the wrapped user code has not raised any
        exception.

        You can overwrite this method to fit your needs. The default behaviour
        is to simply do nothing.
        """

    def on_propagate_exception(self, propagate_reason, exc_info):
        """Hook that is called if the wrapped user code has raised an exception
        that should be propagated (see :meth:`should_propagate_exception`).

        You can overwrite this method to fit your needs. The default behaviour
        is to simply do nothing.

        Args:
            propagate_reason (any type): The propagation reason given in
                :meth:`should_propagate_exception`.
            exc_info (tuple, see :func:`sys.exc_info`)
        """

    def on_suppress_exception(self, exc_info):
        """Hook that is called if the wrapped user code has raised an exception
        that should be suppressed (see :meth:`should_propagate_exception`).

        You can overwrite this method to fit your needs. The default behaviour
        is to log the exception if it should be logged (see
        :meth:`should_log_exception` and :meth:`log_exception`).

        Args:
            exc_info (tuple, see :func:`sys.exc_info`)
        """
        if self.should_log_exception(exc_info):
            self.log_exception(exc_info)

    def should_log_exception(self, exc_info):
        """Decide if the exception given by ``exc_info`` should be logged.

        You can overwrite this method to fit your needs. The default behaviour
        is to return `True`, i.e. log all exceptions.

        Args:
            exc_info (tuple, see :func:`sys.exc_info`)

        Returns:
            bool:
        """
        return True

    def log_exception(self, exc_info):
        """Log the exception given by ``exc_info`` to its loggers.

        Note that if one of the loggers raises an exception while trying to
        log the original exception given by ``exc_info``, this logger exception
        is printed to stderr and ignored.

        Args:
            exc_info (tuple, see :func:`sys.exc_info`)
        """
        for logger in self.get_loggers_for_exception(exc_info):
            try:
                logger(exc_info)
            except:
                _internal_logger.exception('Error in error boundary logger %r',
                                           logger)

    def get_loggers_for_exception(self, exc_info):
        """Get a list of loggers that the exception given by ``exc_info``
        should be logged to.

        You can overwrite this method to fit your needs. The default behaviour
        is to use all available loggers (see :attr:`loggers`).

        Args:
            exc_info (tuple, see :func:`sys.exc_info`)

        Returns:
            iterable: List or other iterable of error boundary loggers.
        """
        return self.loggers


class ProductionErrorBoundary(ErrorBoundary):
    """Error boundary that suppresses exceptions in production, but propagates
    them during development.

    This is recommended error boundary mode.

    Args:
        is_production (bool): Are we in production?
        **kwds: See :class:`ErrorBoundary`.
    """

    def __init__(self, is_production, **kwds):
        self.is_production = is_production
        super().__init__(**kwds)

    def should_propagate_exception(self, exc_info):
        if not self.is_production:
            return 'not-production'
        return super().should_propagate_exception(exc_info)


class DjangoSettingErrorBoundary(ProductionErrorBoundary):
    """Convenience error boundary for Django. Propagate exceptions if `DEBUG`
    is true, otherwise suppress.

    Args:
        setting_name (str, optional): The Django setting to determine
            if we're in production or not. May optionally have a `'not '`
            prefix, in which case the setting's inverted boolean value is used
            for the decision. Defaults to `'not DEBUG'`, i.e. we're in
            production if the `DEBUG` setting is false.
    """

    def __init__(self, setting_name='not DEBUG', **kwds):
        from django.conf import settings
        if setting_name.startswith('not '):
            is_production = not getattr(settings, setting_name[4:])
        else:
            is_production = getattr(settings, setting_name)
        super().__init__(is_production, **kwds)
