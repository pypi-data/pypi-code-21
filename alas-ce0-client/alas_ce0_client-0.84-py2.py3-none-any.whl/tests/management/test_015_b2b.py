# coding=utf-8
import time
import unittest

from sdp_dtv.management.delivery_entity import B2BClient
from sdp_dtv.management.packaging import PackagingLocationClient
from tests import API_ACCESS_CONFIG


class TestB2BApi(unittest.TestCase):
    def test_crud(self):
        chilean_packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)

        result = chilean_packaging_location_client.search({'what3words': 'liner.cooking.montage'})
        self.assertTrue(result.response.status == 200 and result.content)

        b2b_client = B2BClient(**API_ACCESS_CONFIG)
        b2b = {
            'code': '33333333-3',
            'name': 'Directv',
            'location': {
                'country_code': 'CL',
                'zone_type': 1,
                'geo_coding': 'Avenida Vitacura 4380, Vitacura, Chile',
                'geo_location': {
                    'lat': -33.398823,
                    'lon': -70.588274
                },
                'what3words': 'liner.cooking.montage',
                'reference': 'En la esquina de Vitacura con Américo Vespucio',
                'structure_id': 13132,
                'street': 'Vitacura',
                'number': '4380',
                'sector': '',
            },
            'packaging_locations': [result.content['items'][0]['code']],
            'business_activity': 'Televisión Satelital',
            'internal_code': '1'
        }

        result = b2b_client.create(b2b)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = b2b_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = b2b_client.search({'name': 'Directv'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = b2b_client.get_by_id('sample-b2b')
        self.assertTrue(result.response.status == 404)

        result = b2b_client.delete(b2b['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = b2b_client.create(b2b)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        b2b['name'] = 'Directv'
        result = b2b_client.update(b2b, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()