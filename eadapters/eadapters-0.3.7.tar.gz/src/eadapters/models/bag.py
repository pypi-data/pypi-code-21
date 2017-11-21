#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EBag(base.EBase):

    currency = appier.field()

    total = appier.field(
        type = float
    )

    lines = appier.field(
        type = appier.references(
            "EBagLine",
            name = "id"
        )
    )

    @property
    def quantity(self):
        return sum([line.quantity for line in self.lines])
