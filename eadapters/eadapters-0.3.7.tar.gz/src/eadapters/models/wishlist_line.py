#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EWishlistLine(base.EBase):

    quantity = appier.field(
        type = float
    )

    total = appier.field(
        type = float
    )

    product = appier.field(
        type = appier.reference(
            "EProduct",
            name = "id"
        )
    )
