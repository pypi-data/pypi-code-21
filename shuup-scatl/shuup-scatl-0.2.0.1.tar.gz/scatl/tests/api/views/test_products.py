import json
from typing import List

from django.core.urlresolvers import reverse

from scatl.api.api_populator import PRODUCT_LIST
from scatl.tests.testutils.filters_test_case import FiltersTestCase


class ProductsApiTest(FiltersTestCase):
    def test_basic_data_presence(self):
        product = self.gen.product()
        
        response = self.client.get(path=reverse(PRODUCT_LIST))
        product_list = json.loads(response.content.decode())['results'] # type: List[dict]
        
        product_name_actual = product_list[0]['translations']['en']['name']
        self.assert_equal(product.name, product_name_actual)
        
        product_url = reverse(
            viewname='shuup:product',
            kwargs={'pk': product.pk, 'slug': product.slug},
        )
        self.assert_equal(product_url, product_list[0]['url'])

        product_image = product.media.first()
        product_image_rel_url = product_image.file.url
        self.assert_true(product_image_rel_url in product_list[0]['primary_image_url'])

        product_price = product.shop_products.first().default_price_value
        self.assert_equal(product_price, product_list[0]['price'])
