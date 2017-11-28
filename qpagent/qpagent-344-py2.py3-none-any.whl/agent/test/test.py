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
from agent.worker.macaca import Macaca

if __name__ == '__main__':
    # data = {u'devices_id': u'199ce7e631ef60de8b6702e8142c1f8af3073205', u'worker_type': 1, u'packtype': u'Release',
    #         u'ip': u'10.12.54.132', u'port': 9099, u'platform': u'iOS', u'case_id': 1142839,
    #         u'grand_id': u'me.ele.ios.eleme',
    #         u'app_version': u'7.20', u'test_case_id': 65}
    macaca = Macaca("122620")
    macaca.start_worker()