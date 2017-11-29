#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from agent.exc import WorkerException
import commands
import agent.util.file as file_tool
import logging
import subprocess
import time


class PackageManage(object):
    def __init__(self):
        self.dir = os.path.dirname(__file__)
        self.developer_cer = 'iPhone Developer: lanping wang (N347ANRGLA)'
        self.qpagent_bundleid = 'me.ele.ios.qpagent'
        self.eleme_bundleid = 'me.ele.ios.eleme'
        self.workdir = os.getcwd() + "/"
        self.dowingapp = "dowing.ipa"
        self.resinapp = 'eleqpagent.ipa'
        self.downURL = ""
        self.resignsh = self.dir + "/resign.sh"
        self.qpagent_provision = self.dir + '/me.mobileprovision'  # qpagent.me.ele.ios.eleme

        # todo 暂时所有的操作是使用重签名的包和bundleID，即所有的操作使用重签名之后的包。后期更新
        self.bundleId = self.qpagent_bundleid

    def down_app(self):
        if self.downURL.count <= 0:
            logging.warning("dowingURL is empty")
            raise WorkerException('dowingURL is empty')
        logging.info("downing ipa。URL:%s path: %s。 " % (self.downURL.encode('UTF-8'), self.workdir + self.dowingapp))
        file_tool.save_file(self.downURL, self.workdir, self.dowingapp)
        time.sleep(3)
        if not os.path.exists(self.workdir + self.dowingapp):
            raise WorkerException('down app fail')
        else:
            logging.info("down success")

    def install_app(self, udid):
        print "begin install app"
        resigned_ipa = self.workdir + self.resinapp
        install_cmd = "ideviceinstaller -u %s -i %s" % (udid, resigned_ipa)
        print "begin install app " + install_cmd
        status, output = commands.getstatusoutput(install_cmd)
        logging.info(output)
        time.sleep(3)
        logging.info("install app success")

    def uninstall_app(self, udid):
        logging.info("uninstall app")
        uninstall_cmd = "ideviceinstaller -u %s -U %s" % (udid, self.bundleId)
        status, output = commands.getstatusoutput(uninstall_cmd)
        logging.warning(output)
        if output.find("Complete") != -1:
            logging.info(self.bundleId + " uninstall success")
        time.sleep(3)
        logging.info("uninstall app success")

    def outapp(self, ipa, app):
        status, out = commands.getstatusoutput("dirname " + ipa)
        cmd1 = "unzip -qo %s -d %s;cp -R %s/temp/Payload/*.app %s;rm -R %s" % (
            ipa, out + "/temp", out, app, out + "/temp")
        print cmd1
        subprocess.call(cmd1, shell=True)
        print out
        time.sleep(3)
        # 检查是否获取成功
        if not os.path.exists(app):
            raise WorkerException(app + ' not exist')
            return
        else:
            logging.info("output app success")

    # 重签名
    def resign(self):
        donwing_ipa = self.workdir + self.dowingapp
        resigned_ipa = self.workdir + self.resinapp

        logging.info("resign ipa: %s; use provision:%s; bundle:%s" % (
            donwing_ipa, self.qpagent_provision, self.bundleId))
        # 检查是否下载成功
        if not os.path.exists(donwing_ipa):
            raise WorkerException(donwing_ipa + ' not exist')
            return

        # 如果当前文件夹有相同名字的ipa 删除掉
        if os.path.exists(resigned_ipa):
            dele_cmd = "rm " + resigned_ipa
            commands.getstatusoutput(dele_cmd)

        resgin_cmd = 'bash %s -s %s -c \'%s\' -p %s -i %s -o %s -n %s' % (self.resignsh,
                                                                          donwing_ipa, self.developer_cer,
                                                                          self.qpagent_provision, self.bundleId,
                                                                          self.workdir,
                                                                          self.resinapp)
        logging.info(resgin_cmd)
        commands.getstatusoutput(resgin_cmd)

        if not os.path.exists(resigned_ipa):
            raise WorkerException(resigned_ipa + ' resigned fail')
        else:
            logging.info("resigned success")
        return resigned_ipa
