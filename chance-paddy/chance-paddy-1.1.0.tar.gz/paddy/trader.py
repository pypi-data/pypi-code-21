#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: trader.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 26.09.2017
import importlib
import logging

from constant import TRADERS
from exceptions import ExecutedException


class Trader(object):
    """Abstract class for trading
    """
    __slots__ = [
        '_arguments', '_trader', '_logger', 'mode', 'account_id',
        'get_account', 'get_all_entrusts', 'get_cancellable_entrusts',
        'execute_entrust', 'cancel_all_entrusts', 'cycle_cancel_all_entrusts',
    ]

    def __init__(self, mode, arguments=None):
        """Initialize class with given mode and account_id

        Args:
            mode: an int to create correponding trading model
            arguments: an object for all arguments
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._trader = importlib.import_module(
            '..mode.{0}'.format(TRADERS[mode]), __name__
        ).Trader(arguments)
        self.mode = mode
        self._logger.info(
            'Initialize trader as {0} successful'.format(TRADERS[mode])
        )
        self._logger.info('Initialize arguments: {0}'.format(arguments))

    def __getattr__(self, attr):
        """Modified the attribute visiting methods
        """
        self._logger.debug('Trader called {0}'.format(attr))
        if attr not in self.__slots__:
            raise ExecutedException('{0} not in allowed methods'.format(attr))
        return getattr(self._trader, attr)
