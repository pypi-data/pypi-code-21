from shuup.core.models import Attribute, AttributeType

from scatl.api.serializers.query_data import params
from scatl.tests.testutils.filters_test_case import FiltersTestCase


class FiltersTest(FiltersTestCase):
    def test_filter_by_category(self):
        categories = []
        for _ in range(0, 3):
            category = self.gen.category()
            categories.append(category)

        product_0 = self.gen.product(
            primary_category=categories[0],
        )
        product_1 = self.gen.product(
            primary_category=categories[1],
        )
        product_0_1 = self.gen.product(
            primary_category=categories[0],
            categories=[categories[0], categories[1]],
        )
        product_1_2 = self.gen.product(
            primary_category=categories[1],
            categories=[categories[2]],
        )
        product_0_2 = self.gen.product(
            primary_category=categories[0],
            categories=[categories[2]],
        )

        list_1 = self._request_product_list(
            query_params=self._build_category_query_param(slug=categories[1].slug)
        )
        self._assert_contains_product(list_1, product_1)
        self._assert_contains_product(list_1, product_0_1)
        self._assert_contains_product(list_1, product_1_2)
        self._assert_not_contains_product(list_1, product_0)
        self._assert_not_contains_product(list_1, product_0_2)

        list_0 = self._request_product_list(
            query_params=self._build_category_query_param(slug=categories[0].slug)
        )
        self._assert_contains_product(list_0, product_0)
        self._assert_contains_product(list_0, product_0_1)
        self._assert_contains_product(list_0, product_0_2)
        self._assert_not_contains_product(list_0, product_1)
        self._assert_not_contains_product(list_0, product_1_2)

    # noinspection PyShadowingBuiltins
    def test_filter_by_price(self):
        product_100 = self.gen.product(price=100)
        product_200 = self.gen.product(price=200)
        product_300 = self.gen.product(price=300)
        product_400 = self.gen.product(price=400)
        product_500 = self.gen.product(price=500)

        product_list = self._request_product_list(
            query_params=self._build_price_query_param(min=200, max=400)
        )
        self._assert_not_contains_product(product_list, product_100)
        self._assert_not_contains_product(product_list, product_500)
        self._assert_contains_product(product_list, product_200)
        self._assert_contains_product(product_list, product_300)
        self._assert_contains_product(product_list, product_400)

        product_list = self._request_product_list(
            query_params=self._build_price_query_param(min=299, max=400)
        )
        self._assert_not_contains_product(product_list, product_100)
        self._assert_not_contains_product(product_list, product_200)
        self._assert_not_contains_product(product_list, product_500)
        self._assert_contains_product(product_list, product_300)
        self._assert_contains_product(product_list, product_400)

        product_list = self._request_product_list(
            query_params=self._build_price_query_param(min=501, max=1000)
        )
        self._assert_not_contains_product(product_list, product_100)
        self._assert_not_contains_product(product_list, product_200)
        self._assert_not_contains_product(product_list, product_300)
        self._assert_not_contains_product(product_list, product_400)
        self._assert_not_contains_product(product_list, product_500)

        product_list = self._request_product_list(
            query_params=self._build_price_query_param(min=0, max=0)
        )
        self._assert_not_contains_product(product_list, product_100)
        self._assert_not_contains_product(product_list, product_200)
        self._assert_not_contains_product(product_list, product_300)
        self._assert_not_contains_product(product_list, product_400)
        self._assert_not_contains_product(product_list, product_500)

        product_list = self._request_product_list(
            query_params=self._build_price_query_param(min=0, max=100)
        )
        self._assert_contains_product(product_list, product_100)
        self._assert_not_contains_product(product_list, product_200)
        self._assert_not_contains_product(product_list, product_300)
        self._assert_not_contains_product(product_list, product_400)
        self._assert_not_contains_product(product_list, product_500)

    def test_filter_by_shuup_attr_bool(self):
        attr = Attribute.objects.create(
            identifier='ident',
            type=AttributeType.BOOLEAN,
            name='test name',
        )
        
        product_true = self.gen.product()
        bool_true = 1
        product_true.attributes.create(attribute=attr, numeric_value=bool_true)
        
        product_false = self.gen.product()
        bool_false = 0
        product_false.attributes.create(attribute=attr, numeric_value=bool_false)
        
        product_none = self.gen.product()
        
        product_list = self._request_product_list(
            query_params=self._build_shuup_query_param(
                ident=attr.identifier, value=params.shuup.bool.true,
            )
        )
        self._assert_contains_product(product_list, product_true)
        self._assert_not_contains_product(product_list, product_false)
        self._assert_not_contains_product(product_list, product_none)
