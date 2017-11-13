#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from agent.worker.ios_monkey import iosmonkey
# from agent.worker.ios_appcrawler import Appcrawler
# import json
import commands
from agent.exc import WorkerException
import logging
import subprocess
import os
import time

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


    def start_appiumserver(self):
        print "start_appiumserver"
        self.p_appium = subprocess.Popen("appium --session-override", stdout=subprocess.PIPE, shell=True,
                                         preexec_fn=os.setsid)
        time.sleep(5)

    def start_crawler(self):
        print "start_crawler"
        subprocess.call(
            'java -jar /Users/ztcq/Documents/git/appcrawler/appcrawler-2.1.2.jar   -c /Users/ztcq/Documents/git/appcrawler/conf/eleme_ios.yaml ',
            shell=True)


if __name__ == '__main__':
    crawler = test()
    crawler.start_appiumserver()
    crawler.start_crawler()