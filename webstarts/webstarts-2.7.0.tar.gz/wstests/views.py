#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Applicable to shittest"""
import logging

import requests
from flask import Blueprint, jsonify, render_template, request
from structlog import get_logger

__author__ = "john"

logger: logging.Logger = get_logger(__name__)

bp = Blueprint('app', __name__)


@bp.route('/')
@bp.route('/<path:path>')
def login(path=None):
  """

  https://healthgrades.com/physician/dr-john-baldauf-35lnw
  """

  logger.debug('Why no debug')
  logging.getLogger(__name__).warning('Suck it')

  return render_template('web.html')


@bp.route('/save', methods=['POST'])
def save():
  data = {k: v for k, v in request.form.items()}
  logger.info('Saved POST', **data)
  r = requests.get('https://www.healthgrades.com/physician/dr-john-baldauf-35lnw')
  return jsonify({'suck': 'it'}), 200


@bp.route('/save2', methods=['POST'])
def save2():
  d = {}
  try:
    ff = d['a']
  except KeyError as e:
    logger.exception(e, fuck='you')
    logging.getLogger(__name__).exception(e)
    ff = None

  return jsonify({'suck': ff}), 200
