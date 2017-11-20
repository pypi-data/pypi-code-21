#!/usr/bin/env python
# coding: utf-8
# Author caijiajia.cn
# @ ALL RIGHTS RESERVED

from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock
import os

from client.config import Config
from .singleton import Singleton


from .job_running_num import JobRunningNum

import logging
logging.basicConfig()


def join(*args):
    return os.sep.join(args)


class JobZkClient(object):
    __metaclass__ = Singleton

    def __init__(self):
        self._zk_url = Config.instance().ZK_URL
        self._zk_client = KazooClient(hosts=self._zk_url)
        self._zk_client.start(5)

        self.SERVER_IP = "SERVER_IP"
        self.SERVER_PORT = "SERVER_PORT"

        self.job_root = "/job"
        self.job_lock_root = '/job_lock'
        self.lock_path = "lock"
        self.job_group = Config.instance().JOB_GROUP

    def prepare_execution(self, job_name, concurrency, global_concurrency):
        lock_path = join(self.job_lock_root, self.job_group, job_name)
        lock = self._zk_client.Lock(lock_path)

        with lock:
            self.check_running_job_num(job_name, concurrency, global_concurrency)
            n = JobRunningNum.instance().modify_job_running_num(job_name, 1)
            self._zk_client.set(join(self.job_lock_root, self.job_group, job_name), str(n))

    def check_running_job_num(self, job_name, concurrency, global_concurrency):
        job_name_path = self.get_job_name_path(job_name)
        c_list = self._zk_client.get_children(job_name_path)
        global_running_num = 0
        for c in c_list:
            if self.lock_path == c:
                continue

            if self.get_address() == c:
                num = JobRunningNum.instance().get_job_running_num(job_name)
            else:
                v, s = self._zk_client.get(join(job_name_path, c))
                num = int(v)
            global_running_num = global_running_num + num

        if JobRunningNum.instance().get_job_running_num(job_name) >= concurrency or \
                global_running_num >= global_concurrency:
            raise JobZkClientException("No available Job Executor for job [" + job_name + "]")

    def get_job_name_path(self, job_name):
        return join(self.job_root, self.job_group, job_name)

    def report_finished(self, job_name):
        path = join(self.job_root, self.job_group, job_name, self.get_address())
        n = JobRunningNum.instance().modify_job_running_num(job_name, -1)
        self._zk_client.set(path, str(n))

    def register_job(self, job_name):
        lock_path = join(self.job_lock_root, self.job_group, job_name)
        lock = self._zk_client.Lock(lock_path)

        with lock:
            self._create_path_if_not_exist(job_name)
            self._recreate_address_path(job_name)

    def _create_path_if_not_exist(self, job_name):
        path = join(self.job_root, self.job_group, job_name)
        if not self._zk_client.exists(path):
            self._zk_client.create(path, makepath=True)

    def _recreate_address_path(self, job_name):
        path = join(self.job_root, self.job_group, job_name, self.get_address())
        if self._zk_client.exists(path):
            self._zk_client.delete(path)
        n = JobRunningNum.instance().get_job_running_num(job_name)
        self._zk_client.create(path, str(n), ephemeral=True, makepath=True)

    def get_address(self):
        ip = os.getenv(self.SERVER_IP)
        port = os.getenv(self.SERVER_PORT) if os.getenv(self.SERVER_PORT) else "8001"
        print "{}:{}".format(ip, port)
        return "{}:{}".format(ip, port)

    def add_listener(self, listener):
        self._zk_client.add_listener(listener)

    @staticmethod
    def instance():
        return JobZkClient()


class JobZkClientException(Exception):
    pass

