#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EAddress(base.EBase):

    first_name = appier.field()

    last_name = appier.field()

    address = appier.field()

    address_extra = appier.field()

    postal_code = appier.field()

    city = appier.field()

    state = appier.field()

    country = appier.field()

    phone_number = appier.field()

    vat_number = appier.field(
        description = "VAT Number"
    )

    neighborhood = appier.field()

    @classmethod
    def validate(cls):
        return super(EAddress, cls).validate() + [
            appier.not_null("first_name"),
            appier.not_empty("first_name"),

            appier.not_null("last_name"),
            appier.not_empty("last_name"),

            appier.not_null("address"),
            appier.not_empty("address"),

            appier.not_null("country"),
            appier.not_empty("country"),

            appier.not_null("city"),
            appier.not_empty("city"),

            appier.not_null("postal_code"),
            appier.not_empty("postal_code"),

            appier.not_null("phone_number"),
            appier.not_empty("phone_number"),
            appier.string_gt("phone_number", 7),
            appier.is_regex("phone_number", "^\+?[0-9\s]+$")
        ]

    @property
    def full_name(self):
        name = self.first_name
        name += " " + self.last_name if self.last_name else ""
        return name
