#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import payment

class BDPayment(payment.EPayment, bd_common.BDCommon):
    pass
