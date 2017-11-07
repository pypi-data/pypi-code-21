#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: tests/test_account.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017
from nose.tools import assert_almost_equals

from paddy.models.account import Account


def test_Account():
    """Check if ``Account`` works
    """
    fake_value = {
        'total_asset': 100.0, 'stock_asset': 100.0,
        'hold_stock': {'000001': 100.0}
    }
    account = Account(**fake_value)

    for key, value in fake_value.items():
        assert_almost_equals(getattr(account, key), value)
