#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier
import datetime

from . import base

class EOrder(base.EBase):

    status = appier.field()

    paid = appier.field(
        type = bool
    )

    date = appier.field(
        type = int
    )

    reference = appier.field()

    currency = appier.field()

    sub_total = appier.field(
        type = float
    )

    discount = appier.field(
        type = float
    )

    shipping_cost = appier.field(
        type = float
    )

    total = appier.field(
        type = float
    )

    email = appier.field()

    shipping_address = appier.field(
        type = appier.reference(
            "EAddress",
            name = "id"
        )
    )

    billing_address = appier.field(
        type = appier.reference(
            "EAddress",
            name = "id"
        )
    )

    lines = appier.field(
        type = appier.references(
            "EOrderLine",
            name = "id"
        )
    )

    vouchers = appier.field(
        type = appier.references(
            "EVoucher",
            name = "id"
        )
    )

    @classmethod
    def _build(cls, model, map):
        super(EOrder, cls)._build(model, map)

        date = model["date"]
        if date: date = datetime.datetime.utcfromtimestamp(date)
        model["date_s"] = date.strftime("%Y-%m-%d") if date else None

        lines = model.get("lines", [])
        model["quantity"] = sum([line["quantity"] for line in lines])

    @property
    def voucher(self):
        if not hasattr(self, "vouchers"): return
        if not self.vouchers: return
        return self.vouchers[0]

    @property
    def quantity(self):
        return sum([line.quantity for line in self.lines])

    @property
    def date_s(self):
        return self.get_date_s()

    def get_date_s(self, format = "%Y-%m-%d"):
        if not hasattr(self, "date"): return None
        if not self.date: return None
        date = datetime.datetime.utcfromtimestamp(self.date)
        return date.strftime(format)

    def is_finalized(self):
        return True
