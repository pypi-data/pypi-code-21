#!/usr/bin/env python
# coding: utf-8
# Author caijiajia.cn
# @ ALL RIGHTS RESERVED

import threading
from .singleton import Singleton


class JobRunningNum(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.running_num = {}
        self.mutex = threading.Lock()

    @staticmethod
    def instance():
        return JobRunningNum()

    def get_job_running_num(self, job_name):
        result = self.running_num.get(job_name)
        if result is None:
            result = 0
        return result

    def modify_job_running_num(self, job_name, n):
        self.mutex.acquire()
        try:
            num = self.get_job_running_num(job_name)
            num = num + n
            self.running_num[job_name] = num
            return num
        finally:
            self.mutex.release()
