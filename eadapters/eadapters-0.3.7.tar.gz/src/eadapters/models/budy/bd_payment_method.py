#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import payment_method

class BDPaymentMethod(payment_method.EPaymentMethod, bd_common.BDCommon):
    pass
