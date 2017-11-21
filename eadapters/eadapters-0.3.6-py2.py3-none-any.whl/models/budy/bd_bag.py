#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import bd_order
from . import bd_common
from . import bd_bag_line

from .. import bag

class BDBag(bag.EBag, bd_common.BDCommon):

    key = appier.field()

    @classmethod
    def wrap(cls, models, build = True, handler = None, **kwargs):
        def handler(model):
            lines = model.get("lines", [])
            model.update(
                lines = bd_bag_line.BDBagLine.wrap(lines)
            )

        return super(BDBag, cls).wrap(
            models,
            build = build,
            handler = handler,
            **kwargs
        )

    @classmethod
    def _ident_name(cls):
        return "key"

    @classmethod
    @bd_common.handle_error
    def _get(cls, id):
        api = cls._get_api_g()
        bag = api.get_bag(id)
        return cls.wrap(bag)

    @bd_common.handle_error
    def add_line_s(
        self,
        product_id,
        quantity = 1,
        size = None,
        scale = None,
        meta = None,
    ):
        api = self._get_api()
        item = bd_bag_line.BDBagLine(
            product = product_id,
            quantity = quantity,
            size = size,
            scale = scale,
            meta = meta
        )
        item = item.unwrap(default = True)
        line = api.add_update_line_bag(self.key, item)
        line = bd_bag_line.BDBagLine.wrap(line)
        return line

    @bd_common.handle_error
    def remove_line_s(self, line_id):
        api = self._get_api()
        line_id = self.bd_id_e(line_id)
        api.remove_line_bag(self.key, line_id)

    @bd_common.handle_error
    def merge_s(self, bag_id):
        api = self._get_api()
        api.merge_bag(self.key, bag_id)

    @bd_common.handle_error
    def empty_s(self):
        api = self._get_api()
        api.empty_bag(self.key)

    @bd_common.handle_error
    def create_order_s(self):
        api = self._get_api()
        order = api.order_bag(self.key)
        return bd_order.BDOrder.wrap(order)
