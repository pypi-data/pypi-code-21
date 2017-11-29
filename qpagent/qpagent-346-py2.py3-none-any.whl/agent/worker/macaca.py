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

import shutit

import agent.util.file as file_tool
from agent.consts import (
    TaskType
)
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
        file_tool.make_worker_dir(self.wkdir)
        self.package_manage.workdir = self.install_dir

        logger.info('开始进入工作目录')

        os.chdir(self.wkdir)
        print macaca_dir
        logger.info('成功进入工作目录')

    def start_worker(self):
        if self.task_type is TaskType.uirecord.value:
            logger.info('开始执行UI录制')
            self.__manage_pack()
            self.__ui_record()

        self.complete()

    def __manage_pack(self):
        print "__manage_pack"
        if self.platform == "iOS":
            if self.task_type is TaskType.uiplay.value:
                self.appurl = server_api.get_latest_app('me.ele.ios.eleme', 'iOS', 'Release')['downloadURL']
            else:
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
            self.package_manage.outapp(ipa, self.ios_app)

    def __ui_record(self):
        test_case_id = self.data.get('test_case_id')
        case_dir = 'sample/' + str(self.task_id) + '/' + str(test_case_id) + '.js'
        print case_dir
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

        session = shutit.create_session('bash')
        session.send('uirecorder --mobile', expect='测试脚本文件名', echo=True)
        session.send(case_dir, expect='App路径', echo=True)
        session.send(self.app_url, echo=True, check_exit=False)
        print "UIRecord 结束"

    def clear(self):
        pass
