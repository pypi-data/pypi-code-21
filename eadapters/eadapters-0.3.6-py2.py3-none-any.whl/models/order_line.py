#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EOrderLine(base.EBase):

    quantity = appier.field(
        type = float
    )

    total = appier.field(
        type = float
    )

    size = appier.field(
        type = int
    )

    size_s = appier.field()

    scale = appier.field(
        type = int
    )

    meta = appier.field(
        type = dict
    )

    meta_j = appier.field()

    product = appier.field(
        type = appier.reference(
            "EProduct",
            name = "id"
        )
    )

    @classmethod
    def _build(cls, model, map):
        super(EOrderLine, cls)._build(model, map)

        meta = model.get("meta", {}) or {}
        image_url = meta.get("image_url", None)
        if not image_url: return

        product = model["product"]
        for size in ("thumbnail", "large"):
            size_i = size + "_image"
            image = product[size_i] or {}
            image["url"] = image_url
            product[size_i] = image

    @property
    def size_v(self):
        return self.size_s if self.size_s else str(self.size)
