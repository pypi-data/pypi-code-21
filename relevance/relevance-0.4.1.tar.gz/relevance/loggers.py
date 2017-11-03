"""
Relevance logger module.
"""

import logging


class Logger(logging.Logger):
    """
    Logger class.
    """
    def _log(self, level: int, event_type: str, *args, **payload):
        """
        Log a message.

        :param level: the log message level.
        :param event_type: the event type.
        :param **payload: the event payload.
        """
        parts = []
        for key, value in payload.items():
            parts.append('{0}={1}'.format(key, value))

        if len(parts) > 0:
            msg = '{0} with {1}'.format(event_type, ', '.join(parts))
        else:
            msg = event_type

        return super()._log(level, msg, *args)


# Bootstrap the logger
logging.setLoggerClass(Logger)
getLogger = logging.getLogger
