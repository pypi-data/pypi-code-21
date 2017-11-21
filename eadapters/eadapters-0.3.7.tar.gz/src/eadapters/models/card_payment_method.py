#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import payment_method

class ECardPaymentMethod(payment_method.EPaymentMethod):

    @classmethod
    def ensure_method(cls, payment_method):
        if payment_method == "credit_card": return
        raise appier.OperationalError(message = "Unexpected payment method")
