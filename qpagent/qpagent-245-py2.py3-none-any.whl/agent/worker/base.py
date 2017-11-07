#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import time

import agent.qualityplatform.api as server_api
from agent.consts import TaskStatus
from agent.exc import WorkerException
from agent.qualityplatform.api import get_task_by_id
from agent.util.sentry import Sentry

logger = logging.getLogger(__name__)

sentry = Sentry()


class BaseWorker(object):
    def __init__(self, data):
        task_id = data.get('task_id')
        task = get_task_by_id(task_id)
        worker_data = json.loads(task.get('params'))
        self.task_id = task_id
        self.task_type = task.get('task_type')
        self.retry_count = task.get('retry_count')
        self.data = worker_data

    def start_worker(self):
        raise NotImplementedError

    def complete(self):
        server_api.update_task_status(self.task_id, TaskStatus.success.value)

    def run(self):
        try:
            server_api.update_task_status(self.task_id, TaskStatus.running.value)
            return self.start_worker()
        except Exception as e:
            logger.error(
                'got worker exception in run worker task {}: {}'.format(
                    self.task_id, repr(e))
            )
            sentry.client.captureException()
            server_api.update_task_status(self.task_id, TaskStatus.failed.value)
            return self.retry()

    def retry(self):
        count = 0
        log = ''
        while count < self.retry_count:
            try:
                time.sleep(1)
                return self.start_worker()
            except Exception as e:
                log += 'retry {} time failed: {} | '.format(count, repr(e))
                logger.warning(
                    'got exception in retry worker task {} loop {}: {}'.format(
                        self.task_id, count, e.message))
                sentry.client.captureException()
                server_api.update_task_status(self.task_id, TaskStatus.failed.value)
            count += 1
            if count == self.retry_count:
                raise WorkerException(
                    'retry worker task {} failed {} times : {}'.format(
                        self.task_id, count, log))
