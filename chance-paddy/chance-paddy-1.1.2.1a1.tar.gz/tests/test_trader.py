#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: tests/unit/test_trader.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017
import logging

from mock_logger import MockLoggingHandler
from nose.tools import assert_equals, assert_raises

from paddy import Trader
from paddy.constant import TRADE_TEST
from paddy.exceptions import ExecutedException
from paddy.mode.test_trader import Trader as TestTrader


HANDLER = MockLoggingHandler(level='DEBUG')


def test_Trader_init():
    """Check if ``Trader.__init__`` works
    """
    logger = logging.getLogger('Trader')
    logger.addHandler(HANDLER)
    trader = Trader(TRADE_TEST)

    assert isinstance(trader._trader, TestTrader)
    assert_equals(trader.mode, TRADE_TEST)
    assert_equals(
        HANDLER.messages['info'],
        [
            'Initialize trader as test_trader successful',
            'Initialize arguments: None'
        ]
    )


def test_Trader_not_allowed_methods():
    """Check if ``Trader`` raised Exception when methods not allowed
    """
    trader = Trader(TRADE_TEST)
    assert_raises(ExecutedException, getattr, trader, 'test')


def test_Trader_allowed_methods():
    """Check if ``Trader`` works when methods allowed
    """
    trader = Trader(TRADE_TEST)
    assert_equals(trader.get_account(), 'test')
