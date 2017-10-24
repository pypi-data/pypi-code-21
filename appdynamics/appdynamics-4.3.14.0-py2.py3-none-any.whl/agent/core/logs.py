# Copyright (c) AppDynamics, Inc., and its affiliates
# 2016
# All Rights Reserved

from __future__ import unicode_literals
import copy
import logging
import logging.handlers
import os.path
import re

from appdynamics import config
from appdynamics.lang import map
from appdynamics.lib import default_log_formatter, mkdir

LOGGING_MAX_BYTES = 20000000
LOGGING_MAX_NUM_FILES = 5


def get_log_level():
    default_logging_level = logging.WARNING
    allowed_logging_levels = {'WARNING': logging.WARNING, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG}

    level = config.LOGGING_LEVEL.upper()
    return allowed_logging_levels.get(level, default_logging_level)


def get_log_filename():
    non_alphanumeric = re.compile(r'\W+')
    sanitize = lambda x: non_alphanumeric.sub('_', x)
    filename = '-'.join(map(sanitize, [config.APP_NAME, config.NODE_NAME])) + '.log'
    return os.path.join(config.LOGS_DIR, filename)


def debug_enabled(logger):
    """Return True if debugging has been enabled for this logger.

    """
    # Note: we can't just check that the level is DEBUG, since that can be
    # True without config.DEBUG_LOG being True.
    for handler in logger.handlers:
        if handler.__class__ is logging.StreamHandler:
            return True
    return False


def enable_debug(logger):
    """Enable debug mode for this logger.

    This sets the log level to DEBUG and enables a stream handler to stdout.

    """
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers:
        handler.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(default_log_formatter)
    logger.addHandler(stream_handler)


def disable_debug(logger):
    """Disable debug mode for this logger.

    This removes any stream handlers from the logger and returns the log level
    to the value specified in the agent config.

    """
    level = get_log_level()
    logger.setLevel(level)

    handlers = copy.copy(logger.handlers)
    logger.handlers = []
    for handler in handlers:
        if handler.__class__ is not logging.StreamHandler:
            handler.setLevel(level)
            logger.addHandler(handler)


def configure_logging():
    """Configure the appdynamics agent logger.

    By default, we configure 6 log files of 20MB each.

    """
    try:
        logger = logging.getLogger('appdynamics.agent')

        level = get_log_level()
        logger.setLevel(level)

        path = get_log_filename()
        mkdir(os.path.dirname(path))

        rotating_file_handler = logging.handlers.RotatingFileHandler(path, maxBytes=LOGGING_MAX_BYTES,
                                                                     backupCount=LOGGING_MAX_NUM_FILES - 1)

        rotating_file_handler.setLevel(level)
        rotating_file_handler.setFormatter(default_log_formatter)
        logger.addHandler(rotating_file_handler)

        if config.DEBUG_LOG:
            enable_debug(logger)

        logger.propagate = False
    except:
        logging.getLogger('appdynamics.agent').exception('Logging configuration failed.')
