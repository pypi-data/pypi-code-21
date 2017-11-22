# coding=utf-8
import time
import unittest

from alas_ce0.management.vehicle import CargoVehicleTemplateClient

from config import API_ACCESS_CONFIG


class TestCargoVehicleApi(unittest.TestCase):
    def test_crud(self):
        # CargoVehicle Tests

        cargo_vehicle_template_client = CargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        cargo_vehicle_template = {
            "brand": "BRAND",
            "model": "MODEL",
            "cargo_weight": 4350,
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

        result = cargo_vehicle_template_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = cargo_vehicle_template_client.search({'code': result.content['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        cargo_vehicle_template_code = result.content['items'][0]['code']
        result = cargo_vehicle_template_client.get_by_id('sample-cargo-vehicle')
        self.assertTrue(result.response.status == 404)

        result = cargo_vehicle_template_client.delete(cargo_vehicle_template_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = cargo_vehicle_template_client.create(cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        cargo_vehicle_template['cargo_volume'] = 13.1
        result = cargo_vehicle_template_client.update(cargo_vehicle_template, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = cargo_vehicle_template_client.delete(result.content['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
