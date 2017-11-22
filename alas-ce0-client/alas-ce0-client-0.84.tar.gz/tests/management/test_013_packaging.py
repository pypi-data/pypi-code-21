# coding=utf-8
import time
import unittest

from alas_ce0.management.contact import ContactClient

from alas_ce0.management.packaging import PackagingLocationClient

from config import API_ACCESS_CONFIG


class TestPackagingLocationApi(unittest.TestCase):
    def test_crud(self):
        # Tests Setup

        contact_client = ContactClient(**API_ACCESS_CONFIG)
        contact = {
            'code': '44444444-4',
            'first_name': 'Contact FirstName',
            'last_name': 'Contact LastName',
            'land_line': '221345678',
            'mobile_phone': '921345678',
            'email': 'contact@gmail.com',
            'web': 'http://www.contact.com'
        }

        result = contact_client.create(contact)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        # PackagingLocation Tests

        packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)
        packaging_location = {
            "code": "Directv-Fijo-Test",
            "type": 1,
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

        result = packaging_location_client.create(packaging_location)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = packaging_location_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = packaging_location_client.get_by_id('sample-packaging')
        self.assertTrue(result.response.status == 404)

        result = packaging_location_client.search({'what3words': 'liner.cooking.montage'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = packaging_location_client.delete("Directv-Fijo-Test")
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = packaging_location_client.create(packaging_location)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        packaging_location['type'] = 2
        result = packaging_location_client.update(packaging_location, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = packaging_location_client.delete("Directv-Fijo-Test")
        self.assertTrue(result.response.status == 204)
        time.sleep(1)

        # Tests Cleanup

        result = contact_client.delete('44444444-4')
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
