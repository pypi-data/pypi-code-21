#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: tests/test_trady_easy.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017
import arrow
import json
import logging
import mock
import requests

from decimal import Decimal
from mock_logger import MockLoggingHandler
from nose.tools import assert_almost_equals, assert_equals, assert_raises
from requests.exceptions import HTTPError

from paddy.constant import (
    FAKE_ACCOUNT_RESPONSE, FAKE_ENTRUST_RESPONSE,
    FAKE_CANCELLABLE_ENTRUSTS_RESPONSE, SLEEP_TIME, MAX_REQUEST
)
from paddy.exceptions import ExecutedException, CycleCancelFailedException
from paddy.mode.trade_easy import (
    cycle_wait, Trader, response_to_account, LOGGER, response_to_entrusts
)
from paddy.models.entrust import Entrust


HANDLER = MockLoggingHandler(level='DEBUG')


def setup_module():
    LOGGER.addHandler(HANDLER)


class TestCycleWait(object):
    """Test class for ``trade_easy.cycle_wait``
    """
    def setUp(self):
        HANDLER.reset()

    def test_normal(self):
        """Check if ``trade_easy.cycle_wait`` works
        """
        @cycle_wait
        def normal(temp):
            pass

        start_time = arrow.now()
        normal('test')
        end_time = arrow.now()
        assert_equals((end_time - start_time).seconds, SLEEP_TIME)

    def test_raise_exception(self):
        """Check if ``trade_easy.cycle_wait`` works when exception raised
        """
        @cycle_wait
        def normal(temp):
            raise HTTPError()

        start_time = arrow.now()
        assert_raises(ExecutedException, normal, 'test')
        end_time = arrow.now()
        assert_equals(
            (end_time - start_time).seconds, SLEEP_TIME * MAX_REQUEST
        )
        assert_equals(HANDLER.messages['error'], ['', '', ''])


def test_response_to_account():
    """Check if ``trade_easy.response_to_account`` works
    """
    expect_results = {
        'total_asset': Decimal(367.94999999999999),
        'stock_asset': Decimal(245),
        'hold_stock': {
            '600022': Decimal(245.000), '000001': Decimal(1100.000)
        }
    }

    result = response_to_account(FAKE_ACCOUNT_RESPONSE)

    for key, value in expect_results.items():
        assert_almost_equals(getattr(result, key), value)


def test_response_to_entrusts():
    """Check if ``trade_easy.response_to_entrust`` works
    """
    expect_results = [
        {
            'stock_id': '600022', 'price': Decimal(2.540), 'volume': 100,
            'entrust_no': '10381', 'status': 1
        },
        {
            'stock_id': '600022', 'price': Decimal(0.000), 'volume': 0,
            'entrust_no': '10775', 'status': 3
        }
    ]

    results = response_to_entrusts(FAKE_ENTRUST_RESPONSE)
    for expect_result, result in zip(expect_results, results):
        for key, value in expect_result.items():
            assert_almost_equals(getattr(result, key), value)


