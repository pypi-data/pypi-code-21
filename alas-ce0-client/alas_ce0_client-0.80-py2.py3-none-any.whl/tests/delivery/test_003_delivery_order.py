# coding=utf-8
import calendar
import time
import unittest

import datetime
from alas_ce0.delivery.delivery_order import DeliveryOrderClient, CUSTOMER_AGENDA, PACKAGING_AGENDA, \
    REGIONAL_PARTNER_CODE_TYPE, SENDER_CODE_TYPE
from tests import API_ACCESS_CONFIG


class TestDeliveryOrderApi(unittest.TestCase):
    def test_crud(self):
        delivery_order_client = DeliveryOrderClient(**API_ACCESS_CONFIG)
        delivery_order = {
            "code": "CLAAAREUMADEtise17031000001",
            "packages": [
                {
                    "code": "se17031000001U",
                    "package_template_code": "Box1",
                    "status": 1,
                    "products": [
                        {
                            "code": "1234567abcd",
                            "product_template_code": "KitPrepagoDTV",
                        }
                    ]
                }
            ],
            "sender_code": "33333333-3",
            "receiver_code": "10101010-1",
            "status": 1,
            "statuses": [1],
            "priority": 1,
            "product_receiver_code": "22222222-2",
            "packaging_manager_code": "22222222-2",
            "packaging_location_code": "Directv-Fijo",
            "intermediate_manager_code": "22222222-2",
            "intermediate_carrier_code": "77777777-7",
            "regional_partner_code": "88888888-8",
            "delivery_manager_code": "22222222-2",
            "destination": {
                "country_code": "CL",
                "structure_id": 16500,
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
            "reception_time_info": {
                "packaging_expected": "2017-01-05T10:00:00",
                "packaging_actual": "2017-01-05T10:01:00",
                "intermediate_expected": "2017-01-05T11:00:00",
                "intermediate_actual": "2017-01-05T11:01:00",
                "partner_expected": "2017-01-05T12:00:00",
                "partner_actual": "2017-01-05T12:01:00",
                "customer_expected": "2017-01-05T13:00:00",
                "customer_actual": "2017-01-05T13:01:00",
            },
        }

        result = delivery_order_client.create(delivery_order)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        delivery_order_id = result.content['code']
        result = delivery_order_client.get_by_id(delivery_order_id)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = delivery_order_client.get_by_id('123456')
        self.assertTrue(result.response.status == 404)
        time.sleep(0.5)

        result = delivery_order_client.search({'sender_name': 'Directv'})
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = delivery_order_client.delete(delivery_order_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = delivery_order_client.create(delivery_order)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        delivery_order['reception_time_info']['packaging_actual'] = "2017-01-05T10:02:00"
        result = delivery_order_client.update(delivery_order,result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = delivery_order_client.get_events(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content and len(result.content['items']) == 2)
        time.sleep(0.5)

        today = datetime.date.today()
        first_weekday, days_num = calendar.monthrange(today.year, today.month)

        date_from = today.replace(day=1).strftime("%Y-%m-%d")
        date_to = today.replace(day=days_num).strftime("%Y-%m-%d")
        result = delivery_order_client.get_agenda(
            date_from,
            date_to,
            [PACKAGING_AGENDA, CUSTOMER_AGENDA],
            {SENDER_CODE_TYPE: '33333333-3', REGIONAL_PARTNER_CODE_TYPE: '33333333-3'}
        )
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
