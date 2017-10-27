# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import inspect
import logging
import re


from .log_settings import *


frame_formatter = FRAME_FORMATTER


frame_separator = FRAME_SEPARATOR or ' - '


# private methods
# log processing functions

def _extract_kwargs_then_process(kwargs, key, format_dict):
    target = kwargs.pop(key, None)
    format_dict[key] = '' if not target else frame_separator + frame_formatter.format_behaviour[key](target)

def _transform_kwargs(**kwargs):
    for key_arg, method in frame_formatter.transform_kwargs_methods.iteritems():
        arg = kwargs.pop(key_arg, None)
        if arg:
            kwargs = method(arg, **kwargs)
    return kwargs

def _default_log(log_fun, msg, *args, **kwargs):
    format_dict = {'msg': msg}

    kwargs = _transform_kwargs(**kwargs)

    for k in frame_formatter.format_behaviour:
        _extract_kwargs_then_process(kwargs, k, format_dict)
    full_msg = frame_formatter.default_log_format.format(**format_dict)

    log_fun(full_msg, *args, **kwargs)

def _get_logger(mod_name=''):
    stacks = inspect.stack()
    # if len < 3 something went wrong
    # stack len should be super or equal to 3 :
    # 0 is current function _get_logger
    # 1 is the logging function (warn, info, debug, etc...)
    # 2 is the main calling function which we need to find the module
    if len(stacks) >= 3 and not mod_name:
        frame = stacks[2]
        mod = inspect.getmodule(frame[0])
        mod_name = mod.__name__ if mod else ''
    return logging.getLogger(mod_name)


# developer log functions/classess


def get_default_logger():
    return _get_logger()


def debug(msg, *args, **kwargs):
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.debug, msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.info, msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.warning, msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    # warning should be used instead
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.warn, msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.error, msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.critical, msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.exception, msg, *args, **kwargs)


def fatal(msg, *args, **kwargs):
    mod = kwargs.pop('mod', '')
    logger = _get_logger(mod)
    _default_log(logger.fatal, msg, *args, **kwargs)


class DefaultLogger(object):

    """
    mimic python basic logger
    """

    def __init__(self, logname):
        self.singleton = logging.getLogger(logname)

    def debug(self, msg, *args, **kwargs):
        _default_log(self.singleton.debug, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        _default_log(self.singleton.info, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        _default_log(self.singleton.warning, msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        # warning should be used instead
        _default_log(self.singleton.warn, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        _default_log(self.singleton.error, msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        _default_log(self.singleton.critical, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        _default_log(self.singleton.exception, msg, *args, **kwargs)

    def fatal(self, msg, *args, **kwargs):
        _default_log(self.singleton.fatal, msg, *args, **kwargs)

