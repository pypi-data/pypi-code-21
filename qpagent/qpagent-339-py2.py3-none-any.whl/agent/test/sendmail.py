#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime, timedelta
import agent.qualityplatform.api as server_api
from agent.consts import TaskType
## 兼容性测试
if __name__ == '__main__':
    app = server_api.get_latest_app('me.ele.ios.eleme', 'iOS', 'Release')
    # server_api.send_mail('waimai.qa.platform@ele.me,waimai.mobile.platform@ele.me,waimai.qa@ele.me,hongbo.tang@ele.me',
    #                      '阿里云测报告', '饿了么ios_兼容性测试_阿里云测', app,
    #                      'http://mqc.aliyun.com/report.htm?executionId=393713&shareCode=YuW2YKPbUZws',
    #                      'test_report.html')
