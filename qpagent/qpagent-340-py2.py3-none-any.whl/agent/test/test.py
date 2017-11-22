#!/usr/bin/env python
# -*- coding: utf-8 -*-

from agent.worker.ios_monkey import iosmonkey
# from agent.worker.ios_appcrawler import Appcrawler
# import json
import commands
from agent.exc import WorkerException
import logging
import subprocess
import os
import time
from appium import webdriver

if __name__ == '__main__':
    downURL = 'http: // download.ele.me / ios_8ab5a2a700862a598ba4f82c5bc677ea.ipa'
    workdir = '/ Users / ztcq / Documents / ele / qualityplatform.agent / agent / agent / iosMonkey / 121090 / down_dir /'
    dowingapp = "dowing.ipa"

    logging.info("downing ipa。URL:%s path: %s。" % (downURL, workdir + dowingapp))
    #
    # data = {"worker_type": 5, "ip": "10.12.54.235", "port": 9096,
    #         "device_id": "199ce7e631ef60de8b6702e8142c1f8af3073205", "notice_account": "['waimai.qa.platform@ele.me']",
    #         "app_version": "7.11", "grand_id": "me.ele.ios.eleme", "platform": "iOS", "packtype": "Debug",
    #         "throttle": 300, "pct_touch": 30, "pct_motion": 30, "pct_syskeys": 5}
    # monkey = iosmonkey(data)
    # monkey.device_name = "iPod touch"
    # monkey.udid = "199ce7e631ef60de8b6702e8142c1f8af3073205"
    # monkey.wdadir = "/Users/ztcq/Documents/ele/qualityplatform.agent/agent/agent/iosMonkey/Fastmonkey/XCTestWD-master/XCTestWD/XCTestWD.xcodeproj"
    # monkey.throttle = 500
    # monkey.pct_touch = 500
    # monkey.pct_syskeys = 500
    # monkey.pct_motion = 500
    # monkey.start_worker()
    # monkey.device_ip = "http://10.12.56.32:8100"
    # monkey.start_WDATest()
    print "monkeyendend"
    # monkey.start_runmonkey()

    # crawler.start_appiumserver()
    # crawler.start_crawler()
