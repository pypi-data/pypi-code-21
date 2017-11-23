#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Created Date: 2017-06-20 05:23:38
# Author: xujif
# -----
# Last Modified: 2017-08-21 11:54:25
# Modified By: xujif
# -----
# Copyright (c) 2017 上海时来信息科技有限公司
###
from .types import *
from datetime import datetime
import random
import time


class Order:

    @staticmethod
    def gen_cid():
        return datetime.now().strftime('o%Y%m%d%H%M%S') + str(random.randrange(1000000, 9999999))

    def __str__(self):
        return 'cid: %s, side: %s,type: %s,volume: %d, price: %.2f' % (self.cid, self.order_side.name, self.order_type.name, self.volume, self.price)

    def __init__(self, cid=None):
        self._cid = cid if cid is not None else Order.gen_cid()
        self._filled_amount = 0
        self._filled_volume = 0
        self._frozen_money = 0
        self._frozen_volume = 0
        self._status = OrderStatus.WAITING_TO_ORDER
        self._volume = 0
        self._exchange = 'sz'
        self._side = OrderSide.ASK
        self._create_time = time.time()
        self._order_type = OrderType.LIMIT
        self._symbol = ''
        self._account_id = ''

    @property
    def account_id(self):
        '''
        账号id
        '''
        return self._account_id

    @account_id.setter
    def account_id(self, value):
        self._account_id = value

    @property
    def frozen_volume(self):
        return self._frozen_volume

    @frozen_volume.setter
    def frozen_volume(self, value):
        self._frozen_volume = value

    @property
    def symbol(self):
        '''
        当前订单股票代码
        '''
        return self._symbol

    @property
    def frozen_money(self):
        '''
        当前订单冻结的金额
        '''
        return self._frozen_money

    @frozen_money.setter
    def frozen_money(self, value):
        self._frozen_money = value

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def strategy_id(self)->str:
        '''
        订单所属的策略id
        '''
        return self._strategy_id

    @strategy_id.setter
    def strategy_id(self, value):
        self._strategy_id = value

    # 流水号相关
    @property
    def cid(self)->str:
        return self._cid

    @cid.setter
    def cid(self, value):
        self._cid = value

    @property
    def oid(self)->str:
        return self._oid

    @oid.setter
    def oid(self, value):
        self._oid = value

    @property
    def ex_id(self)->str:
        return self._ex_id

    @ex_id.setter
    def ex_id(self, value):
        self._ex_id = value

    @property
    def reject_reason(self)->str:
        return self._reject_reason

    @reject_reason.setter
    def reject_reason(self, value):
        self._reject_reason = value

    @property
    def exchange(self)->Exchange:
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        self._exchange = value

    @property
    def side(self)->OrderSide:
        return self._side

    @side.setter
    def side(self, value):
        self._side = value

    @property
    def order_side(self)->OrderSide:
        return self._side

    @order_side.setter
    def order_side(self, value):
        self._side = value

    @property
    def order_type(self)->OrderType:
        return self._order_type

    @order_type.setter
    def order_type(self, value):
        self._order_type = value

    @property
    def volume(self)->int:
        return self._volume

    @volume.setter
    def volume(self, value: int):
        self._volume = value

    @property
    def price(self)->float:
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def filled_volume(self)->int:
        return self._filled_volume

    @filled_volume.setter
    def filled_volume(self, value):
        self._filled_volume = value

    @property
    def filled_amount(self)->int:
        return self._filled_amount

    @filled_amount.setter
    def filled_amount(self, value):
        self._filled_amount = value

    @property
    def avg_filled_price(self):
        return self._filled_amount / self.filled_volume

    # 时间
    @property
    def create_time(self)->int:
        '''
        订单创建时间
        '''
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        return self._create_time

    @property
    def status(self) -> OrderStatus:
        '''
        订单状态
        '''
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
