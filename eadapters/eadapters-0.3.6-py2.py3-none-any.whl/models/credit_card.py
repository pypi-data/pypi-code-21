#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class ECreditCard(base.EBase):

    card_name = appier.field()

    card_number = appier.field()

    expiration_year = appier.field(
        type = int
    )

    expiration_month = appier.field(
        type = int
    )

    security_code = appier.field()

    @classmethod
    def validate(cls):
        return super(ECreditCard, cls).validate() + [
            appier.not_null("card_name"),
            appier.not_empty("card_name"),

            appier.not_null("card_number"),
            appier.not_empty("card_number"),

            appier.not_null("expiration_month"),
            appier.gte("expiration_month", 1),
            appier.lte("expiration_month", 12),

            appier.not_null("expiration_year"),

            appier.not_null("security_code"),
            appier.not_empty("security_code")
        ]

    @classmethod
    def payment_types(cls):
        return (
            "visa",
            "mastercard",
            "american_express"
        )
