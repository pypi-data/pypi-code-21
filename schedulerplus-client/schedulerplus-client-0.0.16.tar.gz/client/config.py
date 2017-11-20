#!/usr/bin/env python
# coding: utf-8
# Author caijiajia.cn
# @ ALL RIGHTS RESERVED

from ConfigParser import ConfigParser
from .singleton import Singleton


class Config(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.cf = ConfigParser()

    def __get_zk_url(self):
        return self.cf.get("schedulerplus_client", "zk_url")

    def __get_shedulerplus_url(self):
        return self.cf.get("schedulerplus_client", "schedulerplus_url")

    def __get_job_group(self):
        return self.cf.get("schedulerplus_client", "job_group")

    def load(self, conf_file):
        self.cf.read(conf_file)

    @staticmethod
    def instance():
        return Config()

    def get_jobs(self):
        return self.cf.items('jobs')

    ZK_URL = property(__get_zk_url)
    SCHEDULERPLUS_URL = property(__get_shedulerplus_url)
    JOB_GROUP = property(__get_job_group)
