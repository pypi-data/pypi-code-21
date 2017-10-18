# coding=utf-8
import unittest

import time
from alas_ce0.management.shelf import ShelfCellTemplateClient

from config import API_ACCESS_CONFIG


class TestShelfCellApi(unittest.TestCase):
    def test_crud(self):
        # ShelfCell Tests

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

        result = shelf_cell_template_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_cell_template_client.search({'code': result.content['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        shelf_cell_template_code = result.content['items'][0]['code']
        result = shelf_cell_template_client.get_by_id('sample-shelf-cell')
        self.assertTrue(result.response.status == 404)

        result = shelf_cell_template_client.delete(shelf_cell_template_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = shelf_cell_template_client.create(shelf_cell_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_cell_template['volume'] = {
            'width': 51.25,
            'height': 61.13,
            'depth': 22.34
        }

        result = shelf_cell_template_client.update(shelf_cell_template, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_cell_template_client.delete(shelf_cell_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
