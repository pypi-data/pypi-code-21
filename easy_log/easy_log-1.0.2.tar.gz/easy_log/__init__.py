# -*- coding: utf-8 -*-

"""
easy_log library
~~~~~~~~~~~~~~~~~~~~~
easy_log is a log module for humans that can be used directly and easily.

:copyright: (c) 2017 by CcccFz.
:license: Apache2, see LICENSE for more details.
"""

import os
import logging


def log(filename, level):
    """ get a logger object that can be used directly and easily

    :param filename: the relative path or Absolute path for log file
    :param level: the log level, include debug, info, warning, error
    :return: a logging.Logger object

    usage:
        >>> from easy_log import log
        >>> logger = log('/home/tmp.log', 'info')
        >>> logger.info('You have a info record')
        >>> logger.error('You have a error record')

    Result: You will see two records in the file: /home/tmp.log
        [2017-10-11 09:30:27,229][<ipython-input-3-aeb29d4e62ce>/<module>() line:1][INFO] You have a info record
        [2017-10-11 09:30:28,229][<ipython-input-3-aeb29d4e62ce>/<module>() line:2][ERROR] You have a error record
    """

    filename = os.path.normpath(filename)
    if filename[-1] == '/':
        raise LogPathError('This path is not regular file path: %s' % filename)

    dir_path = os.path.dirname(filename)
    if dir_path and not os.path.exists(dir_path):
        raise LogPathError('Not exist this directory: %s' % dir_path)

    if os.path.isdir(filename):
        raise LogPathError('This path is not regular file path: %s' % filename)

    if not os.path.exists(filename):
        with open(filename, 'a'):
            pass

    _map = dict(debug=logging.DEBUG, info=logging.INFO, warning=logging.WARN, error=logging.ERROR)
    if level not in _map:
        raise LogLevelError('Not support this level: %s, Only support debug, info, warning, error' % level)
    level = _map[level]

    logger = logging.getLogger(os.path.basename(filename))
    logger.setLevel(level)

    formatter = logging.Formatter('[%(asctime)s][%(pathname)s/%(funcName)s() line:%(lineno)d][%(levelname)s] %(message)s')
    fh = logging.FileHandler(filename)
    fh.setLevel(level)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


class LogPathError(Exception):
    pass

class LogLevelError(Exception):
    pass
