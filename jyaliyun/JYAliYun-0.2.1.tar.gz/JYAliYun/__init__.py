#! /usr/bin/env python
# coding: utf-8

import os

__author__ = 'ZhouHeng'

P_NAME = "JY_ALY"
LONG_P_NAME = "JY_ALIYUN"

AliYUN_DOMAIN_NAME = "aliyuncs.com"

# 时间相关
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
UTC_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Content-Type相关
XML_CONTENT = "text/xml;charset=utf-8"


# logging相关
DEFAULT_LOGGER_NAME = "JY_ALIYUN_SDK"
LOG_MSG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

# 环境相关
HOSTNAME = os.environ.get("HOSTNAME", "")
