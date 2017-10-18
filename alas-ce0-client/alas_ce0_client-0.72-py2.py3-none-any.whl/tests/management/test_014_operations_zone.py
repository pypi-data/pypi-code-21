# coding=utf-8
import time
import unittest

from sdp_dtv.management.operations_zone import OperationsZoneClient
from tests import API_ACCESS_CONFIG


class TestOperationsZoneApi(unittest.TestCase):
    def test_crud(self):
        operations_zone_client = OperationsZoneClient(**API_ACCESS_CONFIG)
        chilean_operations_zone = {
            'code': 'RM-Vitacura',
            'type': 1,
            'name': 'RM-Vitacur',
            'description': 'Zona de Operaciones en Vitacura, Región Metropolitaana',
            'structure_id': 13132
        }

        result = operations_zone_client.create(chilean_operations_zone)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = operations_zone_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = operations_zone_client.search({'name': 'RM-Vitacura'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = operations_zone_client.get_by_id('operations-zone')
        self.assertTrue(result.response.status == 404)

        result = operations_zone_client.delete(chilean_operations_zone['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = operations_zone_client.create(chilean_operations_zone)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        chilean_operations_zone['name'] = 'RM-Vitacura'
        result = operations_zone_client.update(chilean_operations_zone, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()