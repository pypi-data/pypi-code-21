#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.worker.appcrawler
    ~~~~~~~~~~~~

    This module provide the appcrawler.

    :copyright: (c) 2017 by Ma Fei.
"""
import logging
import os
import subprocess
from collections import OrderedDict

from pyunitreport import HTMLTestRunner

import agent.util.file as file_tool
from agent.consts import TestRunStatus
from agent.qualityplatform import server_api
from agent.worker.base import BaseWorker
from agent.worker.httprunner.task import TaskSuite

logger = logging.getLogger(__name__)

appcrawler_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/api/')


class HttpApi(BaseWorker):
    def __init__(self, data):
        super(HttpApi, self).__init__(data)
        self.run_id = self.data.get('run_id')
        self.case_id = self.data.get('case_id')
        self.report_name = self.data.get('report_name')
        self.failfast = self.data.get('failfast')

        os.chdir(appcrawler_dir)
        subprocess.call('git clone git@git.elenet.me:waimaiqa/waimai.api.git', shell=True)
        os.chdir(appcrawler_dir + 'waimai.api')
        subprocess.call('git pull origin master', shell=True)

    def start_worker(self):
        api_path = os.path.join(appcrawler_dir, 'waimai.api')
        results = {}
        success = True

        api_path = api_path.rstrip('/')

        task_suite = TaskSuite(api_path)

        output_folder_name = os.path.join('/Users/mobile.test/eleme.qa/report/', str(self.task_id))
        kwargs = {
            "output": output_folder_name,
            "report_name": 'index',
            "failfast": self.failfast
        }
        result = HTMLTestRunner(**kwargs).run(task_suite)
        results[api_path] = OrderedDict({
            "total": result.testsRun,
            "successes": len(result.successes),
            "failures": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(result.skipped)
        })

        if len(result.successes) != result.testsRun:
            success = False

        for task in task_suite.tasks:
            task.print_output()

        if success:
            test_run_status = TestRunStatus.passed.value
        else:
            test_run_status = TestRunStatus.failed.value

        mail_content = 'http://10.12.38.246:8000/report/' + str(self.task_id) + '/index.html'

        if self.run_id:
            server_api.add_results_for_cases(self.run_id, self.case_id, mail_content, test_run_status)

        self.complete()

    def clear(self):
        pass
