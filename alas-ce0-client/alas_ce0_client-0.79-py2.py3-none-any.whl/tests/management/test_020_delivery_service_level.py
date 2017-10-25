# coding=utf-8
import time
import unittest

from sdp_dtv.management.delivery_service_level import DeliveryServiceLevelClient
from sdp_dtv.management.operations_zone import OperationsZoneClient
from tests import API_ACCESS_CONFIG


class TestDeliveryServiceLevelApi(unittest.TestCase):
    def test_crud(self):
        operations_zone_client = OperationsZoneClient(**API_ACCESS_CONFIG)
        chilean_operations_zone = {
            'code': 'RM-Vitacura',
            'type': 1,
            'name': 'RM-Vitacura',
            'description': 'Zona de Operaciones en Vitacura, Región Metropolitaana',
            'structure_id': 13132
        }

        result = operations_zone_client.create(chilean_operations_zone)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        delivery_service_level_client = DeliveryServiceLevelClient(**API_ACCESS_CONFIG)
        delivery_service_level = {
            "operations_zone_code": chilean_operations_zone['code'],
            "packaging_reception": 70,
            "intermediate_reception": 72,
            "partner_reception": 72,
            "customer_reception": 72,
        }

        result = delivery_service_level_client.create(delivery_service_level)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = delivery_service_level_client.get_by_id(result.content['delivery_service_level_id'])
        self.assertTrue(result.response.status == 200 and result.content)
        delivery_service_level_id = result.content['delivery_service_level_id']

        result = delivery_service_level_client.search({'operations_zone_code': 'RM-Vitacura'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = delivery_service_level_client.get_by_id('delivery-service-level')
        self.assertTrue(result.response.status == 404)

        result = delivery_service_level_client.delete(delivery_service_level_id)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = delivery_service_level_client.create(delivery_service_level)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        delivery_service_level['packaging_reception'] = 72
        result = delivery_service_level_client.update(delivery_service_level,
                                                      result.content['delivery_service_level_id'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
