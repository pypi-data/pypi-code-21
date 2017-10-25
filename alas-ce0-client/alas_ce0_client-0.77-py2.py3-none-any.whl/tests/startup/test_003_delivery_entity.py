# coding=utf-8
import time
import unittest

from sdp_dtv.management.contact import ContactClient
from sdp_dtv.management.delivery_entity import IntermediateCarrierClient, B2BClient, RegionalPartnerClient
from sdp_dtv.management.delivery_service_level import DeliveryServiceLevelClient
from sdp_dtv.management.employee import EmployeeClient
from sdp_dtv.management.manager_assignment import ManagerAssignmentClient
from sdp_dtv.management.operations_zone import OperationsZoneClient
from sdp_dtv.management.packaging import PackagingLocationClient
from tests import API_ACCESS_CONFIG


class TestDeliveryEntity(unittest.TestCase):
    def test_startup(self):
        contact_client = ContactClient(**API_ACCESS_CONFIG)
        contact = {
            'code': '44444444-4',
            'first_name': 'Tom',
            'last_name': 'Roman',
            'land_line': '221345678',
            'mobile_phone': '921345678',
            'email': 'tom.roman@gmail.com',
            'web': 'http://www.tom-roman.com'
        }

        result = contact_client.create(contact)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        operations_zone_client = OperationsZoneClient(**API_ACCESS_CONFIG)
        chilean_operations_zone = {
            'code': 'RM-Vitacura',
            'type': 1,
            'name': 'RM-Vitacura',
            'description': 'Zona de Operaciones en Vitacura, Región Metropolitaana',
            'structure_id': 13132
        }

        result = operations_zone_client.create(chilean_operations_zone)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        chilean_packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)
        result = chilean_packaging_location_client.search({'what3words': 'liner.cooking.montage'})
        if not result.content or len(result.content['items']) == 0:
            employee_client = EmployeeClient(**API_ACCESS_CONFIG)
            result = employee_client.get_by_id("11111111-1")
            self.assertTrue(result.response.status == 200 and result.content)

            chilean_packaging_location = {
                "code": "Directv-Fijo",
                "type": 1,
                "product_receiver_code": result.content["code"],
                "location": {
                    "country_code": "CL",
                    "zone_type": 1,
                    "geo_coding": "Avenida Vitacura 4380, Vitacura, Chile",
                    "geo_location": {
                        "lat": -33.398823,
                        "lon": -70.588274
                    },
                    "what3words": "liner.cooking.montage",
                    "reference": "En la esquina de Vitacura con Américo Vespucio",
                    "structure_id": 13132,
                    "sector": "",
                    "street": "Vitacura",
                    "number": "4380",
                },
                "contact": "44444444-4",
            }

            result = chilean_packaging_location_client.create(chilean_packaging_location)
            self.assertTrue(result.response.status == 200 and result.content)
            time.sleep(0.5)
            packaging_location_code = result.content['code']
        else:
            packaging_location_code = result.content['items'][0]['code']

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
            'packaging_locations': [packaging_location_code],
            'business_activity': 'Televisión Satelital',
            'internal_code': '1'
        }

        result = b2b_client.create(b2b)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        intermediate_carrier_client = IntermediateCarrierClient(**API_ACCESS_CONFIG)
        intermediate_carrier = {
            'code': '77777777-7',
            'name': 'Rapid Cargo',
            'location': {
                'country_code': 'CL',
                'zone_type': 1,
                'geo_coding': 'Avenida Vitacura 4380, Vitacura, Chile',
                'geo_location': {
                    'lat': -33.398823, 'lon': -70.588274
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
            'operations_zone_code': chilean_operations_zone['code'],
            'internal_code': '1'
        }

        result = regional_partner_client.create(regional_partner)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        manager_assignment_client = ManagerAssignmentClient(**API_ACCESS_CONFIG)
        result = manager_assignment_client.search({'operations_zone_code': 'RM-Vitacura'})
        if not result.content or len(result.content['items']) == 0:
            manager_assignment = {
                "operations_zone_code": chilean_operations_zone['code'],
                "delivery_manager_code": "11111111-1",
                "packaging_manager_code": "11111111-1",
                "intermediate_manager_code": "11111111-1",
                "intermediate_carrier_code": "77777777-7",
                "regional_partner_code": "88888888-8",
            }

            result = manager_assignment_client.create(manager_assignment)
            self.assertTrue(result.response.status == 200 and result.content)
            time.sleep(0.5)

        delivery_service_level_client = DeliveryServiceLevelClient(**API_ACCESS_CONFIG)
        result = delivery_service_level_client.search({'operations_zone_code': 'RM-Vitacura'})
        if not result.content or len(result.content['items']) == 0:
            delivery_service_level = {
                "operations_zone_code": chilean_operations_zone['code'],
                "packaging_reception": 72,
                "intermediate_reception": 72,
                "partner_reception": 72,
                "customer_reception": 72,
            }

            result = delivery_service_level_client.create(delivery_service_level)
            self.assertTrue(result.response.status == 200 and result.content)
            time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()
