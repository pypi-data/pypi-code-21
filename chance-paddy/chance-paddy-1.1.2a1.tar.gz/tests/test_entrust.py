# -*- coding:utf-8 -*-
###
# Created Date: Tuesday, October 10th 2017, 2:35:13 pm
# Author: Rossa <qingwen.liao@whu.edu.cn>
# -----
# Last Modified: Tue Oct 10 2017
# Modified By: Rossa
# -----
# Copyright (c) 2017 chancefocus
#
###
from nose.tools import assert_almost_equals

from paddy.models.entrust import Entrust


def test_Entrust():
    """Check if ``Entrust`` works
    """
    fake_value = {
        'stock_id': '000001', 'price': 100.0, 'volume': 34.2,
        'entrust_no': '183', 'status': '0'
    }
    entrust = Entrust(**fake_value)

    for key, value in fake_value.items():
        assert_almost_equals(getattr(entrust, key), value)
