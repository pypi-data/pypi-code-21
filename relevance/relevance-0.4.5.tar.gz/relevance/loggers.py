"""
This module provides the functionality for binary and extended logging. Rather than use
the :mod:`logging` module directly and parse message strings, this module allows a message
to be logged with parameters, making it easier to parse by a computer.
"""

import logging


class Logger(logging.Logger):
    """
    This subclass of :class:`logging.Logger` rewires the logging method so that
    arbritary keyword arguments can be supplied along with an event type, so that
    log messages are easily machine readable.
    """
    def _log(self, level: int, event_type: str, *args, **payload):  # pylint: disable=arguments-differ
        """
        Implementation of :meth:`logging.Logger._log`.

        :param level: the log message level, as defined in the :mod:`logging` module.
        :param event_type: the event type, typically a string that describes the current
            action or state to log.
        :param **payload: the keyword arguments to attach to the log message.
        """
        parts = []
        for key, value in payload.items():
            parts.append('{0}={1}'.format(key, value))

        if parts:
            msg = '{0} with {1}'.format(event_type, ', '.join(parts))
        else:
            msg = event_type

        return super()._log(level, msg, *args)  # type: ignore  # pylint: disable=no-value-for-parameter


def getLogger(*args, **kwargs):  # pylint: disable=invalid-name
    """
    Override logger method to use our own logger.
    """
    return logging.getLogger(*args, **kwargs)


# Bootstrap the logger
logging.setLoggerClass(Logger)
