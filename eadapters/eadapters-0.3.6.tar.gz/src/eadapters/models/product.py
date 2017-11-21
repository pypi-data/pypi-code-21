#!/usr/bin/python
# -*- coding: utf-8 -*-

import appier

from . import graphic

class EProduct(graphic.EGraphic):

    SIZE_ALIAS = dict(
        thumbnail = ("70",),
        large = ("1000",)
    )

    GENDER_ALIAS = dict(
        Male = "Men",
        Female = "Women",
        Both = "Unisex"
    )

    name = appier.field()

    description = appier.field()

    code = appier.field()

    size = appier.field(
        type = int
    )

    scale = appier.field(
        type = int
    )

    price = appier.field(
        type = float
    )

    @classmethod
    def _get_measurements(cls, model, sort = True):
        measurements = model.get("measurements", None)
        if not measurements: return []
        if sort: measurements.sort(
            key = lambda item:\
            (item.get("value", -1), item.get("value_s", None))
        )
        return measurements

    @classmethod
    def _get_currency(cls, model):
        return "GBP"

    def get_image_url(self, size):
        image = self.images[0]
        url = image.get(size, None)
        return url

    def get_measurements(self, sort = True):
        return self.__class__._get_measurements(self.model, sort = sort)

    def get_price(self, currency = "EUR", field = "totalPriceValue"):
        if hasattr(self, "price"): return self.price
        if not self.variants: return None
        variant = self.variants[0]
        prices = variant.get("prices", [])
        if not prices: return None
        for price in prices:
            _currency = price["currencyIsoCode"]
            if not _currency == currency: continue
            return price[field]
        return None

    def get_gender(self, default = "Male"):
        if hasattr(self, "gender"): gender = self.gender
        gender = gender or default
        return self.__class__.GENDER_ALIAS.get(gender, gender)

    def is_available(self):
        if self.quantity_hand == None: return True
        if self.quantity_hand > 0.0: return True
        if self.get_measurements(): return True
        return False
