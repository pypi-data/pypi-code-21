#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
easy_log library
~~~~~~~~~~~~~~~~~~~~~
easy_log is a log module for humans that can be used directly and easily.

:copyright: (c) 2017 by CcccFz.
:license: Apache2, see LICENSE for more details.

usage:
    >>> from easy_log import Logger
    >>> log = Logger('/home/tmp.log', 'info')
    >>> log.info('start service', 'You have a info record')
    >>> log.error('send email', 'You have a error record')

Result: You will see two records in the file: /home/tmp.log
    [2017-10-11 09:30:27,229][<ipython-input-3-aeb29d4e62ce>/<module>() line:1][INFO] [start service] You have a info record
    [2017-10-11 09:30:28,229][<ipython-input-3-aeb29d4e62ce>/<module>() line:2][ERROR] [send email] You have a error record
"""

import os
import logging
from utils import check_file_path, LogPathError, LogParaError, LogLevelError


class Logger(object):
    def __init__(self, path, level):
        """Init to create a easy_log.Logger instance object: self._logger
         
        :param path: the relative path or Absolute path for log file
        :param level: the log level, include debug, info, warning, error
        :return: None
        """
        path = check_file_path(path, auto=True)

        _map = dict(debug=logging.DEBUG, info=logging.INFO, warning=logging.WARN, error=logging.ERROR)
        if level not in _map:
            raise LogLevelError('Not support this level: %s, Only support debug, info, warning, error' % level)
        level = _map[level]

        formatter = logging.Formatter(
            '[%(asctime)s][%(pathname)s/%(funcName)s() line:%(lineno)d][%(levelname)s] %(message)s')

        fh = logging.FileHandler(path)
        fh.setLevel(level)
        fh.setFormatter(formatter)

        self._logger = logging.getLogger(os.path.basename(path))
        self._logger.setLevel(level)
        self._logger.addHandler(fh)

    def debug(self, tag, msg):
        """record a debug msg in logfile

        :param tag: a tag for category msg
        :param msg: detail msg
        :return: None
        """
        if not tag or not msg:
            raise LogParaError('tag[%s] and msg[%s] can not be empty' % (tag, msg))
        self._logger.debug('[%s] %s' % (tag, msg))

    def info(self, tag, msg):
        if not tag or not msg:
            raise LogParaError('tag[%s] and msg[%s] can not be empty' % (tag, msg))
        self._logger.info('[%s] %s' % (tag, msg))

    def warning(self, tag, msg):
        if not tag or not msg:
            raise LogParaError('tag[%s] and msg[%s] can not be empty' % (tag, msg))
        self._logger.warning('[%s] %s' % (tag, msg))

    warn = warning

    def error(self, tag, msg):
        if not tag or not msg:
            raise LogParaError('tag[%s] and msg[%s] can not be empty' % (tag, msg))
        self._logger.error('[%s] %s' % (tag, msg))


