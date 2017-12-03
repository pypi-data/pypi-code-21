from django.test import RequestFactory
from shuup_testutils.generators.shuup.requests import gen_shuup_request
from shuup_utils.lang_constants import DEFAULT_LANG

from scatl.api.serializers.query_data import params
from scatl.tests.testutils.filters_test_case import FiltersTestCase


class SortingFiltersTest(FiltersTestCase):
    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.shuup_request = gen_shuup_request(factory=RequestFactory())

    def test_sorting_by_name_AZ(self):
        product_list_source = [
            self.gen.product(name='alpha'),
            self.gen.product(name='beta'),
            self.gen.product(name='gamma'),
            self.gen.product(name='zeta'),
        ]
        product_list_json = self._request_product_list({
            params.sorting.key: params.sorting.by_name_AZ
        })
        for order, product_json in enumerate(product_list_json):
            name = product_json['translations'][DEFAULT_LANG]['name']
            # noinspection PyUnresolvedReferences
            self.assert_equal(product_list_source[order].name, name)

    def test_sorting_by_name_ZA(self):
        product_list_source = [
            self.gen.product(name='zeta'),
            self.gen.product(name='gamma'),
            self.gen.product(name='beta'),
            self.gen.product(name='alpha'),
        ]
        product_list_json = self._request_product_list({
            params.sorting.key: params.sorting.by_name_ZA
        })
        for order, product_json in enumerate(product_list_json):
            name = product_json['translations'][DEFAULT_LANG]['name']
            self.assert_equal(product_list_source[order].name, name)

    def test_sorting_by_price_min_max(self):
        products_min_max = [
            self.gen.product(price=100.5),
            self.gen.product(price=200.5),
            self.gen.product(price=300.5),
            self.gen.product(price=500.5),
        ]
        product_list_json = self._request_product_list({
            params.sorting.key: params.sorting.by_price_min_max
        })
        for order, product_json in enumerate(product_list_json):
            price_actual_str = product_json['price']
            price_actual = float(price_actual_str)
            # noinspection PyTypeChecker
            product_price_raw = products_min_max[order].get_price(self.shuup_request).value
            # noinspection PyTypeChecker
            product_price_expected = float(product_price_raw)
            self.assert_equal(product_price_expected, price_actual)

    def test_sorting_by_price_max_min(self):
        products_max_min = [
            self.gen.product(price=500.5),
            self.gen.product(price=300.5),
            self.gen.product(price=200.5),
            self.gen.product(price=100.5),
        ]
        product_list_json = self._request_product_list({
            params.sorting.key: params.sorting.by_price_max_min
        })
        for order, product_json in enumerate(product_list_json):
            price_actual_str = product_json['price']
            price_actual = float(price_actual_str)
            # noinspection PyTypeChecker
            product_price_raw = products_max_min[order].get_price(self.shuup_request).value
            # noinspection PyTypeChecker
            product_price_expected = float(product_price_raw)
            self.assert_equal(product_price_expected, price_actual)
