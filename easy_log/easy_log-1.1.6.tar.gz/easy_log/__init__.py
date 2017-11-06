#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
easy_log library
~~~~~~~~~~~~~~~~~~~~~
easy_log is a log module for humans that can be used directly and easily.

:copyright: (c) 2017 by CcccFz.
:license: Apache2, see LICENSE for more details.

usage:
    >>> from easy_log import getLogger
    >>> logger = getLogger('/home/tmp.log', 'debug')
    >>> logger.info('[start service] You have a info record')
    >>> logger.error('[send email] You have a error record')

Result: You will see two records in the file: /home/tmp.log
    2017-10-11 09:30:27 | <ipython-input-3-aeb29d4e62ce>/<module>() line:1 | INFO | [start service] You have a info record
    2017-10-11 09:30:28 | <ipython-input-3-aeb29d4e62ce>/<module>() line:2 | ERROR | [send email] You have a error record
"""

import os
import logging
from utils import check_file_path, LogLevelError


def getLogger(path, level):
    """Get a logging.Logger instance object: logger

    :param path: the relative path or Absolute path for log file
    :param level: the log level, include debug, info, warning, error
    :return: logging.Logger
    """
    path = check_file_path(path, auto=True)

    _map = dict(debug=logging.DEBUG, info=logging.INFO, warning=logging.WARNING, error=logging.ERROR, warn=logging.WARN)
    if level not in _map:
        raise LogLevelError('Not support this level: %s, Only support debug, info, warning, error' % level)
    level = _map[level]

    formatter = logging.Formatter(
        '%(asctime)s | %(pathname)s/%(funcName)s() line:%(lineno)d | %(levelname)s | %(message)s')
    formatter.datefmt = '%Y-%m-%d %H:%M:%S'

    fh = logging.FileHandler(path)
    fh.setLevel(level)
    fh.setFormatter(formatter)

    logger = logging.getLogger(os.path.basename(path))
    logger.setLevel(level)
    logger.addHandler(fh)

    return logger
