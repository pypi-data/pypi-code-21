# coding=utf-8
import time
import unittest

from alas_ce0.management.shelf import ShelfCellTemplateClient

from alas_ce0.management.shelf import ShelfRowTemplateClient, ShelfTemplateClient
from alas_ce0.management.vehicle import ShelfCargoVehicleTemplateClient, CargoVehicleTemplateClient

from config import API_ACCESS_CONFIG


class TestShelfCargoVehicleApi(unittest.TestCase):
    def test_crud(self):
        # Tests Setup

        shelf_cell_template_client = ShelfCellTemplateClient(**API_ACCESS_CONFIG)
        shelf_cell_template = {
            'volume': {
                'width': 50.25,
                'height': 60.13,
                'depth': 25.34
            }
        }

        result = shelf_cell_template_client.create(shelf_cell_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)
        shelf_cell_code = result.content['code']

        shelf_row_template_client = ShelfRowTemplateClient(**API_ACCESS_CONFIG)
        shelf_row_template = {
            'volume': {
                'width': 50.25,
                'height': 60.13,
                'depth': 25.34
            },
            'cells': [shelf_cell_code]
        }

        result = shelf_row_template_client.create(shelf_row_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)
        shelf_row_code = result.content['code']

        shelf_template_client = ShelfTemplateClient(**API_ACCESS_CONFIG)
        shelf_template = {
            'code': 'S1',
            'rows': [shelf_row_code]
        }

        result = shelf_template_client.create(shelf_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)
        shelf_code = result.content['code']

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
        cargo_vehicle_code = result.content['code']

        # ShelfCargoVehicle Tests

        shelf_cargo_vehicle_template_client = ShelfCargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        shelf_cargo_vehicle_template = {
            'cargo_vehicle_template_code': cargo_vehicle_code,
            'shelf_templates': [shelf_code]
        }

        result = shelf_cargo_vehicle_template_client.create(shelf_cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_cargo_vehicle_template_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_cargo_vehicle_template_client.search({'code': result.content['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        shelf_cargo_vehicle_template_code = result.content['items'][0]['code']
        result = shelf_cargo_vehicle_template_client.get_by_id('sample-shelf-cargo')
        self.assertTrue(result.response.status == 404)

        result = shelf_cargo_vehicle_template_client.delete(shelf_cargo_vehicle_template_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = shelf_cargo_vehicle_template_client.create(shelf_cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_cargo_vehicle_template['cargo_vehicle_template_code'] = cargo_vehicle_code
        result = shelf_cargo_vehicle_template_client.update(
            shelf_cargo_vehicle_template, result.content['code']
        )
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_cargo_vehicle_template_client.delete(result.content['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        # Tests Cleanup

        result = cargo_vehicle_template_client.delete(cargo_vehicle_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = shelf_template_client.delete(shelf_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = shelf_row_template_client.delete(shelf_row_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = shelf_cell_template_client.delete(shelf_cell_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
