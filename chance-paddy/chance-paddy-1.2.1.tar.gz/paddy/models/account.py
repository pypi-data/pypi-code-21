#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: models/account.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017


class Account(object):
    """Model class for ``account``
    """
    _total_asset = None
    _stock_asset = None
    _hold_stock = None

    def __init__(self, total_asset=None, stock_asset=None, hold_stock=None):
        self._total_asset = total_asset
        self._stock_asset = stock_asset
        self._hold_stock = hold_stock

    @property
    def total_asset(self):
        return self._total_asset

    @property
    def stock_asset(self):
        return self._stock_asset

    @property
    def hold_stock(self):
        return self._hold_stock
