#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EWishlist(base.EBase):

    currency = appier.field()

    total = appier.field(
        type = float
    )

    lines = appier.field(
        type = appier.references(
            "EWishlistLine",
            name = "id"
        )
    )
