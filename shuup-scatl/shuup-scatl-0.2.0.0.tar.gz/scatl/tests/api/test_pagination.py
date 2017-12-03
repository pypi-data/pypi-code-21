import json

from django.core.urlresolvers import reverse
from shuup_testutils.generators import ShuupModelsGen

from scatl.api.api_populator import PRODUCT_LIST
from scatl.models import Config
from scatl.models.config import PAGE_SIZE_DEFAULT
from scatl.tests.testutils.filters_test_case import FiltersTestCase


class PaginationTest(FiltersTestCase):
    def set_up(self):
        self.gen = ShuupModelsGen()
        self.config = Config.get_solo()
    
    def test_page_size(self):
        self.gen.products(amount=25)
        
        product_list_page_1 = self._request_product_list()
        self.assert_equal(PAGE_SIZE_DEFAULT, len(product_list_page_1))
        
        product_list_page_2 = self._request_product_list(query_params={'page': 2})
        self.assert_equal(PAGE_SIZE_DEFAULT, len(product_list_page_2))
        
        product_list_page_3 = self._request_product_list(query_params={'page': 3})
        self.assert_equal(5, len(product_list_page_3))

    def test_page_last(self):
        self.gen.products(amount=25)
        
        response = self.client.get(reverse(PRODUCT_LIST), follow=True)
        response_content = response.content.decode()
        page_last = json.loads(response_content)['last']
        self.assert_equal(3, page_last)
