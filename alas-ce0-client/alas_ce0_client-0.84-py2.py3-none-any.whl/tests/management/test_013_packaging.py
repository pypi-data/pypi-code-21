# coding=utf-8
import time
import unittest

from sdp_dtv.management.employee import EmployeeClient
from sdp_dtv.management.packaging import PackagingLocationClient
from tests import API_ACCESS_CONFIG


class TestPackagingApi(unittest.TestCase):
    def test_crud(self):
        employee_client = EmployeeClient(**API_ACCESS_CONFIG)
        result = employee_client.get_by_id("22222222-2")
        self.assertTrue(result.response.status == 200 and result.content)

        chilean_packaging_location_client = PackagingLocationClient(**API_ACCESS_CONFIG)
        chilean_packaging_location = {
            "code": "Directv-Fijo",
            "type": 1,
            "product_receiver_code": result.content["code"],
            "location":{
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

        result = chilean_packaging_location_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = chilean_packaging_location_client.get_by_id('sample-packaging')
        self.assertTrue(result.response.status == 404)

        result = chilean_packaging_location_client.search({'what3words': 'liner.cooking.montage'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = chilean_packaging_location_client.delete(result.content['items'][0]['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = chilean_packaging_location_client.create(chilean_packaging_location)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        chilean_packaging_location['type'] = 2
        result = chilean_packaging_location_client.update(chilean_packaging_location, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)


if __name__ == '__main__':
    unittest.main()