# coding=utf-8
import unittest

import time
from sdp_dtv.management.shelf import ShelfCellTemplateClient
from tests import API_ACCESS_CONFIG


class TestShelfCellApi(unittest.TestCase):
    def test_crud(self):
        shelf_cell_template_client = ShelfCellTemplateClient(**API_ACCESS_CONFIG)
        shelf_cell_template = {
            'code': 'C1',
            'volume': {
                'width': 50.25,
                'height': 60.13,
                'depth': 25.34
            }
        }

        result = shelf_cell_template_client.create(shelf_cell_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_cell_template_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_cell_template_client.search({'code': shelf_cell_template['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_cell_template_client.get_by_id('sample-shelf-cell')
        self.assertTrue(result.response.status == 404)

        result = shelf_cell_template_client.delete(shelf_cell_template['code'])
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

        result = shelf_cell_template_client.update(shelf_cell_template, shelf_cell_template['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()