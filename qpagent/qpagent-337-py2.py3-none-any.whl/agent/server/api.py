#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.server.api
    ~~~~~~~~~~~~

    This module provide the agent server api.

    :copyright: (c) 2017 by Ma Fei.
"""
import json
import logging

from bottle import Bottle, run
from bottle import request

import agent.config as config
from agent.qualityplatform import server_api
from agent.queue import TaskQueue

q = TaskQueue(num_workers=8)

app = Bottle()
logger = logging.getLogger(__name__)


def start_server():
    run(app, host='', port=config.agent['port'])


def stop_server():
    app.close()


@app.post('/jobs')
def task():
    body = request.body
    agent_task = json.load(body)
    task_id = agent_task.get('task_id')
    task_data = server_api.get_task_by_id(task_id)
    worker_data = json.loads(task_data.get('params'))
    worker_type = worker_data.get('worker_type')
    q.add_task(worker_type, task_id)


@app.get('/ping')
def ping():
    return json.dumps(True)
