"""
logbind
=======

Much, much easier interface for ``LoggerAdapter``: bind new fields to
loggers.

"""

import logging


__version__ = '2017.11.6'


def bind(logger, **kwargs):
    # type: (logging.Logger, ...) -> logging.LoggerAdapter

    extra = {}

    # If given a LoggerAdapter instance, extract the extra
    # fields and find the original logging.Logger instance.
    if isinstance(logger, logging.LoggerAdapter):
        extra.update(logger.extra)  # Use update to force a copy
        logger = logger.logger

    extra.update(kwargs)
    return logging.LoggerAdapter(logger, extra)
