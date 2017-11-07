#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2017 TUNE, Inc. (http://www.tune.com)
#  @namespace tune_reporting

import sys

from tune_reporting import (__version__, __title__)

__MODULE_VERSION_INFO__ = tuple(__version__.split('.'))
__MODULE_SIG__ = "%s/%s" % (__title__, __version__)

__TIMEZONE_NAME_DEFAULT__ = "UTC"

__PYTHON_VERSION__ = 'Python/%d.%d.%d' % (sys.version_info[0], sys.version_info[1], sys.version_info[2])

__USER_AGENT__ = "({}, {})".format(__MODULE_SIG__, __PYTHON_VERSION__)

__LOGGER_NAME__ = __name__.split('.')[0]

HEADER_CONTENT_TYPE_APP_JSON = \
    {'Content-Type': 'application/json'}

HEADER_CONTENT_TYPE_APP_URLENCODED = \
    {'Content-Type': 'application/x-www-form-urlencoded'}

HEADER_USER_AGENT = \
    {'User-Agent': __USER_AGENT__}
