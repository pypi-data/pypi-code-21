#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import shutil
import signal
import subprocess
import time

import agent.util.file as file_tool
from agent.qualityplatform import server_api
from base import BaseWorker

logger = logging.getLogger(__name__)

appcrawler_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/')


class Appcrawler(BaseWorker):
    def __init__(self, data):
        super(Appcrawler, self).__init__(data)
        self.notice_account = self.data.get('notice_account')
        self.conf_url = self.data.get('fuss_hash')
        self.device_id = self.data.get('device_id')
        self.grand_id = self.data.get('grand_id')
        self.platform = self.data.get('platform')
        self.packtype = self.data.get('packtype')
        self.app_version = self.data.get('app_version')
        self.app = server_api.get_latest_app(self.grand_id, self.platform, self.packtype, self.app_version)

        self.p_appium = subprocess.Popen("appium --session-override", stdout=subprocess.PIPE, shell=True,
                                         preexec_fn=os.setsid)
        time.sleep(5)
        os.chdir(appcrawler_dir)
        subprocess.call('git clone git@git.elenet.me:waimaiqa/appcrawler.git', shell=True)
        os.chdir(appcrawler_dir + 'appcrawler')
        subprocess.call('git pull origin master', shell=True)

    def start_worker(self):
        if self.conf_url:
            file_tool.save_file(self.conf_url.encode('utf-8'), 'conf/', 'eleme.yaml')
        os.chdir(appcrawler_dir + 'appcrawler')
        subprocess.call(
            'java -jar appcrawler-2.1.2.jar -c conf/eleme.yaml --capability udid=' + self.device_id + ' -a ' + self.app[
                'downloadURL'],
            shell=True)
        self.clear()
        self.upload('reports', str(self.task_id))
        shutil.rmtree('reports')
        server_api.upload_task_reports(self.task_id,
                                       'http://10.12.38.246:8000/report/' + str(self.task_id) + '/index.html')
        server_api.send_mail(self.notice_account, 'appcrawlerUI遍历报告', '饿了么android_稳定性测试_UI遍历', self.app,
                             'http://10.12.38.246:8000/report/' + str(self.task_id) + '/index.html', 'test_report.html')
        self.complete()

    def clear(self):
        logger.info('kill(%d)' % self.p_appium.pid)
        os.killpg(os.getpgid(self.p_appium.pid), signal.SIGTERM)
