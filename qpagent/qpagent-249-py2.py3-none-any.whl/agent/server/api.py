#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

from bottle import Bottle, run
from bottle import request

import agent.config as config
from agent.qualityplatform.api import get_task_by_id
from agent.queue import TaskQueue

# from agent.queue import (
#     macaca_q,
#     selenium_q,
#     appcrawler_q,
#     androidmonkey_q,
#     crawlerTask_q,
#     iosmonkey_q
# )

q = TaskQueue(num_workers=5)

app = Bottle()
logger = logging.getLogger(__name__)


def start_server():
    run(app, host='', port=config.agent['port'])


@app.post('/jobs')
def task():
    body = request.body
    agent_task = json.load(body)
    task_id = agent_task.get('task_id')
    task = get_task_by_id(task_id)
    worker_data = json.loads(task.get('params'))
    worker_type = worker_data.get('worker_type')
    q.add_task(worker_type, task_id)


@app.get('/ping')
def ping():
    return json.dumps(True)
