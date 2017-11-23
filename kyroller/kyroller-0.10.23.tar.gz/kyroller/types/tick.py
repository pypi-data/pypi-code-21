#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-21 01:40:32
# Author: xujif
# -----
# Last Modified: 2017-08-03 11:13:54
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###

import json
import time
from ..utils import js_float, js_int


class Tick:
    def __str__(self):
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)

    def __init__(self, quotation_string):
        sp = quotation_string.split(',')
        self.symbol = sp[0]
        self.market = sp[0][:2]
        self.code = sp[0][2:]
        self.name = sp[1]
        self.timestamp = js_int(sp[2])
        self.preclose_backadj = js_float(sp[3])
        upper_limit = js_float(sp[4])
        if(upper_limit > 0):
            self.upper_limit = upper_limit
        else:
            self.upper_limit = round(self.preclose_backadj * 1.1, 2)

        lower_limit = js_float(sp[5])
        if(lower_limit > 0):
            self.lower_limit = lower_limit
        else:
            self.lower_limit = round(self.preclose_backadj * 0.9, 2)

        self.open = js_float(sp[6])
        self.high = js_float(sp[7])
        self.low = js_float(sp[8])
        self.price = js_float(sp[9])
        self.volume = js_int(sp[10])
        self.amount = js_float(sp[11])
        self.ask_volume = js_int(sp[12])
        self.bid_volume = js_int(sp[13])
        self.total_trades = js_int(sp[14])
        self.order_num = js_int(sp[15])
        self.status = sp[16]
        self.asks = []
        self.bids = []
        order_num = self.order_num
        for i in range(0, order_num * 2, 2):
            self.bids.append({
                "volume": js_int(sp[17 + i]),
                "price": js_float(sp[18 + i])
            })
        for i in range(0, order_num * 2, 2):
            self.asks.append({
                "volume": js_int(sp[17 + order_num * 2 + i]),
                "price": js_float(sp[18 + order_num * 2 + i])
            })

    def __getitem__(self, key):
        if key == 'date':
            return self.date
        if key == 'time':
            return self.time
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
