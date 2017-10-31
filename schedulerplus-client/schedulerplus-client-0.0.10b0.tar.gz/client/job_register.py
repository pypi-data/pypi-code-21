#!/usr/bin/env python
# coding: utf-8
# Author caijiajia.cn
# @ ALL RIGHTS RESERVED

import logging

from kazoo.protocol.states import KazooState

from .job_zk_client import JobZkClient
from .singleton import Singleton


class JobRegister(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.job_map = {}

    @staticmethod
    def listener(state):
        """
        The listener should return A.S.A.P
        Using kazoo client inside the listener would raise dead loop.
        :param state:
        :return:
        """
        if state == KazooState.CONNECTED:
            logging.info("kazoo reconnected.")
            import thread
            thread.start_new(JobRegister.instance().register_jobs)

    def register(self, job_name, executor):
        self.job_map[job_name] = executor
        JobZkClient.instance().register_job(job_name)

    def get_executor(self, job_name):
        return self.job_map.get(job_name)

    def register_jobs(self):
        for job_name in self.job_map:
            JobZkClient.instance().register_job(job_name)

    @staticmethod
    def instance():
        return JobRegister()
