# coding=utf-8
import time
import unittest

from sdp_dtv.management.delivery_entity import IntermediateCarrierClient
from tests import API_ACCESS_CONFIG


class TestIntermediateCarrierApi(unittest.TestCase):
    def test_crud(self):
        intermediate_carrier_client = IntermediateCarrierClient(**API_ACCESS_CONFIG)
        intermediate_carrier = {
            'code': '77777777-7',
            'name': 'Rapid Cargo',
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
            'internal_code': '1'
        }

        result = intermediate_carrier_client.create(intermediate_carrier)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = intermediate_carrier_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = intermediate_carrier_client.search({'name': 'Rapid Cargo'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = intermediate_carrier_client.get_by_id('sample-intermediate-carrier')
        self.assertTrue(result.response.status == 404)

        result = intermediate_carrier_client.delete(intermediate_carrier['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = intermediate_carrier_client.create(intermediate_carrier)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        intermediate_carrier['name'] = 'Rapid Cargo'
        result = intermediate_carrier_client.update(intermediate_carrier, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()