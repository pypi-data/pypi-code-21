# coding=utf-8
import unittest

import time
from alas_ce0.delivery.delivery_order import DeliveryOrderRequestClient
from alas_ce0.management.contact import ContactClient
from alas_ce0.management.delivery_entity import B2BClient, RegionalPartnerClient
from alas_ce0.management.packaging import PackagingLocationClient
from tests import API_ACCESS_CONFIG


class TestDeliveryOrderRequestApi(unittest.TestCase):
    def test_crud(self):
        delivery_order_request_client = DeliveryOrderRequestClient(**API_ACCESS_CONFIG)
        chilean_delivery_order_request = {
            "sender_code": "33333333-3",
            "receiver": {
                "code": "10101010-1",
                "first_name": "Joh",
                "last_name": "Doe",
                "mobile_phone": "912345678",
                "email": "john.doe@gmail.com"
            },
            "products": [
                {
                    "code": "1234567abcd",
                    "product_template_code": "KitPrepagoDTV",
                }
            ],
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

        delivery_order_request_id = result.content['delivery_order_request_id']
        result = delivery_order_request_client.get_by_id(delivery_order_request_id)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = delivery_order_request_client.get_by_id('123456')
        self.assertTrue(result.response.status == 404)
        time.sleep(0.5)

        result = delivery_order_request_client.search({'product_code': '1234567abcd'})
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = delivery_order_request_client.delete(result.content['items'][0]['delivery_order_request_id'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = delivery_order_request_client.create(chilean_delivery_order_request)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        chilean_delivery_order_request['receiver']['first_name'] += 'n'
        result = delivery_order_request_client.update(
            chilean_delivery_order_request,
            result.content['delivery_order_request_id']
        )
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
