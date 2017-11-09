# coding=utf-8
import time
import unittest

from alas_ce0.management.shelf import ShelfCellTemplateClient

from alas_ce0.management.shelf import ShelfTemplateClient, ShelfRowTemplateClient

from config import API_ACCESS_CONFIG


class TestShelfApi(unittest.TestCase):
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

        # ShelfRow Tests

        shelf_template_client = ShelfTemplateClient(**API_ACCESS_CONFIG)
        shelf_template = {
            'code': 'S1',
            'rows': [shelf_row_code]
        }

        result = shelf_template_client.create(shelf_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_template_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = shelf_template_client.search({'code': result.content['code']})
        self.assertTrue(result.response.status == 200 and result.content)

        shelf_template_code = result.content['items'][0]['code']
        result = shelf_template_client.get_by_id('sample-shelf-row')
        self.assertTrue(result.response.status == 404)

        result = shelf_template_client.delete(shelf_template_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = shelf_template_client.create(shelf_template)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        shelf_template['rows'] = [shelf_row_code]
        result = shelf_template_client.update(shelf_template, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = shelf_template_client.delete(result.content['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        # Tests Cleanup

        result = shelf_row_template_client.delete(shelf_row_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        result = shelf_cell_template_client.delete(shelf_cell_code)
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
