#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base
from . import currency

class ECountry(base.EBase):

    name = appier.field()

    country_code = appier.field()

    currency_code = appier.field()

    locale = appier.field()

    def get_currency(self):
        return currency.ECurrency(
            name = self.currency_code,
            currency_code = self.currency_code
        )
