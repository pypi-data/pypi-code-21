#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import uuid

from structlog import get_logger

from . import defaults

__author__ = "john"

logger = get_logger(__name__)


def err(v):
  ass = 1 + v
  return ass


def make():
  return str(uuid.uuid4())[:12].replace('-', '')


def ctx():
  return dict(logger._context._dict)


def find():
  return ctx().get(defaults.LOG_KEY) or ''


def wrap_logid(app):
  def wrap_logid_(environ, start_response):
    # maybe do not need to do .new if logid exists. in backend too.
    logid = environ.get(defaults.LOG_KEY)
    if not logid:
      from webstarts.util import clear_cache
      clear_cache()
      logid = make()
    environ[defaults.LOG_KEY] = logid
    logger.new(logid=logid)

    def wrap_logid_header(status, headers, exc_info=None):
      headers.append((defaults.LOG_KEY, logid))
      start_response(status, headers, exc_info)

    return app(environ, wrap_logid_header)

  return wrap_logid_
