#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.worker.monitor
    ~~~~~~~~~~~~

    This module provide the monitor.

    :copyright: (c) 2017 by Ma Fei.
"""
import commands
import logging
import os
import zipfile

import agent.util.file as file_tool
import agent.worker.appetizerio.insights as insights
from agent.consts import TestRunStatus
from agent.qualityplatform import server_api
from agent.worker.base import BaseWorker

logger = logging.getLogger(__name__)

monitor_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/monitor/')


class Monitor(BaseWorker):
    def __init__(self, data):
        super(Monitor, self).__init__(data)
        self.notice_account = self.data.get('notice_account')
        self.username = self.data.get('username')
        self.password = self.data.get('password')
        self.device_id = self.data.get('device_id')
        self.grand_id = self.data.get('grand_id')
        self.platform = self.data.get('platform')
        self.packtype = self.data.get('packtype')
        self.run_id = self.data.get('run_id')
        self.case_id = self.data.get('case_id')
        self.app = server_api.get_latest_app(self.grand_id, self.platform, self.packtype)

        self.android_monitor_task_dir = os.path.join(monitor_dir, str(self.task_id))

    def start_worker(self):
        file_tool.save_file(self.app['downloadURL'], self.android_monitor_task_dir, 'eleme_android.apk')
        os.chdir(self.android_monitor_task_dir)
        logger.info(u'当前目录：>>>>>>>>>>' + os.getcwd())
        logger.info(u'开始登陆：>>>>>>>>>>')
        insights.login(self.username, self.password)
        logger.info(u'当前目录：>>>>>>>>>>' + os.getcwd())

        logger.info(
            u'开始安装：>>>>>>>>>>' + '/Users/mobile.test/eleme.qa/app/instrumented.apk' + '|' + str(self.device_id))

        insights.install('/Users/mobile.test/eleme.qa/app/instrumented.apk', {self.device_id})

        logger.info(
            u'开始清理log：>>>>>>>>>>' + '/Users/mobile.test/eleme.qa/app/instrumented.apk' + '|' + str(self.device_id))

        insights.clearlog('/Users/mobile.test/eleme.qa/app/instrumented.apk', {self.device_id})

        logger.info(
            u'开始执行monkey：>>>>>>>>>>')

        cmd_monkey = "adb -s {} shell monkey -p {} --throttle 300 --pct-touch 50 --pct-motion 50 --ignore-crashes --ignore-timeouts -v -v 5000".format(
            self.device_id, self.grand_id)
        logger.info("Monkey cmd: {}".format(cmd_monkey))
        commands.getstatusoutput(cmd_monkey)

        logger.info(
            u'开始分析：>>>>>>>>>>' + '/Users/mobile.test/eleme.qa/app/instrumented.apk' + '|' + str(self.device_id))

        key = insights.analyze('/Users/mobile.test/eleme.qa/app/instrumented.apk', {self.device_id})

        logger.info(key)

        logger.info(
            u'开始下载报告：>>>>>>>>>>' + 'http://cache.appetizer.io/' + key + '_export.html.zip' + '|' + str(self.device_id))

        file_tool.save_file('http://cache.appetizer.io/' + key + '_export.html.zip', self.android_monitor_task_dir,
                            'report.zip')

        logger.info(
            u'开始解压报告：>>>>>>>>>>' + self.android_monitor_task_dir + '/report.zip' + '|' + str(self.device_id))
        f = zipfile.ZipFile(self.android_monitor_task_dir + '/report.zip', 'r')
        for report_file in f.namelist():
            f.extract(report_file, '/Users/mobile.test/eleme.qa/report/' + str(self.task_id))
        mail_content = 'http://10.12.38.246:8000/report/' + str(self.task_id) + '/index.html'

        if self.run_id:
            logger.info('add test run reesult')
            server_api.add_results_for_cases(self.run_id, self.case_id, mail_content, TestRunStatus.failed.value,
                                             self.app)

        self.complete()

    def clear(self):
        pass
