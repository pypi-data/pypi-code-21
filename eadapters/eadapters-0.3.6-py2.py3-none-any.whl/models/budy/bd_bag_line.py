#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import bd_common

from .. import bag_line

class BDBagLine(bag_line.EBagLine, bd_common.BDCommon):

    @classmethod
    def wrap(cls, models, build = True, handler = None, **kwargs):
        def handler(model):
            from .. import bd_product
            product = model.get("product")
            model.update(
                meta = cls.bd_json_d(model, "attributes"),
                meta_j = cls.bd_unicode_d(model, "attributes")
            )
            if type(product) == dict:
                model["product"] = bd_product.BDProduct.wrap(product)

        return super(BDBagLine, cls).wrap(
            models,
            build = build,
            handler = handler,
            **kwargs
        )

    def unwrap(self, **kwargs):
        result = bag_line.EBagLine.unwrap(self, **kwargs)
        if hasattr(self, "meta") and self.meta: result["attributes"] = self.bd_json_e(self.meta, sort_keys = True)
        return result
