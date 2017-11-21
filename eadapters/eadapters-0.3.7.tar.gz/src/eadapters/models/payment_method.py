#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EPaymentMethod(base.EBase):

    type = appier.field()

    name = appier.field()

    @classmethod
    def ensure_method(cls, payment_method):
        pass

    def is_credit_card(self):
        return self.type == "credit_card"
