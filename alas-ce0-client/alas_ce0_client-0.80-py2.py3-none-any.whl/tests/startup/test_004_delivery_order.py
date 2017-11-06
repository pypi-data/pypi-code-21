# coding=utf-8
import datetime
import random
import time
import unittest
import uuid

from sdp_dtv.delivery.delivery_order import DeliveryOrderRequestClient, DeliveryOrderClient
from sdp_dtv.management.package_template import PackageTemplateClient
from sdp_dtv.management.product_template import ProductTemplateClient
from tests import API_ACCESS_CONFIG


class TestDeliveryOrder(unittest.TestCase):
    def test_crud(self):
        package_template_client = PackageTemplateClient(**API_ACCESS_CONFIG)
        package_template = {
            "code": "Box1",
            "weight": 21.25,
            "width": 11.5,
            "height": 11.3,
            "depth": 21.4,
            "box_type": 1
        }

        result = package_template_client.create(package_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        product_template_client = ProductTemplateClient(**API_ACCESS_CONFIG)
        product_template = {
            "code": "KitPrepagoDTV",
            "name": "Kit Prepago",
            "description": "Kit Prepago",
            "provider_code": "33333333-3",
            "provider_name": "Directv",
            "weight": 20.25,
            "width": 10.5,
            "height": 10.3,
            "depth": 20.4,
            "box_type": 1,
            'packaging_location_code': 'Directv-Fijo'
        }

        result = product_template_client.create(product_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        delivery_order_request_client = DeliveryOrderRequestClient(**API_ACCESS_CONFIG)
        delivery_order_client = DeliveryOrderClient(**API_ACCESS_CONFIG)

        max_products = 3
        product = {
            "code": "",
            "product_template_code": "KitPrepagoDTV",
        }

        requests_count = 15
        for i in range(requests_count):
            # generate random amount of products per delivery order request

            products = []
            products_count = random.randint(1, max_products)
            for j in range(products_count):
                temp = product.copy()
                temp.update({"code": str(uuid.uuid4())})
                products.append(temp)

            chilean_delivery_order_request = {
                "sender_code": "33333333-3",
                "receiver": {
                    "code": "22222222-2",
                    "first_name": "John",
                    "last_name": "Doe",
                    "mobile_phone": "912345678",
                    "email": "john.doe@gmail.com"
                },
                "products": products,
                "destination": {
                    "country_code": "CL",
                    "structure_id": 13132,
                    "street": "Vitacura",
                    "number": "4380",
                    "local": "piso 15",
                    "geo_coding": "Avenida Vitacura 4380, Vitacura",
                    "geo_location": {
                        "lat": -33.398823,
                        "lon": -70.588274
                    },
                    "what3words": "liner.cooking.montage"
                },
                "priority": 1,
                "status": 1
            }

            result = delivery_order_request_client.create(chilean_delivery_order_request)
            self.assertTrue(result.response.status == 200 and result.content)
            time.sleep(0.5)

            result = delivery_order_client.create_from_request(result.content['delivery_order_request_id'])
            self.assertTrue(result.response.status == 200)

if __name__ == '__main__':
    unittest.main()
