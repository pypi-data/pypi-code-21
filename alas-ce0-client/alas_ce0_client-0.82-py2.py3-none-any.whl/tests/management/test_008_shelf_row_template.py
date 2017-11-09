# coding=utf-8
import time
import unittest

from sdp_dtv.management.shelf import ShelfRowTemplateClient
from tests import API_ACCESS_CONFIG


class TestShelfRowApi(unittest.TestCase):
    def test_crud(self):
        shelf_row_template_client = ShelfRowTemplateClient(**API_ACCESS_CONFIG)
        shelf_row_template = {
            'code': 'R1',
            'volume': {
                'width': 50.25,
                'height': 60.13,
                'depth': 25.34
            },
            'cells': ['C1']
        }

        result = shelf_row_template_client.create(shelf_row_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_row_template_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_row_template_client.get_by_id('sample-shelf-row')
        self.assertTrue(result.response.status == 404)

        result = shelf_row_template_client.search({'code': shelf_row_template['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_row_template_client.delete(shelf_row_template['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = shelf_row_template_client.create(shelf_row_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_row_template['volume'] = {
                'width': 51.25,
                'height': 61.13,
                'depth': 22.34
            }
        result = shelf_row_template_client.update(shelf_row_template, shelf_row_template['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()