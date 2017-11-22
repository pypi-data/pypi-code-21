# -*- coding: UTF-8 -*-
"""
    trytond_async.celery

    Implementation of the celery app

    This module is named celery because of the way celery workers lookup
    the app when `--proj` argument is passed to the worker. For more details
    see the celery documentation at:
    http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#about-the-app-argument
"""
from __future__ import absolute_import

import os

from celery import Celery
from trytond.config import config

try:
    from raven import Client
    from raven.contrib.celery import register_signal
except ImportError:
    pass
else:
    if os.environ.get('SENTRY_DSN'):
        sentry_client = Client(os.environ.get('SENTRY_DSN'))
        register_signal(sentry_client)

config.update_etc()


broker_url = config.get('async', 'broker_url')
backend_url = config.get('async', 'backend_url')

app = Celery(
    'trytond_async',
    broker=broker_url or os.environ.get('TRYTOND_ASYNC__BROKER_URL'),
    backend=backend_url or os.environ.get('TRYTOND_ASYNC__BACKEND_URL'),
    include=['trytond_async.tasks']
)

app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=os.environ.get(
        'CELERY_TASK_RESULT_EXPIRES', 3600),
    CELERY_TASK_SERIALIZER='tryson',
    CELERY_RESULT_SERIALIZER='tryson',
    CELERY_ACCEPT_CONTENT=[
        'application/x-tryson',
        'application/x-python-serialize'
    ],
    TEST_MODE=True if os.environ.get("DISABLE_ASYNC") else False
)

if __name__ == '__main__':
    app.start()
