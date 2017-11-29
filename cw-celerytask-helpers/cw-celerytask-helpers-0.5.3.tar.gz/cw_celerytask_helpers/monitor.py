"""Helpers for monitoring tasks in cubicweb-celerytask workers

Add this module 'cw_celerytask_helpers.monitor' to CELERY_IMPORTS
"""
from __future__ import absolute_import

import json

import celery
import celery.signals

from .utils import get_redis_client

MONITOR_KEY = "cw:celerytask:monitor"


def monitor_task(task_id, task_name):
    if celery.current_app.conf.get('CUBICWEB_CELERYTASK_MONITOR', True):
        client = get_redis_client()
        if client is not None:
            client.lpush(MONITOR_KEY, json.dumps({'task_id': task_id,
                                                  'task_name': task_name}))


@celery.signals.task_prerun.connect
def prerun(task_id, task, *args, **kwargs):
    monitor_task(task_id, task.name)


@celery.signals.task_postrun.connect
def postrun(task_id, task, *args, **kwargs):
    monitor_task(task_id, task.name)


@celery.signals.task_revoked.connect
def task_revoked(request, *args, **kwargs):
    monitor_task(request.task_id, request.task.name)
