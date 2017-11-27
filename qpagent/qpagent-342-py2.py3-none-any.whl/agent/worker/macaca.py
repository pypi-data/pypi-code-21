#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.worker.macaca
    ~~~~~~~~~~~~

    This module provide the macaca.

    :copyright: (c) 2017 by Ma Fei.
"""
import logging
import os
import shutil
import subprocess
import time

import shutit
from bs4 import BeautifulSoup

import agent.util.file as file_tool
from agent.consts import (
    TaskType,
    DeviceStatus
)
from agent.consts import TestRunStatus
from agent.qualityplatform import server_api
from agent.worker.base import BaseWorker
from agent.worker.iosmanage.package_manage import PackageManage

logger = logging.getLogger(__name__)

macaca_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/macaca/')


# todo 先完成iOS UIRecorder 再对代码进行重构
class Macaca(BaseWorker):
    def __init__(self, data):
        super(Macaca, self).__init__(data)
        self.devices_id = self.data.get('devices_id')
        self.platform = self.data.get('platform')
        self.package_manage = PackageManage()
        self.wkdir = macaca_dir + str(self.task_id)
        self.install_dir = self.wkdir + '/down_dir/'
        self.package_manage.workdir = self.install_dir

        logger.info('开始进入工作目录')
        file_tool.make_worker_dir(self.wkdir)

        os.chdir(self.wkdir)
        print macaca_dir
        logger.info('成功进入工作目录')

        logger.info('设置设备的状态')
        self.__connect_devices()

        logger.info('开始初始化uirecorder')
        # subprocess.call('uirecorder init --mobile', shell=True)

        session = shutit.create_session('bash')
        session.send('uirecorder init --mobile', expect='WebDriver域名或IP', echo=True)
        session.send('127.0.0.1', expect='WebDriver端口号', echo=True)
        session.send('4444', echo=True, check_exit=False)

    def start_worker(self):
        if self.task_type is TaskType.uiplay.value:
            logger.info('开始执行UI回放')
            self.__ui_play()
        elif self.task_type is TaskType.uirecord.value:
            logger.info('开始执行UI录制')
            self.__uirecord()

        self.__disconnect_devices()
        self.complete()

    def __manage_pack(self):
        print "__manage_pack"
        if self.platform == "iOS":
            grand_id = self.data.get('grand_id')
            platform = self.data.get('platform')
            packtype = self.data.get('packtype')
            app_version = self.data.get('app_version')

            self.app_url = server_api.get_latest_app(grand_id, platform, packtype, app_version)[
                'downloadURL']
            self.package_manage.downURL = self.app_url
            self.package_manage.down_app()  # 下载
            self.package_manage.resign()  # 重签名
            ipa = self.package_manage.workdir + self.package_manage.resinapp
            self.ios_app = self.package_manage.workdir + "ele.app"
            self.package_manage.outapp(ipa,self.ios_app)

    def __uirecord(self):
        self.__manage_pack()
        self.__ui_record()

    def __ui_play(self):
        case_url = self.data.get('case_url')
        case_id = self.data.get('case_id')
        project_id = self.data.get('project_id')
        app = server_api.get_latest_app('me.ele', 'Android', 'Release')
        test_run_data = {
            "name": "UI脚本回放_" + time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time())),
            "milestone_id": server_api.get_project_milestones(project_id)[0].get('id'),
            "description": "{'type': 'ui_play'}",
            "include_all": False,
            "case_ids": [case_id]
        }
        test_run = server_api.add_project_run(project_id, test_run_data)

        case_dir = 'task'
        file_name = str(self.task_id) + '.js'

        file_tool.save_file(case_url, case_dir, file_name)

        os.chdir(macaca_dir)
        shutil.rmtree('reports')
        subprocess.call('source run.sh ' + case_dir + '/' +
                        file_name, shell=True)

        self.upload('reports', str(self.task_id))
        fp = open(macaca_dir + "reports/index.html")
        soup = BeautifulSoup(fp, 'html.parser')
        fail_count = soup.findAll("li", class_="suite-summary-item failed")[0].string
        if fail_count != '0':
            test_run_status = TestRunStatus.failed.value
        else:
            test_run_status = TestRunStatus.passed.value
        log = 'http://10.12.38.246:8000/report/' + str(self.task_id) + '/index.html'
        server_api.add_results_for_cases(test_run.get('id'), case_id, log, test_run_status, app)

    def __ui_record(self):
        test_case_id = self.data.get('test_case_id')
        case_dir = 'sample/' + str(self.task_id) + '/' + str(test_case_id) + '.js'

        if self.platform == "iOS":
            self.app_url = self.ios_app
        else:
            grand_id = self.data.get('grand_id')
            platform = self.data.get('platform')
            packtype = self.data.get('packtype')
            app_version = self.data.get('app_version')
            self.app_url = server_api.get_latest_app(grand_id, platform, packtype, app_version)[
                'downloadURL']
            if self.app_url.endswith('apk'):
                pass
            else:
                self.app_url = self.app_url.encode('utf-8').split('-')[0] + '.apk'

        logger.info('开始执行录制命令')
        # subprocess.call('uirecorder --mobile', shell=True)



        session = shutit.create_session('bash')
        session.send('uirecorder --mobile', expect='测试脚本文件名', echo=True)
        session.send(case_dir, expect='App路径', echo=True)
        session.send(self.app_url, echo=True, check_exit=False)
        server_api.upload_case_file(test_case_id, open(case_dir, 'rb'))

    def __connect_devices(self):
        server_api.update_device_status(self.devices_id, DeviceStatus.busy.value)

    def __disconnect_devices(self):
        server_api.update_device_status(self.devices_id, DeviceStatus.online.value)

    def clear(self):
        pass
