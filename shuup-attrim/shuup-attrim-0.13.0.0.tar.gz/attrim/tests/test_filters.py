from typing import List

from shuup.core.models import Product
from shuup.testing.factories import get_default_shop
from shuup_testutils.cases import SnakeTestCase

from attrim.filters import filter_product_qs_by
from attrim.models import Option
from attrim.testutils.generators import ModelsGen


class FiltersTest(SnakeTestCase):
    """
    This is just a smoke test, everything else is located at shuup-scatl.
    """
    def test_trans_str_product_filter(self):
        gen = ModelsGen()
        cls = gen.attrim.cls(options_amount=0)
        options = gen.attrim.option_list(cls=cls, amount=5)  # type: List[Option]

        product_0_1 = gen.product()
        product_0_1.attrim_attrs.create(cls=cls).options.set([
            options[0],
            options[1],
        ])
        product_1_2 = gen.product()
        product_1_2.attrim_attrs.create(cls=cls).options.set([
            options[1],
            options[2],
        ])

        product_qs_0_1 = filter_product_qs_by(
            cls=cls,
            option_values_raw=[options[0].get_value(), options[1].get_value()],
            product_qs_source=Product.objects.listed(shop=get_default_shop()),
        )
        self.assert_true(len(product_qs_0_1) >= 2)
        self.assert_true(product_0_1 in product_qs_0_1)
        self.assert_true(product_1_2 in product_qs_0_1)

        product_qs_1_2 = filter_product_qs_by(
            cls=cls,
            option_values_raw=[options[1].get_value(), options[2].get_value()],
            product_qs_source=Product.objects.listed(shop=get_default_shop()),
        )
        self.assert_true(len(product_qs_1_2) >= 2)
        self.assert_true(product_0_1 in product_qs_1_2)
        self.assert_true(product_1_2 in product_qs_1_2)

        product_qs_1 = filter_product_qs_by(
            cls=cls,
            option_values_raw=[options[1].get_value()],
            product_qs_source=Product.objects.listed(shop=get_default_shop()),
        )
        self.assert_true(len(product_qs_1) >= 2)
        self.assert_true(product_0_1 in product_qs_1)
        self.assert_true(product_1_2 in product_qs_1)
