#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging

from bottle import Bottle, run
from bottle import request

import agent.config as config
from agent.consts import AgentWorkerType
from agent.qualityplatform.api import get_task_by_id
from agent.queue import (
    macaca_q,
    selenium_q,
    appcrawler_q,
    androidmonkey_q,
    crawlerTask_q,
    iosmonkey_q
)

app = Bottle()
logger = logging.getLogger(__name__)


def start_server():
    run(app, host='', port=config.agent['port'])


@app.post('/jobs')
def task():
    body = request.body
    agent_task = json.load(body)
    if agent_task.get('task_type', '') == 'crawler':
        logger.info('爬虫队列')
        crawlerTask_q.put(agent_task)
        return
    task_id = agent_task.get('task_id')
    task = get_task_by_id(task_id)
    worker_data = json.loads(task.get('params'))
    worker_type = worker_data.get('worker_type')
    if worker_type is AgentWorkerType.macaca.value:
        logger.info('Macaca队列')
        macaca_q.put(agent_task)
    elif worker_type is AgentWorkerType.selenium.value:
        logger.info('selenium队列')
        selenium_q.put(agent_task)
    elif worker_type is AgentWorkerType.appcrawler.value:
        logger.info('appcrawler队列')
        appcrawler_q.put(agent_task)
    elif worker_type is AgentWorkerType.androidmonkey.value:
        logger.info('androidmonkey队列')
        androidmonkey_q.put(agent_task)
    elif worker_type is AgentWorkerType.iosmonkey.value:
        logger.info('iosmonkey队列')
        iosmonkey_q.put(agent_task)


@app.get('/ping')
def ping():
    return json.dumps(True)
