import json

from django.core.urlresolvers import reverse
from shuup.testing.factories import get_default_product_type
from shuup_testutils.cases import ApiAuthAdminTestCase


class ProductTypeRestapiTest(ApiAuthAdminTestCase):
    def test_detail(self):
        product_type = get_default_product_type()
        response = self.client.get(
            reverse('product-type-detail', kwargs={'pk': product_type.pk}),
        )
        product_type_json = json.loads(response.content.decode())
        
        self.assert_equal(product_type.id, product_type_json['id'])
        product_type_name_actual = product_type_json['translations']['en']['name']
        self.assert_equal(product_type.name, product_type_name_actual)

    def test_list(self):
        product_type = get_default_product_type()
        response = self.client.get(reverse('product-type-list'))
        product_type_list_json = json.loads(response.content.decode())
        product_type_json = product_type_list_json[0]
        
        product_type_name_actual = product_type_json['translations']['en']['name']
        self.assert_equal(product_type.name, product_type_name_actual)
