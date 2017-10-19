#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations

import copy
import logging
import logging.config
import tempfile

from .logging_json_formatter import LoggingJsonFormatter
from .logger_adapter_custom import LoggerAdapterCustom

from .logging_format import TuneLoggingFormat
from .logging_output import LoggingOutput


def get_logging_level(str_logging_level):

    assert str_logging_level
    str_logging_level = str_logging_level.upper()

    return {
        'NOTSET': logging.NOTSET,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }.get(str_logging_level, logging.INFO)


def get_logger(
    logger_name,
    logger_version=None,
    logger_level=logging.INFO,
    logger_format=None,
    logger_output=LoggingOutput.STDOUT_COLOR
):
    """
        logger_name      Return a logger with the specified logger_name, creating it if necessary.
        logger_level     Set the root logger level to the specified level.
        logger_filename  Specifies that a FileHandler be created, using the specified
              filename, rather than a StreamHandler.
    """
    if logger_format == TuneLoggingFormat.STANDARD:
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    else:
        formatter = LoggingJsonFormatter(
            logger_name,
            logger_version,
            logger_output=logger_output,
            fmt='%(asctime)s %(levelname)s %(name)s %(version)s %(message)s'
        )

    if logger_output == LoggingOutput.FILE:
        new_file, logging_file = tempfile.mkstemp()
        handler = logging.FileHandler(logging_file, encoding='utf-8')
    else:
        logging_file = None
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logger_level)

    if not len(logger.handlers):
        logger.addHandler(handler)

    return LoggerAdapterCustom(logger_output, logging_file, logger, {'version': logger_version})





