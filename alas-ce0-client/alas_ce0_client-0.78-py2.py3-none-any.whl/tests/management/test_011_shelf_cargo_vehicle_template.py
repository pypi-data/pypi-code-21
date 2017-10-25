# coding=utf-8
import time
import unittest

from sdp_dtv.management.vehicle import ShelfCargoVehicleTemplateClient
from tests import API_ACCESS_CONFIG


class TestShelfCargoVehicleApi(unittest.TestCase):
    def test_crud(self):
        shelf_cargo_vehicle_template_client = ShelfCargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        shelf_cargo_vehicle_template = {
            'code': 'SCVT1',
            'cargo_vehicle_template_code': 'CVT1',
            'shelf_templates': ['S1']
        }

        result = shelf_cargo_vehicle_template_client.create(shelf_cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_cargo_vehicle_template_client.get_by_id(shelf_cargo_vehicle_template['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_cargo_vehicle_template_client.get_by_id('sample-shelf-cargo')
        self.assertTrue(result.response.status == 404)

        result = shelf_cargo_vehicle_template_client.search({'code': shelf_cargo_vehicle_template['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_cargo_vehicle_template_client.delete(shelf_cargo_vehicle_template['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = shelf_cargo_vehicle_template_client.create(shelf_cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_cargo_vehicle_template['cargo_vehicle_template_code'] = 'CVT1'
        result = shelf_cargo_vehicle_template_client.update(
            shelf_cargo_vehicle_template, shelf_cargo_vehicle_template['code']
        )
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()