#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-14 12:06:52
# Author: xujif
# -----
# Last Modified: 2017-08-16 10:39:58
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###
from abc import abstractmethod
from enum import Enum, unique
import time
import random
from functools import reduce
from datetime import datetime


class State(dict):
    def __getattribute__(self, name):
        if name not in self:
            return None
        else:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value


class IncorrectDataException(Exception):
    pass


@unique
class Exchange(Enum):
    SH = 0
    SZ = 1


@unique
class MarketStatus(Enum):
    '''
        PQ 开盘前
        KJ 开盘竞价
        PZ 盘中
        WX 午休
        CJ 收盘集合竞价
        PH 盘后
        ND 新的一天，回测中会用到
    '''
    PQ = 0
    KJ = 5
    PZ = 10
    WX = 15
    CJ = 20
    PH = 25
    ND = 1000


class MarketEvent:
    def __str__(self):
        return 'exchange: %s, timestamp: %s,_status: %s' % (self.exchange, datetime.fromtimestamp(self.timestamp), self._status.name)

    def __init__(self, exchange, timestamp, market_status):
        self._exchange = exchange
        self._timestamp = timestamp
        self._status = MarketStatus[market_status]

    @property
    def exchange(self)->Exchange:
        return self._exchange

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def status(self)->MarketStatus:
        return self._status


class OrderSide(Enum):
    '''
    BID:买
    ASK:卖
    N:未标明（只在订单记录中出现，创建委托单请勿使用）
    '''
    N = 0
    BID = 1
    ASK = 2


class OrderType(Enum):
    '''
    委托单类型：
        LIMIT: 限价委托
        BOC : 对方最优价格(best of counterparty)
        BOP: 己方最优价格(best of party)
        B5TC: 最优五档剩余撤销(best 5 then cancel)
        B5TL: 最优五档剩余转限价(best 5 then limit)
        IOC: 即时成交剩余撤销(immediately or cancel)
        FOK: 即时全额成交或撤销(fill or kill)
        AON: 全额成交或不成交(all or none)
        MTL: 市价剩余转限价(market then limit)
    '''
    LIMIT = 0
    BOC = 1
    BOP = 2
    B5TC = 3
    B5TL = 4
    IOC = 5
    FOK = 6
    AON = 7
    MTL = 8


class OrderStatus(Enum):
    '''
    委托单状态：
        WAITING_TO_ORDER: 未报
        ORDER_PENDING: 报单中（已到达柜台或者券商，未发送到交易所）
        CONFIRMED: 已报单,待交易所处理
        PART_FILLED：部分成交
        ALL_FILLED：全部成交
        REJECTED：废单（风控系统拒绝）
        REJECTED_T：废单（券商或者交易所拒绝，余额不足或者价格错误等）
        CANCELED：已被撤单(全部撤单)
        PART_CANCELED : 已撤单（部分已成交）

    '''
    WAITING_TO_ORDER = 0
    ORDER_PENDING = 5
    CONFIRMED = 10
    PART_FILLED = 20
    ALL_FILLED = 25
    REJECTED = -10
    PART_CANCELED = -20
    CANCELED = -25
