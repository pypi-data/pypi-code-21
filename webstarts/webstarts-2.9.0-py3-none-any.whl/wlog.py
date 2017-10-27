#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""

import logging
import sys
from typing import Any, Dict

import colorama
from flask import request
from flask.ctx import has_request_context
from kids.cache import cache
from structlog import configure, processors, stdlib, threadlocal

from . import defaults, types

__author__ = "john"


def setup(conf: Dict[str, Any]):
  """Setup logging first so nothing shits on it

  - Checkout
  """
  colorama.deinit()
  logging.setLoggerClass(types.WebstartsLogger)
  logging.getLogger().setLevel(logging.NOTSET)
  set_record_factory()

  formatter = get_formatter(conf)
  handler = get_handler()
  set_handler(logging.DEBUG, handler, formatter)

  setup_struct()
  shush_loggers()

  logger = logging.getLogger(__name__)
  logger.info('Configured Logging')

  from .wflask import sentry_handler
  set_handler(logging.ERROR, sentry_handler(), formatter)


@cache(key=defaults.CACHE_KEY)
def get_formatter(conf: Dict[str, str] = None) -> types.WebstartsFormatter:
  conf = conf or {}
  fmt, proc = conf.get('fmt', None), None
  if conf['debug']:
    formatter = types.DevFormatter(fmt=fmt or defaults.FORMAT_DEBUG, proc=types.DevRenderer())
  else:
    formatter = types.WebstartsFormatter(fmt=fmt or defaults.FORMAT, proc=types.ExtrasProcessor())
  return formatter


def set_handler(level: int, handler: logging.Handler, formatter: logging.Formatter = None) -> None:
  if formatter:
    handler.setFormatter(formatter)
  handler.setLevel(level)
  logging.getLogger().addHandler(handler)


def setup_struct() -> None:
  """Configure the shit"""
  configure(
    processors=[
      stdlib.filter_by_level,
      stdlib.PositionalArgumentsFormatter(),
      processors.UnicodeDecoder(),
      # add_labels,
      render_to_log_kwargs,
    ],
    context_class=threadlocal.wrap_dict(dict),
    logger_factory=types.LogFactory(),
    wrapper_class=stdlib.BoundLogger,
    cache_logger_on_first_use=True,
  )


@cache(key=defaults.CACHE_KEY)
def get_handler() -> logging.StreamHandler:
  return logging.StreamHandler(sys.stdout)


def set_record_factory() -> None:
  old_factory = logging.getLogRecordFactory()

  # noinspection PyMissingTypeHints
  def record_factory(*args, **kwargs):
    from webstarts import log_id
    record = old_factory(*args, **kwargs)
    record.logid = log_id.find()
    record.extras = ''
    return record

  logging.setLogRecordFactory(record_factory)


def add_labels(_, __, ed) -> Dict:
  cloud = ed.pop('cloud', {})
  if has_request_context():
    cloud['httpRequest'] = dict(
      requestUrl=request.url,
      requestMethod=request.method,
      userAgent=request.user_agent.string,
      referer=request.referrer,
      remoteIp=request.remote_addr,
      requestSize=request.content_length,
    )

  ed['cloud'] = cloud
  return ed


def render_to_log_kwargs(_, __, event_dict) -> Dict:
  extra = event_dict.pop('extra', {})
  exc = event_dict.pop('exc_info', None)
  stack_info = event_dict.pop('stack_info', False)
  event_dict.pop('logid', None)
  # extra = {'ed': event_dict, 'cloud': event_dict.pop('cloud', {}), **extra}
  extra = {**extra}
  if event_dict:
    extra.update(ed=event_dict)
  ret = dict(msg=event_dict.pop("event", ''), extra=extra, exc_info=exc, stack_info=stack_info)
  return ret


def shush_loggers():
  names = [
    'passlib'
  ]
  for n in names:
    logging.getLogger(n).setLevel(logging.WARN)
