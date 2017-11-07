#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Queue
import logging
from threading import Lock
from threading import Thread

from agent.consts import AgentWorkerType
from agent.worker.android_monkey import AndroidMonkey

# from agent.worker.appcrawler import Appcrawler
# from agent.worker.appstore import AppStoreCrawler
# from agent.worker.compatibility import Compatibility
# from agent.worker.ios_monkey import iosmonkey
# from agent.worker.macaca import Macaca
# from agent.worker.xiaomi import XiaomiCrawler

logger = logging.getLogger(__name__)

mutex = Lock()


class TaskQueue(Queue.Queue):
    def __init__(self, num_workers=1):
        Queue.Queue.__init__(self)
        self.num_workers = num_workers
        self.start_workers()

    def add_task(self, worker_type, task_id):
        self.put((worker_type, task_id))

    def start_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            worker_type, task_id = self.get(True)
            if worker_type is AgentWorkerType.androidmonkey.value:
                logger.info('androidmonkey-------'+str(task_id))
                mutex.acquire()
                AndroidMonkey(task_id).run()
                mutex.release()
