#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

from bottle import Bottle, run
from bottle import request

import agent.config as config
from agent.queue import TaskQueue
from agent.consts import AgentWorkerType

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
    worker_type = agent_task.get('worker_type')
    if worker_type is AgentWorkerType.crawler.value:
        q.add_task(worker_type, agent_task)
    else:
        q.add_task(worker_type, task_id)


@app.get('/ping')
def ping():
    return json.dumps(True)
