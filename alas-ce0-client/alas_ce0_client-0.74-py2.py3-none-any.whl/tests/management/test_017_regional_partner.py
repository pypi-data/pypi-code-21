# coding=utf-8
import time
import unittest

from sdp_dtv.management.delivery_entity import RegionalPartnerClient
from sdp_dtv.management.operations_zone import OperationsZoneClient
from tests import API_ACCESS_CONFIG


class TestRegionalPartnerApi(unittest.TestCase):
    def test_crud(self):
        operations_zone_client = OperationsZoneClient(**API_ACCESS_CONFIG)
        result = operations_zone_client.search({'name': 'RM-Vitacura'})
        operations_zone_code = result.content['items'][0]['code']

        regional_partner_client = RegionalPartnerClient(**API_ACCESS_CONFIG)
        regional_partner = {
            'code': '88888888-8',
            'name': 'Last Mile Cargo',
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
            'operations_zone_code': operations_zone_code,
            'internal_code': '1'
        }

        result = regional_partner_client.create(regional_partner)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = regional_partner_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = regional_partner_client.search({'name': 'Last Mile Cargo'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = regional_partner_client.get_by_id('sample-regional-partner')
        self.assertTrue(result.response.status == 404)

        result = regional_partner_client.delete(regional_partner['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = regional_partner_client.create(regional_partner)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        regional_partner['name'] = 'Last Mile Cargo'
        result = regional_partner_client.update(regional_partner, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()