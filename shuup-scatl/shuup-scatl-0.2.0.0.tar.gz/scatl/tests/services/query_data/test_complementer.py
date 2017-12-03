from shuup.testing.factories import get_default_shop

from scatl.models import Config
from scatl.services.query_data.complementer import complement_query_data_from_db
from scatl.services.query_data.query_data import QueryData, PriceRange
from scatl.tests.testutils.filters_test_case import FiltersTestCase


class ComplementerTest(FiltersTestCase):
    def test_page_last_complementation(self):
        self.gen.products(amount=25)
        query_data = QueryData(
            shop=get_default_shop(),
            user_contact=self.gen.person_contact(),
        )
        complement_query_data_from_db(query_data)
        self.assert_equal(3, query_data.page_last)

    def test_page_last_complementation_with_filters_by_price(self):
        page_size = Config.get_solo().page_size
        for _ in range(0, page_size):
            self.gen.product(price=400)
        self.gen.product(price=500)
        
        query_data_without_filters = QueryData(
            shop=get_default_shop(),
            user_contact=self.gen.person_contact(),
        )
        complement_query_data_from_db(query_data_without_filters)
        self.assert_equal(2, query_data_without_filters.page_last)
        
        query_data_with_filters = QueryData(
            price_range=PriceRange(min=100, max=450),
            shop=get_default_shop(),
            user_contact=self.gen.person_contact(),
        )
        complement_query_data_from_db(query_data_with_filters)
        self.assert_equal(1, query_data_with_filters.page_last)
