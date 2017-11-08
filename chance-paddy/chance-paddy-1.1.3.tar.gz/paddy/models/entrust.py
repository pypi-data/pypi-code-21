# -*- coding:utf-8 -*-
###
# Created Date: Tuesday, October 10th 2017, 2:16:05 pm
# Author: Rossa <qingwen.liao@whu.edu.cn>
# -----
# Last Modified: Tue Oct 10 2017
# Modified By: Rossa
# -----
# Copyright (c) 2017 chancefocus
#
###


class Entrust(object):
    """Model class for ``Entrust``
    """
    _stock_id = None
    _price = None
    _volume = None
    _entrust_no = None
    _status = None

    def __init__(
        self, stock_id=None, price=None, volume=None,
        entrust_no=None, status=None
    ):
        self._stock_id = stock_id
        self._price = price
        self._volume = volume
        self._entrust_no = entrust_no
        self._status = status

    @property
    def stock_id(self):
        return self._stock_id

    @property
    def price(self):
        return self._price

    @property
    def volume(self):
        return self._volume

    @property
    def entrust_no(self):
        return self._entrust_no

    @property
    def status(self):
        return self._status
