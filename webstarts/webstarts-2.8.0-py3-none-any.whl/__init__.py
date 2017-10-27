#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to webstarts"""
import json
import os

from decorator import decorator

__author__ = "john"


def get_conf(env):
  """Right now just checks if it is debug mode"""
  conf = json.loads(env.get('WSCONF', '{}'))
  debug = True if env.get('WSDEV') == '1' else False
  conf.update(debug=debug)
  return conf


def configure(env=os.environ):
  from . import wlog, backend
  conf = get_conf(env)
  wlog.setup(conf)
  backend.setup_celery(conf)
  return conf


def entry():
  """Run eventlet


  - structlog
    Check out colorama
    Like queries always do log = log.new(y=23)
    logging.getLogger('foo').addHandler(logging.NullHandler()) should be used by libraries
  - GoogleCloud logging - when the shit gets fixed
    I could add the handler to logging.getLogger('socialclime') since it will be the parent of all app loggers.
    Now that i finally understand logging.

  """
  from gevent import monkey
  monkey.patch_all(subprocess=True)

  conf = configure()

  from .gunicorn import WebstartsApp

  app = WebstartsApp('%(prog)s [OPTIONS] [APP_MODULE]', conf['debug'])
  return app.run()


@decorator
def trace(f, *args, **kwargs):
  import colorama
  import inspect
  reset = colorama.Style.RESET_ALL
  brblack = colorama.Fore.BLACK + colorama.Style.BRIGHT
  red = colorama.Fore.LIGHTRED_EX + colorama.Style.BRIGHT
  # full = inspect.getcallargs(f, *args, **kwargs)
  # full = dict(full)
  # aas, kws = full.pop('args', None), full.pop('kwargs', None)
  # print(f'{brblack}{name:50}{reset} {brblack}Named={reset}{full!r:200} {brblack}Args={reset}{aas} {brblack}Kwargs={reset}{kws}')

  from . import log_id
  name = [i for i in inspect.getmembers(f, lambda mem: isinstance(mem, str)) if i[0] == '__qualname__'][0][1]
  before = log_id.find()
  ret = f(*args, **kwargs)
  after = log_id.find()
  # print(f'{brblack}{name:100}{reset} - {red}{before}{reset}->{brblack}{after}{reset}')
  return ret
