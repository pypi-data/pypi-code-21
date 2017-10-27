#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
from threading import local

import requests
from structlog import get_logger

__author__ = "john"
__all__ = ['req_session']

log = get_logger(__name__)


class Local(local):
  def __init__(self):
    super().__init__()
    self.cache = {}


sessions = Local()
_key = requests.Session


def clear_cache(back=False):
  sessions.cache = {}
  if back:
    log.debug('Clearing backend sessions')


def req_session(cls=None) -> requests.Session:
  """Thread local request sessions"""

  _cls = cls or _key
  s = sessions.cache.get(_cls)

  if s is None:
    s = sessions.cache[_cls] = _cls()
    log.debug(f'Creating session')
  return s
