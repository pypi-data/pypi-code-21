#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from agent.worker.ios_monkey import iosmonkey
# from agent.worker.ios_appcrawler import Appcrawler
# import json
import commands
from agent.exc import WorkerException
import logging
import subprocess


class test():
    def __init__(self):
        self.udid = "199ce7e631ef60de8b6702e8142c1f8af3073205"
        self.install_dir = "/Users/ztcq/Documents/ele/qualityplatform.agent/agent/agent/iosMonkey/117665/install_dir"
        self.bundleId = "com.ele.ios.eleme"

    def install_app(self):
        install_cmd = "ideviceinstaller -u %s -i %s" % (self.udid, self.install_dir + '/eleme_ios.ipa')
        status, output = commands.getstatusoutput(install_cmd)
        logging.warning(output)
        if output.find("Complete") != -1:
            print (self.bundleId + " install success")
            return True
        logging.warning(self.bundleId + " install not success")
        # raise WorkerException('install app fail')


    def uninstall_app(self):
        print "uninstall_app"
        uninstall_cmd = "ideviceinstaller -u %s -U %s" % (self.udid, self.bundleId)
        status, output = commands.getstatusoutput(uninstall_cmd)
        logging.warning(output)
        if output.find("Complete", 0, len(output)):
            print(self.bundleId + " uninstall success")
            return True
        logging.warning(self.bundleId + " uninstall not success")
        # raise WorkerException('uninstall app fail')

if __name__ == '__main__':
    out = subprocess.check_output(["ideviceinstaller","-u","199ce7e631ef60de8b6702e8142c1f8af3073205","-i","eleme_ios.ipa"])

    # out = subprocess.check_output("ideviceinstaller -u 199ce7e631ef60de8b6702e8142c1f8af3073205 -i eleme_ios.ipa")
    print out
    # str = {"worker_type":5}
    # str = '{"worker_type":5,"ip":"10.12.38.246","port":9099,"device_id":"199ce7e631ef60de8b6702e8142c1f8af3073205","notice_account":"['tianchen.zhang@ele.me']","app_version":"7.20","grand_id":"me.ele.ios.eleme","platform":"iOS","packtype":"Debug","throttle":300,"pct_touch":30,"pct_motion":30,"pct_syskeys":5}'
    # data = json.load(str)
    # print  data


    # data = {"params":{'task_id':999,'notice_account':'tianchen.zhang@ele.me','device_id':'32575086c794e341f59e03799f5d8164ad157c1d','app_url':'http://download.ele.me/ios_864c0e2a6dc234c2900a05bb490e6e79.ipa','port':'9096'}}
    # print data
    #
    # crawler = Appcrawler(data)
    # crawler.start_worker()

    # monkey = test()
    # monkey.uninstall_app()
    # monkey.install_app()




    # monkey.data = data
    # monkey.udid = '32575086c794e341f59e03799f5d8164ad157c1d'
    # monkey.search_key = 'Integration'
    # monkey.notice_account = 'tianchen.zhang@ele.me'
    # monkey.get_deviceName()
    # monkey.start_WDATest()
    # monkey.deal_report()