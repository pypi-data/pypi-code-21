from typing import List

from attrim.models import Class, Option, Attribute
from attrim.models.type import Type

from scatl.tests.testutils.filters_test_case import FiltersTestCase


class AttrimFiltersTest(FiltersTestCase):
    def test_filter_by_one_class(self):
        cls = self.gen.attrim.cls(type=Type.INT) # type: Class
        options = self.gen.attrim.option_list(cls=cls, amount=4) # type: List[Option]

        product_0 = self.gen.product()
        product_0_attr = product_0.attrim_attrs.create(cls=cls) # type: Attribute
        product_0_attr.options.set([options[0]])
        product_0_1 = self.gen.product()
        product_0_1_attr = product_0_1.attrim_attrs.create(cls=cls) # type: Attribute
        product_0_1_attr.options.set([options[0], options[1]])
        product_1_2 = self.gen.product()
        product_1_2_attr = product_1_2.attrim_attrs.create(cls=cls) # type: Attribute
        product_1_2_attr.options.set([options[1], options[2]])
        product_2 = self.gen.product()
        product_2_attr = product_2.attrim_attrs.create(cls=cls) # type: Attribute
        product_2_attr.options.set([options[2]])
        product_3 = self.gen.product()
        product_3_attr = product_3.attrim_attrs.create(cls=cls) # type: Attribute
        product_3_attr.options.set([options[3]])

        list_0_1 = self._request_product_list(
            query_params=self._build_attrim_query_param(
                code=cls.code,
                options=[options[0], options[1]],
            )
        )
        self._assert_contains_product(list_0_1, product_0)
        self._assert_contains_product(list_0_1, product_0_1)
        self._assert_contains_product(list_0_1, product_1_2)
        self._assert_not_contains_product(list_0_1, product_2)
        self._assert_not_contains_product(list_0_1, product_3)

        list_1 = self._request_product_list(
            query_params=self._build_attrim_query_param(
                code=cls.code, options=[options[1]],
            )
        )
        self._assert_contains_product(list_1, product_0_1)
        self._assert_contains_product(list_1, product_1_2)
        self._assert_not_contains_product(list_1, product_0)
        self._assert_not_contains_product(list_1, product_2)
        self._assert_not_contains_product(list_1, product_3)

    def test_filter_by_two_classes(self):
        cls_0 = self.gen.attrim.cls(type=Type.INT, options_amount=0)
        cls_0_options = [
            self.gen.attrim.option(cls=cls_0),
            self.gen.attrim.option(cls=cls_0),
        ]
        cls_1 = self.gen.attrim.cls(type=Type.INT, options_amount=0)
        cls_1_options = [
            self.gen.attrim.option(cls=cls_1),
            self.gen.attrim.option(cls=cls_1),
        ]

        product_cls_0_opt_0 = self.gen.product()
        product_cls_0_opt_0_attr = product_cls_0_opt_0.attrim_attrs.create(cls=cls_0)
        product_cls_0_opt_0_attr.options.set([cls_0_options[0]])

        product_cls_0_opt_1 = self.gen.product()
        product_cls_0_opt_1_attr = product_cls_0_opt_1.attrim_attrs.create(cls=cls_0)
        product_cls_0_opt_1_attr.options.set([cls_0_options[1]])

        product_cls_0_opt_0_1 = self.gen.product()
        product_cls_0_opt_0_1_attr = product_cls_0_opt_0_1.attrim_attrs.create(cls=cls_0)
        product_cls_0_opt_0_1_attr.options.set([cls_0_options[0], cls_0_options[1]])

        product_cls_1_opt_0 = self.gen.product()
        product_cls_0_opt_0_1_attr = product_cls_1_opt_0.attrim_attrs.create(cls=cls_1)
        product_cls_0_opt_0_1_attr.options.set([cls_1_options[0]])

        product_cls_1_opt_0_1 = self.gen.product()
        product_cls_0_opt_0_1_attr = product_cls_1_opt_0_1.attrim_attrs.create(cls=cls_1)
        product_cls_0_opt_0_1_attr.options.set([cls_1_options[0], cls_1_options[1]])

        product_cls_0_opt_0__cls_1_opt_0 = self.gen.product()
        product_cls_0_opt_0__cls_1_attr = product_cls_0_opt_0__cls_1_opt_0.attrim_attrs.create(cls=cls_0)
        product_cls_0_opt_0__cls_1_attr.options.set([cls_0_options[0]])
        product_cls_0__cls_1_opt_0_attr = product_cls_0_opt_0__cls_1_opt_0.attrim_attrs.create(cls=cls_1)
        product_cls_0__cls_1_opt_0_attr.options.set([cls_1_options[0]])

        product_list = self._request_product_list(
            query_params={
                **self._build_attrim_query_param(
                    code=cls_0.code, options=[cls_0_options[0]],
                ),
                **self._build_attrim_query_param(
                    code=cls_1.code, options=[cls_1_options[0]],
                ),
            }
        )
        self._assert_contains_product(product_list, product_cls_0_opt_0__cls_1_opt_0)
        self._assert_not_contains_product(product_list, product_cls_0_opt_0)
        self._assert_not_contains_product(product_list, product_cls_0_opt_1)
        self._assert_not_contains_product(product_list, product_cls_0_opt_0_1)
        self._assert_not_contains_product(product_list, product_cls_1_opt_0)
        self._assert_not_contains_product(product_list, product_cls_1_opt_0_1)

        product_list = self._request_product_list(
            query_params=self._build_attrim_query_param(
                code=cls_0.code, options=[cls_0_options[0]],
            )
        )
        self._assert_contains_product(product_list, product_cls_0_opt_0__cls_1_opt_0)
        self._assert_contains_product(product_list, product_cls_0_opt_0)
        self._assert_contains_product(product_list, product_cls_0_opt_0_1)
        self._assert_not_contains_product(product_list, product_cls_0_opt_1)
        self._assert_not_contains_product(product_list, product_cls_1_opt_0)
        self._assert_not_contains_product(product_list, product_cls_1_opt_0_1)
