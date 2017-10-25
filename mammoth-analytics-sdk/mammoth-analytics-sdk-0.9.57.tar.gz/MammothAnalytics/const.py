from __future__ import unicode_literals
import logging
import os

log = logging


if os.environ.get('MAMMOTH_API_URL', None):
    API = os.environ['MAMMOTH_API_URL']
else:
    API = 'https://qa.mammoth.io/api/v1'

log.warning('{0} is the api server URL'.format(API))