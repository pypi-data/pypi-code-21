#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import base

class EBagLine(base.EBase):

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
        super(EBagLine, cls)._build(model, map)

        meta = model.get("meta", {}) or {}
        image_url = meta.get("image_url", None)
        embossing = meta.get("embossing", None)

        if image_url:
            product = model["product"]
            for size in ("thumbnail", "large"):
                size_i = size + "_image"
                image = product[size_i] or {}
                image["url"] = image_url
                product[size_i] = image

        if embossing:
            embossing_s = embossing.replace("_", " ")
            embossing_s = embossing_s.capitalize()
            meta["embossing_s"] = embossing_s

    def get_meta(self, normalize = True):
        if not self.meta: return self.meta
        meta = dict(self.meta)
        if not normalize: return meta
        for extra in ("embossing_s",):
            if not extra in meta: continue
            del meta[extra]
        return meta

    @property
    def size_v(self):
        return self.size_s if self.size_s else str(self.size)
