#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import logging

from flask import Flask
from kids.cache import cache
from raven import Client, middleware
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler

from . import defaults

__author__ = "john"


def setup_app(app, dsn=None, **client_args):
  """

  - exclude_paths
    Should use this to ignore the flask-classful crap that is in every trace?
  - Pass all in 'data'. logging.error('asdf', extra={'data': {}})
  - When updating sentry with app
    - sentry.client.tags['flask_app'] = app.name
  """
  sentry = get_sentry()
  sentry.client.set_dsn(dsn)
  for k, v in client_args.items():
    setattr(sentry.client, k, v)
  sentry.init_app(app, dsn=dsn)
  sentry.client.tags['flask_app'] = app.name
  logging.getLogger(__name__).info('Finalized webstarts config')


class FlaskApp(Flask):
  """Inherit from this in usage application"""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @property
  def logger(self):
    return logging.getLogger(self.logger_name)


@cache(key=defaults.CACHE_KEY)
def get_sentry(**kwargs) -> 'Sentry':
  kwargs['install_logging_hook'] = False
  # ignore not configured message from raven that is forced on us at info
  _log = logging.getLogger('webstarts.wflask.SentryClient')
  _log.setLevel(logging.WARN)
  client = SentryClient(**kwargs)
  _log.setLevel(logging.DEBUG)
  sentry = Sentry(client=client, wrap_wsgi=False, logging=False)
  get_sentry.sentry = sentry
  return get_sentry.sentry


def get_client() -> 'SentryClient':
  return get_sentry().client


@cache(key=defaults.CACHE_KEY)
def sentry_handler() -> 'SentryHandler':
  sentry = get_sentry()
  handler = SentryHandler(client=sentry.client)
  return handler


def add_logging_context(tags, extra):
  from . import log_id
  tags = tags or {}
  extra = extra or {}
  ctx = log_id.ctx()
  tags.update(logid=ctx.get(defaults.LOG_KEY))
  extra.update(ctx)
  return tags, extra


def wrap_sentry(app):
  return RavenMiddleware(app, client=get_sentry().client)


class SentryClient(Client):
  """Subclass for more control over what is sent to sentry"""

  def __init__(self, *args, **kwargs):
    kwargs['include_paths'] = {'socialclime'}
    super().__init__(*args, **kwargs)

  def capture(self, event_type, tags=None, extra=None, **kwargs):
    tags, extra = add_logging_context(tags, extra)
    super().capture(event_type, tags=tags, extra=extra, **kwargs)


class RavenMiddleware(middleware.Sentry):
  """Clear context before request starts"""

  def __call__(self, environ, start_response):
    self.client.context.clear()
    return super().__call__(environ, start_response)
