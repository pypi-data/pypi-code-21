# coding=utf-8
import time
import unittest

from sdp_dtv.management.package_template import PackageTemplateClient
from sdp_dtv.management.product_template import ProductTemplateClient
from tests import API_ACCESS_CONFIG


class TestProductTemplateApi(unittest.TestCase):
    def test_crud(self):
        product_template_client = ProductTemplateClient(**API_ACCESS_CONFIG)
        product_template = {
            "code": "KitPrepagoDTV",
            "name": "Kit Prepago",
            "description": "Kit Prepago",
            "provider_code": "33333333-3",
            "weight": 20.25,
            "width": 10.5,
            "height": 15.3,
            "depth": 20.4,
            "box_type": 1,
            'packaging_location_code': 'Directv-Fijo'
        }

        result = product_template_client.create(product_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        product_template_code = result.content['code']
        result = product_template_client.get_by_id(product_template_code)
        self.assertTrue(result.response.status == 200 and result.content)

        result = product_template_client.get_by_id('sample-product-template')
        self.assertTrue(result.response.status == 404)

        result = product_template_client.search({'code': 'KitPrepagoDTV'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = product_template_client.delete(result.content['items'][0]['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = product_template_client.create(product_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        product_template['width'] = 11.6
        result = product_template_client.update(product_template, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()