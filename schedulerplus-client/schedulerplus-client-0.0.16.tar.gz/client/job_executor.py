#!/usr/bin/env python
# coding: utf-8
# Author caijiajia.cn
# @ ALL RIGHTS RESERVED

import logging
from abc import abstractmethod
from datetime import datetime

import time

import requests
from .job_zk_client import JobZkClient, JobZkClientException
from .job_code_messages import *
from .config import Config


class JobExecutor:

    def __init__(self):
        self.zk_client = JobZkClient.instance()
        self.scheduler_plus_url = Config.instance().SCHEDULERPLUS_URL
        self.LOG_RESULT_URL = "/logResult"

    @abstractmethod
    def execute(self, external_data):
        """
        Job execute logic, needs be implemented by subclasses.
        :param external_data: param given when triggered on web.
        :return: r, m; boolean execute result and message
        """
        pass

    def execute_job(self, form):
        job_name = form.get("jobName")
        job_group = form.get("jobGroup")
        job_schedule_id = form.get("jobScheduleId")
        ori_schedule_id = form.get("oriScheduleId")
        retry_times = form.get("retryTimes", 0)
        external_data = form.get("externalData")
        concurrency = form.get("concurrency", 1)
        global_concurrency = form.get("globalConcurrency", 1)

        try:
            self.zk_client.prepare_execution(job_name, concurrency, global_concurrency)
        except Exception as e:
            logging.error("{send result failed {}".format(e))
            self.send_result(None, None, PREPARE_EXEC_ERROR_CODE, e.message, job_schedule_id,
                             ori_schedule_id, retry_times, job_name, job_group, external_data)
            return

        start = datetime.now()
        try:
            code, message = self.execute(external_data)
        except Exception as e:
            code = EXECUTE_JOB_ERROR_CODE
            message = e.message
        finally:
            interval = (datetime.now() - start).microseconds/1000  # milli secs needed

        try:
            start = int(time.mktime(start.timetuple()) * 1000)  # alibaba fast json serialize date as timestamp
            self.send_result(start, interval, code, message, job_schedule_id, ori_schedule_id,
                             retry_times, job_name, job_group, external_data)
        except SendResultException as e:
            logging.error("{}".format(e))

        try:
            self.zk_client.report_finished(job_name)
        except JobZkClientException as e:
            logging.error("{}".format(e))

    def send_result(self, start, interval, code, message, job_schedule_id, ori_schedule_id,
                    retry_times, job_name, job_group, external_data):
        d = {'start': start, 'interval': interval, 'code': code, 'message': message, 'jobScheduleId': job_schedule_id,
             'oriScheduleId': ori_schedule_id, 'retryTimes': retry_times, 'jobName': job_name, 'jobGroup': job_group,
             'externalData': external_data}
        try:
            requests.post(self.scheduler_plus_url + self.LOG_RESULT_URL, json=d)
        except BaseException as e:
            logging.error("send result error: {}".format(e))
            raise SendResultException(e.message)


class SendResultException(Exception):
    pass

