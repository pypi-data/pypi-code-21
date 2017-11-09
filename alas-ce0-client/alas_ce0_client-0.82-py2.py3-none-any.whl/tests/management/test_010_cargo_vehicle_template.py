# coding=utf-8
import time
import unittest

from sdp_dtv.management.vehicle import CargoVehicleTemplateClient
from tests import API_ACCESS_CONFIG


class TestShelfCargoVehicleApi(unittest.TestCase):
    def test_crud(self):
        cargo_vehicle_template_client = CargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        cargo_vehicle_template = {
            "code": "CVT1",
            "cargo_weight": 11765,
            "cargo_volume": 13.0,
            "delivery_cargo_volume": {
                "width": 50.25,
                "height": 60.13,
                "depth": 25.34
            }
        }

        result = cargo_vehicle_template_client.create(cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = cargo_vehicle_template_client.get_by_id(cargo_vehicle_template['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = cargo_vehicle_template_client.get_by_id('sample-cargo-vehicle')
        self.assertTrue(result.response.status == 404)

        result = cargo_vehicle_template_client.search({'code': cargo_vehicle_template['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        result = cargo_vehicle_template_client.delete(cargo_vehicle_template['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = cargo_vehicle_template_client.create(cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        cargo_vehicle_template['cargo_volume'] = 13.1
        result = cargo_vehicle_template_client.update(cargo_vehicle_template, cargo_vehicle_template['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()