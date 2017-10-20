# coding=utf-8
import time
import unittest

from sdp_dtv.management.shelf import ShelfCellTemplateClient, ShelfRowTemplateClient, ShelfTemplateClient
from sdp_dtv.management.vehicle import CargoVehicleTemplateClient, ShelfCargoVehicleTemplateClient
from tests import API_ACCESS_CONFIG


class TestVehicle(unittest.TestCase):
    def test_startup(self):
        shelf_cell_template_client = ShelfCellTemplateClient(**API_ACCESS_CONFIG)
        shelf_cell_template_1 = {
            'code': 'C1',
            'volume': {
                'width': 85.0,
                'height': 36.0,
                'depth': 30.0
            }
        }

        result = shelf_cell_template_client.create(shelf_cell_template_1)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_row_template_client = ShelfRowTemplateClient(**API_ACCESS_CONFIG)
        shelf_row_template_1 = {
            'code': 'R1',
            'volume': {
                'width': 170.0,
                'height': 36.0,
                'depth': 30.0
            },
            'cells': ['C1', 'C1']
        }

        result = shelf_row_template_client.create(shelf_row_template_1)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_template_client = ShelfTemplateClient(**API_ACCESS_CONFIG)
        shelf_template_1 = {
            'code': 'S1',
            'rows': ['R1', 'R1', 'R1', 'R1']
        }

        result = shelf_template_client.create(shelf_template_1)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        cargo_vehicle_template_client = CargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        cargo_vehicle_template = {
            "code": "CVT1",
            "cargo_weight": 11765,
            "cargo_volume": 0.5,
            "delivery_cargo_volume": {
                "width": 1360.0,
                "height": 288.0,
                "depth": 240.0
            }
        }

        result = cargo_vehicle_template_client.create(cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_cargo_vehicle_template_client = ShelfCargoVehicleTemplateClient(**API_ACCESS_CONFIG)
        shelf_cargo_vehicle_template = {
            'code': 'SCVT1',
            'cargo_vehicle_template_code': 'CVT1',
            'shelf_templates': ['S1', 'S1']
        }

        result = shelf_cargo_vehicle_template_client.create(shelf_cargo_vehicle_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

if __name__ == '__main__':
    unittest.main()
