#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-20 04:22:41
# Author: xujif
# -----
# Last Modified: 2017-08-03 11:12:19
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###

import json
import time
from ..utils import js_float, js_int


class Bar:
    def __str__(self):
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)

    def __init__(self, barString):
        sp = barString.split(',')
        self.symbol = sp[0]
        self.market = sp[0][:2]
        self.code = sp[0][2:]
        self.timestamp = js_int(sp[1])
        self.preclose_backadj = js_float(sp[2])
        self.open = js_float(sp[3])
        self.high = js_float(sp[4])
        self.low = js_float(sp[5])
        self.close = js_float(sp[6])
        self.price = js_float(sp[6])
        self.volume = js_int(sp[7])
        self.amount = js_float(sp[8])
        self.period = js_int(sp[9])

    def __getitem__(self, key):
        return self.__dict__[key]

    @property
    def date(self):
        if '_date' in self.__dict__:
            return self._date
        else:
            timeArray = time.localtime(self.timestamp)
            self._time = time.strftime("%H:%M:%S", timeArray)
            self._date = time.strftime("%Y-%m-%d", timeArray)
            return self._date

    @property
    def time(self):
        if '_time' in self.__dict__:
            return self._time
        else:
            timeArray = time.localtime(self.timestamp)
            self._time = time.strftime("%H:%M:%S", timeArray)
            self._date = time.strftime("%Y-%m-%d", timeArray)
            return self._time
