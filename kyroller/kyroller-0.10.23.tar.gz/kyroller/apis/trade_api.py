#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-21 01:35:12
# Author: xujif
# -----
# Last Modified: 2017-06-21 06:08:35
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###


from ..types import Order


class TradeApi:

    def mk_order(self, order):
        pass


class MockTradeApi:
    def __init__(self):
        self.order_map = {}

    def mk_order(self, order: Order):
        self.order_map[order.cid] = order
