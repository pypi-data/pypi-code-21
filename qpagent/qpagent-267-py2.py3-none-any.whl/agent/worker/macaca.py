#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import shutil
import signal
import subprocess
import time

import shutit

import agent.util.file as file_tool
from agent.consts import (
    TaskType,
    DeviceStatus
)
from agent.qualityplatform import server_api
from base import BaseWorker

logger = logging.getLogger(__name__)

macaca_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/macaca/')


class Macaca(BaseWorker):
    def __init__(self, data):
        super(Macaca, self).__init__(data)
        self.devices_id = self.data.get('devices_id')

        logger.info('开始进入工作目录')
        os.chdir(macaca_dir)
        logger.info('成功进入工作目录')

        logger.info('设置设备的状态')
        self.__connect_devices()

        logger.info('开始初始化uirecorder')
        session = shutit.create_session('bash')
        session.send('uirecorder init --mobile', expect='WebDriver域名或IP', echo=True)
        session.send('127.0.0.1', expect='WebDriver端口号', echo=True)
        session.send('4444', echo=True, check_exit=False)

        logger.info('启动Macaca server')
        self.p_macaca = subprocess.Popen("macaca server --port 4444", stdout=subprocess.PIPE, shell=True,
                                         preexec_fn=os.setsid)
        time.sleep(5)

    def start_worker(self):
        if self.task_type is TaskType.uiplay.value:
            logger.info('开始执行UI回放')
            self.__ui_play()
        elif self.task_type is TaskType.uirecord.value:
            logger.info('开始执行UI录制')
            self.__ui_record()

        self.__disconnect_devices()
        self.clear()
        self.complete()

    def __ui_play(self):
        self.case_url = self.data.get('case_url')
        self.case_id = self.data.get('case_id')
        self.project_id = self.data.get('project_id')
        test_run_data = {
            "name": "UI脚本回放_" + time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time())),
            "milestone_id": server_api.get_project_milestones(self.project_id)[0].get('id'),
            "description": "{'type': 'ui_play'}",
            "include_all": False,
            "case_ids": [self.case_id]
        }
        test_run = server_api.add_project_run(self.project_id, test_run_data)

        case_dir = 'task'
        file_name = str(self.task_id) + '.js'

        file_tool.save_file(self.case_url, case_dir, file_name)

        os.chdir(macaca_dir)
        shutil.rmtree('reports')
        subprocess.call('source run.sh ' + case_dir + '/' +
                        file_name, shell=True)

        self.upload('reports', str(self.task_id))
        log = 'http://10.12.38.246:8000/report/' + str(self.task_id) + '/index.html'
        server_api.add_results_for_cases(test_run.get('id'), self.case_id, log)

    def __ui_record(self):
        self.test_case_id = self.data.get('test_case_id')
        self.grand_id = self.data.get('grand_id')
        self.platform = self.data.get('platform')
        self.packtype = self.data.get('packtype')
        self.app_version = self.data.get('app_version')
        self.app_url = server_api.get_latest_app(self.grand_id, self.platform, self.packtype, self.app_version)[
            'downloadURL']

        case_dir = 'sample/' + str(self.task_id) + '/' + str(self.test_case_id) + '.js'
        if self.app_url.endswith('apk'):
            app_url = self.app_url
        else:
            app_url = self.app_url.encode('utf-8').split('-')[0] + '.apk'

        logger.info('开始执行录制命令')
        session = shutit.create_session('bash')
        session.send('uirecorder --mobile', expect='测试脚本文件名', echo=True)
        session.send(case_dir, expect='App路径', echo=True)
        session.send(app_url, echo=True, check_exit=False)

        server_api.upload_case_file(self.test_case_id, open(case_dir, 'rb'))

    def __connect_devices(self):
        server_api.update_device_status(self.devices_id, DeviceStatus.busy.value)

    def __disconnect_devices(self):
        server_api.update_device_status(self.devices_id, DeviceStatus.online.value)

    def clear(self):
        logger.info('kill(%d)' % self.p_macaca.pid)
        os.killpg(os.getpgid(self.p_macaca.pid), signal.SIGTERM)
