# -*- coding: utf-8 -*-
"""
    agent.worker.android_monkey
    ~~~~~~~~~~~~

    This module provide the android monkey.

    :copyright: (c) 2017 by Ma Fei.
"""
import commands
import logging
import os
import re
import time

import agent.util.file as file_tool
from agent.consts import TestRunStatus
from agent.qualityplatform import server_api
from agent.util.appetizerkit import AppToolKit
from agent.worker.base import BaseWorker

logger = logging.getLogger(__name__)

app_tool_kit = AppToolKit()

android_monkey_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/androidMonkey/')


class AndroidMonkey(BaseWorker):
    def __init__(self, data):
        super(AndroidMonkey, self).__init__(data)
        self.notice_account = self.data.get('notice_account')
        self.device_id = self.data.get('device_id')
        self.grand_id = self.data.get('grand_id')
        self.platform = self.data.get('platform')
        self.packtype = self.data.get('packtype')
        self.app_version = self.data.get('app_version')
        self.run_id = self.data.get('run_id')
        self.case_id = self.data.get('case_id')
        self.throttle = self.data.get('throttle')
        self.pct_touch = self.data.get('pct_touch')
        self.pct_motion = self.data.get('pct_motion')
        self.pct_syskeys = self.data.get('pct_syskeys')

        self.android_monkey_task_dir = os.path.join(android_monkey_dir, str(self.task_id))
        file_tool.make_worker_dir(self.android_monkey_task_dir)
        self.log_file_dir = os.path.join(android_monkey_dir, str(self.task_id), 'log')
        file_tool.make_worker_dir(self.log_file_dir)
        self.android_monkey_log = os.path.join(self.log_file_dir, 'monkey')
        self.android_monkey_error = os.path.join(self.log_file_dir, 'error')

    def start_worker(self):
        app = server_api.get_latest_app(self.grand_id, self.platform, self.packtype, self.app_version)

        file_tool.save_file(app['downloadURL'], self.android_monkey_task_dir, 'eleme_android.apk')

        app_tool_kit.uninstall_android_app(self.device_id, self.grand_id)
        app_tool_kit.install_android_app(self.device_id, self.android_monkey_task_dir + '/eleme_android.apk')
        monkey_duration = self.start_monkey(self.device_id)
        mail_content = self.deal_with_log(self.android_monkey_error, monkey_duration)
        if mail_content == '':
            mail_content = 'No crash happened'
            test_run_status = TestRunStatus.passed.value
        else:
            test_run_status = TestRunStatus.failed.value
            self.upload(self.log_file_dir, str(self.task_id))
            mail_content = 'http://10.12.38.246:8000/report/' + str(self.task_id) + '/error.txt'
            server_api.add_jira_issue('UTM', 'Monkey Error Log', 'Monkey error log url:' + mail_content)
        if self.run_id:
            server_api.add_results_for_cases(self.run_id, self.case_id, mail_content, test_run_status, app)
        server_api.upload_task_reports(self.task_id, mail_content)
        self.complete()

    @staticmethod
    def stop_monkey(device_id):
        for i in xrange(10):
            status, output = commands.getstatusoutput('adb -s %s shell ps | grep monkey' % device_id)
            if output == "error: device not found":
                logger.debug("Please check device")
            elif output == "":
                logger.info("no monkey running in %s" % device_id)
                break
            else:
                output = re.search('shell     [0-9]+', output).group()
                pid = re.search('[0-9]+', output).group()
                logger.info("kill the monkey process: %s in %s" % (pid, device_id))
                commands.getstatusoutput("adb -s %s shell kill %s" % (device_id, pid))
            time.sleep(2)

    def start_monkey(self, device_id):
        logger.info("start monkey with {}".format(device_id))
        monkey_start_time = time.time()
        cmd_monkey = "adb -s {} shell monkey -p {} --throttle {} --pct-touch {} --pct-motion {} --pct-syskeys {} " \
                     "--ignore-crashes --ignore-timeouts -v -v 5000 1>{}.txt 2>{}.txt".format(device_id,
                                                                                              self.grand_id,
                                                                                              self.throttle,
                                                                                              self.pct_touch,
                                                                                              self.pct_motion,
                                                                                              self.pct_syskeys,
                                                                                              self.android_monkey_log,
                                                                                              self.android_monkey_error)
        logger.info("Monkey cmd: {}".format(cmd_monkey))
        commands.getstatusoutput(cmd_monkey)
        logger.info("monkey end with {}".format(device_id))
        monkey_end_time = time.time()
        monkey_duration = round((monkey_end_time - monkey_start_time) / 3600, 2)
        return str(monkey_duration)

    @staticmethod
    def deal_with_log(log_file_name_with_location, monkey_duration):
        # analyze with log:
        logger.info("deal_with_log")
        f_full_log = open(log_file_name_with_location + '.txt', 'r')
        full_log = f_full_log.readlines()
        f_full_log.close()
        full_log_lines_number = len(full_log)
        anr = 'NOT RESPONDING'
        crash = 'Crash'
        exception = 'Exception'
        mail_content = ''
        for i in xrange(full_log_lines_number):
            if (exception in full_log[i]) | (anr in full_log[i]) | (crash in full_log[i]):
                f_crash_log = open(log_file_name_with_location + '.txt', 'r')
                f_crash_log.close()
                for j in range(i, full_log_lines_number):
                    mail_content = mail_content + full_log[j] + '\r'
                break
        if mail_content == "":
            return mail_content
        tmp = log_file_name_with_location.split('/')
        log_file_name = tmp[-1]
        mail_content = log_file_name + '_' + monkey_duration + "hour" + '\r\r' + mail_content
        return mail_content
