#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to shittest"""

from flask import Flask
from structlog import get_logger

from webstarts.wflask import setup_app

__author__ = "john"

logger = get_logger(__name__)


def create_app():
  app = Flask(__name__)

  setup_app(app, dsn='https://de3e703c200f443cbe375ad22b94fb3e:5f36eac41b324a86afa701cc20d3771c@sentry.io/146706', environment='local')

  from .views import bp
  app.register_blueprint(bp)

  return app
