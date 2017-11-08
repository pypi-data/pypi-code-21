# -*- coding: utf-8 -*-
import commands
import logging
import os
import re
import time

import agent.util.file as file_tool
from agent.consts import TestRunStatus
from agent.qualityplatform import server_api
from base import BaseWorker

logger = logging.getLogger(__name__)

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

        self.wkdir = android_monkey_dir + str(self.task_id)
        self.log_file_dir = android_monkey_dir + str(self.task_id)

    def start_worker(self):
        app = server_api.get_latest_app(self.grand_id, self.platform, self.packtype, self.app_version)

        file_tool.save_file(app['downloadURL'], self.wkdir, 'eleme_android.apk')

        self.uninstall_app(self.device_id, self.grand_id)
        self.install_app(self.device_id, self.wkdir + '/eleme_android.apk')
        log_file_name_with_location = self.generate_log_file_name_with_location()
        monkey_duration = self.start_monkey(self.device_id)
        mail_content = self.deal_with_log(log_file_name_with_location, monkey_duration)
        if mail_content == '':
            mail_content = 'No crash happened'
            test_run_status = TestRunStatus.passed.value
        else:
            test_run_status = TestRunStatus.failed.value
            self.upload(self.log_file_dir, str(self.task_id))
            mail_content = 'http://10.12.38.246:8000/report/' + str(self.task_id) + '/' + str(self.task_id) + '.txt'

        server_api.add_results_for_cases(self.run_id, self.case_id, mail_content, test_run_status, app)
        self.complete()

    @staticmethod
    def install_app(device_id, app):
        install_cmd = "adb -s " + device_id + " install -f " + app
        status, output = commands.getstatusoutput(install_cmd)
        if output == "Success":
            logging.info(device_id + " install eleme apk success")
            return True
        logger.warning(device_id + " install not success")
        return False

    @staticmethod
    def uninstall_app(device_id, app_name):
        uninstall_cmd = "adb -s " + device_id + " shell pm uninstall  " + app_name
        status, output = commands.getstatusoutput(uninstall_cmd)
        if output == "Success":
            logging.info(device_id + " uninstall success")
            return True
        logging.warning(device_id + " uninstall not success")
        return False

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
                status, output = commands.getstatusoutput("adb -s %s shell kill %s" % (device_id, pid))
            time.sleep(2)

    @staticmethod
    def generate_log_file_name(device_id):
        # 生成 crash log 名字
        current_time = time.strftime("%m-%d~%H-%M-%S")
        log_file_name = device_id + '_' + current_time
        return log_file_name

    def generate_log_file_name_with_location(self):
        # 获取当前 Log 存储路径
        location_log = os.path.join(self.wkdir, 'performance', 'monkey', 'monkeylog')
        current_date = time.strftime("%Y-%m-%d")
        current_date = os.path.join(location_log, current_date)
        if os.path.isdir(current_date):
            pass
        else:
            os.makedirs(current_date)
        log_file_name = str(self.task_id)
        self.log_file_dir = current_date
        log_file_name_with_location = os.path.join(current_date, log_file_name)
        return log_file_name_with_location

    def start_monkey(self, device_id):
        logger.info("start monkey with %s" % device_id)
        log_file_name_with_location = self.generate_log_file_name_with_location(device_id)
        monkey_start_time = time.time()
        cmd_monkey = "adb -s %s shell monkey -p %s --throttle %s --pct-touch %s --pct-motion %s --pct-syskeys %s --ignore-crashes --ignore-timeouts -v -v 5000 > %s.txt" % (
            device_id, self.grand_id, self.throttle, self.pct_touch, self.pct_motion, self.pct_syskeys,
            log_file_name_with_location)
        logger.info("Monkey cmd: %s" % cmd_monkey)
        commands.getstatusoutput(cmd_monkey)
        logger.info("monkey end with %s" % device_id)
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
        else:
            tmp = log_file_name_with_location.split('/')
            log_file_name = tmp[-1]
            mail_content = log_file_name + '_' + monkey_duration + "hour" + '\r\r' + mail_content
            return mail_content

    @staticmethod
    def reboot_device(device_id):
        logger.info("Reboot %s" % device_id)
        commands.getstatusoutput('adb -s ' + device_id + ' reboot')