class TestTrader(object):
    """Test class for ``trade_easy.Trader``
    """
    def setUp(self):
        logger = logging.getLogger(Trader.__name__)
        logger.addHandler(HANDLER)
        HANDLER.reset()
        self.trader = Trader({'host': '192.168.0.1:8080'})
        self.content = "response content"

    def test_init(self):
        """Check if ``trade_easy.Trader.__init__`` works
        """
        assert_equals(self.trader.host, '192.168.0.1:8080')
        assert_equals(HANDLER.messages['info'], ['Read trade easy arguments'])

    @mock.patch.object(requests, 'get')
    def test_get_account(self, mock_get):
        """Check if ``trade_easy.Trader.get_account`` works

        Args:
            mock_get: mock object of ``requests.get``
        """
        mock_get.return_value.json.return_value = FAKE_ACCOUNT_RESPONSE
        expect_results = {
            'total_asset': Decimal(367.94999999999999),
            'stock_asset': Decimal(245),
            'hold_stock': {
                '600022': Decimal(245.000), '000001': Decimal(1100.000)
            }
        }
        mock_get.return_value.content = self.content
        start_time = arrow.now()
        result = self.trader.get_account()
        end_time = arrow.now()

        assert_equals((end_time - start_time).seconds, SLEEP_TIME)
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'Successfully get account info'
            ]
        )

        for key, value in expect_results.items():
            assert_almost_equals(getattr(result, key), value)

    @mock.patch.object(requests, 'get')
    def test_get_account_raise_exception(self, mock_get):
        """Check if ``trade_easy.Trader.get_account`` raises Exception

        Args:
            mock_get: mock object of ``requests.get``
        """
        mock_get.return_value.raise_for_status.side_effect = HTTPError()
        mock_get.return_value.content = self.content

        start_time = arrow.now()
        assert_raises(ExecutedException, self.trader.get_account)
        end_time = arrow.now()

        assert_equals(
            (end_time - start_time).seconds, SLEEP_TIME * MAX_REQUEST
        )
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'response content', 'response content'
            ]
        )
        assert_equals(HANDLER.messages['error'], ['', '', ''])

    @mock.patch.object(requests, 'get')
    def test_get_all_entrusts(self, mock_get):
        """Check if ``trade_easy.Trader.get_all_entrusts

        Args:
            mock_get:mock object of ``requests.get``
        """
        mock_get.return_value.json.return_value = FAKE_ENTRUST_RESPONSE
        mock_get.return_value.content = self.content
        expect_results = [
            {
                'stock_id': '600022', 'price': Decimal(2.540), 'volume': 100,
                'entrust_no': '10381', 'status': 1
            },
            {
                'stock_id': '600022', 'price': Decimal(0.000), 'volume': 0,
                'entrust_no': '10775', 'status': 3
            }
        ]
        start_time = arrow.now()
        results = self.trader.get_all_entrusts()
        end_time = arrow.now()

        assert_equals((end_time - start_time).seconds, SLEEP_TIME)
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'Successfully get entrust info'
            ]
        )
        assert_equals(len(results), len(expect_results))
        for each_result, each_expect_result in zip(results, expect_results):
            for key, value in each_expect_result.items():
                assert_almost_equals(getattr(each_result, key), value)

    @mock.patch.object(requests, 'get')
    def test_get_all_entrusts_raise_exception(self, mock_get):
        """Check if ``trade_easy.Trader.get_account`` raises Exception

        Args:
            mock_get: mock object of ``requests.get``
        """
        mock_get.return_value.raise_for_status.side_effect = HTTPError()
        mock_get.return_value.content = self.content
        start_time = arrow.now()
        assert_raises(ExecutedException, self.trader.get_all_entrusts)
        end_time = arrow.now()

        assert_equals(
            (end_time - start_time).seconds, SLEEP_TIME * MAX_REQUEST
        )
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'response content', 'response content'
            ]
        )
        assert_equals(HANDLER.messages['error'], ['', '', ''])

    @mock.patch.object(requests, 'delete')
    def test_cancel_all_entrusts(self, mock_delete):
        """Check if ``trade_easy.Trader.cancel_all_entrusts`` works

        Args:
            mock_delete: mock object of ``requests.delete``
        """
        mock_delete.return_value.content = self.content
        start_time = arrow.now()
        result = self.trader.cancel_all_entrusts()
        end_time = arrow.now()

        mock_delete.assert_called_with('192.168.0.1:8080/orders')

        assert_equals((end_time - start_time).seconds, SLEEP_TIME)
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'Successfully delete all orders'
            ]
        )
        assert_equals(result, True)

    @mock.patch.object(requests, 'delete')
    def test_cancel_all_entrusts_raises_exception(self, mock_delete):
        """Check if ``trade_easy.Trader.cancel_all_entrusts`` raises Exception

        Args:
            mock_delete: mock object of ``requests.delete``
        """
        mock_delete.return_value.raise_for_status.side_effect = HTTPError()
        mock_delete.return_value.content = self.content
        start_time = arrow.now()
        assert_raises(ExecutedException, self.trader.cancel_all_entrusts)
        end_time = arrow.now()

        mock_delete.assert_called_with('192.168.0.1:8080/orders')

        assert_equals(
            (end_time - start_time).seconds, SLEEP_TIME * MAX_REQUEST
        )
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'response content', 'response content'
            ]
        )
        assert_equals(HANDLER.messages['error'], ['', '', ''])

    @mock.patch.object(requests, 'post')
    def test_execute_entrust(self, mock_post):
        """Check if ``trade_easy.Trader.execute_entrust`` works

        Args:
            mock_post: mock object of ``requests.post``
        """
        mock_post.return_value.json.return_value = {
            "id": "11106", "action": "BUY", "symbol": "test", "priceType": "0",
            "price": 0.01, "amountProportion": "", "amount": 100
        }
        mock_post.return_value.content = self.content
        start_time = arrow.now()
        result = self.trader.execute_entrust('BUY', 'test', 0.01, 100)
        end_time = arrow.now()

        mock_post.assert_called_with(
            '192.168.0.1:8080/orders',
            data=json.dumps(
                {
                    "action": "BUY", "symbol": "test", "type": "LIMIT",
                    "priceType": "0", "price": 0.01, "amount": 100
                }
            )
        )

        assert_equals((end_time - start_time).seconds, SLEEP_TIME)
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                (
                    'Successfully execute order:\n'
                    "{'symbol': 'test', 'amount': 100, 'action': 'BUY', "
                    "'type': 'LIMIT', 'price': 0.01, 'priceType': '0'}"
                )
            ]
        )
        assert_equals(result, "11106")

    @mock.patch.object(requests, 'post')
    def test_execute_entrust_raises_exception(self, mock_post):
        """Check if ``trade_easy.Trader.execute_entrust`` raises exception

        Args:
            mock_post: mock object of ``requests.post``
        """
        mock_post.return_value.raise_for_status.side_effect = HTTPError()
        mock_post.return_value.content = self.content
        start_time = arrow.now()
        assert_raises(
            ExecutedException, self.trader.execute_entrust, 'BUY', 'test',
            0.01, 100
        )
        end_time = arrow.now()

        mock_post.assert_called_with(
            '192.168.0.1:8080/orders',
            data=json.dumps(
                {
                    "action": "BUY", "symbol": "test", "type": "LIMIT",
                    "priceType": '0', "price": 0.01, "amount": 100
                }
            )
        )

        assert_equals(
            (end_time - start_time).seconds, SLEEP_TIME * MAX_REQUEST
        )
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'response content', 'response content'
            ]
        )
        assert_equals(HANDLER.messages['error'], ['', '', ''])

    @mock.patch.object(requests, 'get')
    def test_get_cancellable_entrusts(self, mock_get):
        """Check if ``trade_easy.Trader.get_cancellable_entrusts`` works

        Args:
            mock_get: mock object of ``requests.get``
        """
        mock_get.return_value.json.return_value = (
            FAKE_CANCELLABLE_ENTRUSTS_RESPONSE
        )
        mock_get.return_value.content = self.content
        expect_results = [
            {
                'stock_id': '600022', 'price': Decimal(0.000), 'volume': 0,
                'entrust_no': '11106', 'status': 0
            },
            {
                'stock_id': '600022', 'price': Decimal(0.000), 'volume': 0,
                'entrust_no': '11852', 'status': 0
            }
        ]
        start_time = arrow.now()
        results = self.trader.get_cancellable_entrusts()
        end_time = arrow.now()

        assert_equals((end_time - start_time).seconds, SLEEP_TIME)
        assert_equals(
            HANDLER.messages['info'], [
                'Read trade easy arguments', 'response content',
                'Successfully get cancellable entrusts'
            ]
        )
        assert_equals(len(results), len(expect_results))
        for each_result, each_expect_result in zip(results, expect_results):
            for key, value in each_expect_result.items():
                assert_equals(getattr(each_result, key), value)

    @mock.patch.object(requests, 'get')
    def test_get_cancellable_entrusts_raise_exception(self, mock_get):
        """Check if ``trade_easy.Trader.get_cancellable_entrusts`` raises Exception

        Args:
            mock_get: mock object of ``requests.get``
        """
        mock_get.return_value.raise_for_status.side_effect = HTTPError()
        mock_get.return_value.content = self.content

        start_time = arrow.now()
        assert_raises(ExecutedException, self.trader.get_cancellable_entrusts)
        end_time = arrow.now()

        mock_get.assert_called_with('192.168.0.1:8080/orders?status=open')
        assert_equals(
            (end_time - start_time).seconds, SLEEP_TIME * MAX_REQUEST
        )
        assert_equals(
            HANDLER.messages['info'],
            [
                'Read trade easy arguments', 'response content',
                'response content', 'response content'
            ]
        )
        assert_equals(HANDLER.messages['error'], ['', '', ''])

    @mock.patch.object(Trader, 'cancel_all_entrusts')
    @mock.patch.object(Trader, 'get_cancellable_entrusts')
    def test_cycle_cancel_all_entrusts(
        self, mock_get_cancellable_entrusts, mock_cancel_all_entrusts
    ):
        """Check if ``trade_easy.Trader.cycle_cancel_all_entrusts`` works

        Args:
            mock_get_cancellable_entrusts: (
                mock object of ``Trader.get_cancellable_entrusts``
            )
            mock_cancel_all_entrusts: (
                mock object of ``Trader.cancel_all_entrusts``
            )
        """
        mock_cancel_all_entrusts.return_value = True
        mock_get_cancellable_entrusts.return_value = []

        start_time = arrow.now()
        result = self.trader.cycle_cancel_all_entrusts()
        end_time = arrow.now()

        assert_equals((end_time - start_time).seconds, 0)
        assert_equals(
            HANDLER.messages['info'], [
                'Read trade easy arguments',
                'Successfully cycle cancle all entrusts'
            ]
        )
        assert_equals(HANDLER.messages['error'], [])
        assert_equals(True, result)

    @mock.patch.object(Trader, 'cancel_all_entrusts')
    @mock.patch.object(Trader, 'get_cancellable_entrusts')
    def test_cycle_cancel_all_subscribe(
        self, mock_get_cancellable_entrusts, mock_cancel_all_entrusts
    ):
        """Check if ``trade_easy.Trader.cycle_cancel_all_entrusts`` subscribe

        Args:
            mock_get_cancellable_entrusts: (
                mock object of ``Trader.get_cancellable_entrusts``
            )
            mock_cancel_all_entrusts: (
                mock object of ``Trader.cancel_all_entrusts``
            )
        """
        mock_cancel_all_entrusts.return_value = True
        mock_get_cancellable_entrusts.return_value = [
            Entrust('000001', Decimal(0.00), 0, '10001', 5),
            Entrust('000001', Decimal(0.00), 0, '10002', 5)
        ]

        start_time = arrow.now()
        result = self.trader.cycle_cancel_all_entrusts()
        end_time = arrow.now()

        assert_equals((end_time - start_time).seconds, 0)
        assert_equals(
            HANDLER.messages['info'], [
                'Read trade easy arguments',
                'Successfully cycle cancle all entrusts'
            ]
        )
        assert_equals(HANDLER.messages['error'], [])
        assert_equals(True, result)

    @mock.patch.object(Trader, 'cancel_all_entrusts')
    @mock.patch.object(Trader, 'get_cancellable_entrusts')
    def test_cycle_cancel_all_entrusts_incomplete(
        self, mock_get_cancellable_entrusts, mock_cancel_all_entrusts
    ):
        """Check if ``trade_easy.Trader.cycle_cancel_all_entrusts`` incomplete

        Args:
            mock_get_cancellable_entrusts: (
                mock object of ``Trader.get_cancellable_entrusts``
            )
            mock_cancel_all_entrusts: (
                mock object of ``Trader.cancel_all_entrusts``
            )
        """
        mock_cancel_all_entrusts.return_value = True
        mock_get_cancellable_entrusts.return_value = [
            Entrust('000001', Decimal(0.00), 0, '10001', 0),
            Entrust('000001', Decimal(0.00), 0, '10002', 5)
        ]

        start_time = arrow.now()
        assert_raises(
            CycleCancelFailedException, self.trader.cycle_cancel_all_entrusts
        )
        end_time = arrow.now()

        assert_equals((end_time - start_time).seconds, 0)
        assert_equals(HANDLER.messages['info'], ['Read trade easy arguments'])
        assert_equals(HANDLER.messages['error'], ["['10001']"])

    @mock.patch.object(Trader, 'cancel_all_entrusts')
    def test_cycle_cancel_all_entrusts_failed(self, mock_cancel_all_entrusts):
        """Check if ``trade_easy.Trader.cycle_cancel_all_entrusts`` raises exception

        Args:
            mock_cancel_all_entrusts: (
                mock object of ``Trader.cancel_all_entrusts``
            )
        """
        mock_cancel_all_entrusts.side_effect = ExecutedException('test')

        start_time = arrow.now()
        assert_raises(
            CycleCancelFailedException, self.trader.cycle_cancel_all_entrusts
        )
        end_time = arrow.now()

        assert_equals((end_time - start_time).seconds, 0)
        assert_equals(HANDLER.messages['info'], ['Read trade easy arguments'])
        assert_equals(
            HANDLER.messages['error'], ['test', 'test', 'test', '[]']
        )
