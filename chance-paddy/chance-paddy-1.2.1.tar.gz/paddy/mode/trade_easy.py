#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: mode/trade_easy.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017
import json
import logging
import requests

from decimal import Decimal
from requests.exceptions import HTTPError
from time import sleep

from paddy.constant import (
    MAX_REQUEST, SLEEP_TIME, ENTRUST_STATE_DICT
)
from paddy.exceptions import ExecutedException, CycleCancelFailedException
from paddy.models.account import Account
from paddy.models.entrust import Entrust


LOGGER = logging.getLogger(__name__)


def cycle_wait(func):
    """Decorator for cycling wait
    """
    def wrapper(*args, **kwargs):
        """Wrapper methods
        """
        for _ in range(MAX_REQUEST):
            sleep(SLEEP_TIME)
            try:
                return func(*args, **kwargs)
            except HTTPError, e:
                LOGGER.exception(e)
        raise ExecutedException('Reached max request times')

    return wrapper


class Trader(object):
    """Trader class for ``trade_easy``
    """
    def __init__(self, arguments):
        """Initialize class

        Args:
            arguments: a dict of trader arguments
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        self.host = arguments.get('host')
        self._logger.info('Read trade easy arguments')

    @cycle_wait
    def get_account(self):
        """Get account info

        Return:
            ``Account``

        Raises:
            HTTPError
        """
        response = requests.get('{0}/positions'.format(self.host))
        self._logger.info(response.content)
        response.raise_for_status()
        response = response.json()
        self._logger.info('Successfully get account info')

        return response_to_account(response)

    @cycle_wait
    def get_all_entrusts(self):
        """Get today all entrusts

        Return:
            list of ``Entrust``

        Raises:
            HTTPError
        """
        response = requests.get('{0}/orders'.format(self.host))
        self._logger.info(response.content)
        response.raise_for_status()
        self._logger.info('Successfully get entrust info')
        return response_to_entrusts(response.json())

    @cycle_wait
    def cancel_all_entrusts(self):
        """Cancel all entrusts

        Return:
            ``bool``

        Raises:
            HTTPError
        """
        response = requests.delete('{0}/orders'.format(self.host))
        self._logger.info(response.content)
        response.raise_for_status()
        self._logger.info('Successfully delete all orders')

        return True

    @cycle_wait
    def execute_entrust(
        self, action, stock_id, price, volume, types='LIMIT', price_type='0'
    ):
        """Execute entrust

        Args:
            action: String
            stock_id: String
            price: Decimal
            volume: int
            types: String, default as 'LIMIT'
            price_type: String, default as '0'

        Return:
            String

        Raises:
            HTTPError
        """
        data = {
            "action": action, "symbol": stock_id, "price": price,
            "amount": volume, "type": types, "priceType": price_type
        }

        response = requests.post(
            '{0}/orders'.format(self.host), data=json.dumps(data)
        )
        self._logger.info(response.content)
        response.raise_for_status()

        self._logger.info('Successfully execute order:\n{0}'.format(data))

        return response.json().get('id')

    @cycle_wait
    def get_cancellable_entrusts(self):
        """Get cancellable entrusts

        Returns:
            a List of ``Entrust``

        Raises:
            HTTPError
        """
        response = requests.get('{0}/orders?status=open'.format(self.host))
        self._logger.info(response.content)
        response.raise_for_status()
        self._logger.info('Successfully get cancellable entrusts')
        return response_to_entrusts(response.json())

    def cycle_cancel_all_entrusts(self):
        """Cycle cancel all entrusts

        Returns:
            bool

        Raises:
            CycleCancleFailedException
        """
        cancellable_entrusts = []
        for _ in range(MAX_REQUEST):
            try:
                self.cancel_all_entrusts()
                cancellable_entrusts = self.get_cancellable_entrusts()

                cancellable_entrusts = [
                    entrust for entrust in cancellable_entrusts
                    if entrust.status != 5
                ]
                if not cancellable_entrusts:
                    self._logger.info('Successfully cycle cancle all entrusts')
                    return True
            except ExecutedException, e:
                self._logger.error(e)
        ids = [
            getattr(entrust, 'entrust_no') for entrust in cancellable_entrusts
        ]
        self._logger.error(ids)
        raise CycleCancelFailedException(ids)


def response_to_account(response):
    """Transform reponse to ``Account``

    Args:
        response: a dict

    Return:
        Account
    """
    cols = response['dataTable']['columns']
    rows = response['dataTable']['rows']
    hold_stock_list = []
    for each_row in rows:
        account_src_dict = dict(zip(cols, each_row))
        hold_stock_list.append(
            (account_src_dict[u'证券代码'], Decimal(account_src_dict[u'市值']))
        )

    account_dict = {
        'total_asset': Decimal(
            response['subAccounts'][u'人民币'][u'参考总资产（含港股通）']
        ),
        'stock_asset': Decimal(
            response['subAccounts'][u'人民币'][u'参考股票市值(含港股通)']
        ),
        'hold_stock': dict(hold_stock_list)
    }

    return Account(**account_dict)


def response_to_entrusts(response):
    """Get instance of Entrust list

    Args:
        response: a dict

    Return:
    list of ``Entrust``
    """
    entrust_list = []
    cols = response['dataTable']['columns']
    rows = response['dataTable']['rows']
    for each_row in rows:
        entrust_src_dict = dict(zip(cols, each_row))
        entrust_dict = {
            'stock_id': entrust_src_dict[u'证券代码'],
            'price': Decimal(entrust_src_dict[u'成交均价']),
            'volume': int(entrust_src_dict[u'成交数量']),
            'entrust_no': entrust_src_dict[u'合同编号'],
            'status': ENTRUST_STATE_DICT[entrust_src_dict[u'备注']],
        }
        entrust_list.append(Entrust(**entrust_dict))
    return entrust_list
