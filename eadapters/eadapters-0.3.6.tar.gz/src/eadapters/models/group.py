#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import graphic

class EGroup(graphic.EGraphic):

    SIZE_ALIAS = dict(
        thumbnail = ("70",),
        large = ("1000",)
    )

    name = appier.field()

    order = appier.field(
        type = int
    )
