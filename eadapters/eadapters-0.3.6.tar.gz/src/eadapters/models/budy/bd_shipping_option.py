#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import shipping_option

class BDShippingOption(shipping_option.EShippingOption, bd_common.BDCommon):
    pass
