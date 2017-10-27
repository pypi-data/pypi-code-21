#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""

import logging

import os
from celery import signals
from kids.cache import cache
from raven.contrib.celery import CeleryFilter, SentryCeleryHandler
from structlog import get_logger

from . import defaults, log_id, wflask

__author__ = "john"

logger = get_logger(__name__)


def setup_celery(_):
  """Register celery shit"""

  signals.setup_logging.connect(on_setup)
  signals.before_task_publish.connect(on_before_pub)
  signals.task_prerun.connect(on_prerun)
  get_sentry_handler().install()
  add_celery_filter()

  logger.info('Configured Celery')
  set_logs_to_info()


def on_setup(**_):
  pass


@cache(key=defaults.CACHE_KEY)
def get_sentry_handler():
  return SentryCeleryHandler(wflask.get_client())


def add_celery_filter():
  handler = wflask.sentry_handler()
  if not [f for f in handler.filters if isinstance(f, CeleryFilter)]:
    handler.addFilter(CeleryFilter())


def on_before_pub(headers=None, **_):
  headers[defaults.LOG_KEY] = log_id.find()


def on_prerun(task_id=None, task=None, **_):
  from .wflask import get_client
  sentry_client = get_client()
  sentry_client.context.clear()
  logid = getattr(task.request, 'logid', '')
  root_id = getattr(task.request, 'root_id', None)
  if root_id == task_id:
    from webstarts.util import clear_cache
    clear_cache(back=True)
  ctx = dict(logid=logid)
  if os.environ.get('WSDEV') != '1':
    ctx.update(tid=task_id, task=task.name)
  logger.new(**ctx)


def set_logs_to_info():
  names = [
    'amqp',
    'kombu',
    'celery',
    'asyncio'
  ]
  [logging.getLogger(n).setLevel(logging.INFO) for n in names]
