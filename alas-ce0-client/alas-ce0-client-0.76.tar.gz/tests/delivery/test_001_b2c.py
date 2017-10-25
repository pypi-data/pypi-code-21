# coding=utf-8
import time
import unittest

from alas_ce0.delivery.b2c import B2CClient

from config import API_ACCESS_CONFIG


class TestB2CApi(unittest.TestCase):
    def test_crud(self):
        # B2C Tests

        b2c_client = B2CClient(**API_ACCESS_CONFIG)
        b2c = {
            "code": "10101010-1",
            "first_name": "Joh",
            "last_name": "Doe",
            "mobile_phone": "912345678",
            "email": "john.doe@gmail.com"
        }

        result = b2c_client.create(b2c)
        self.assertTrue(result.response.status == 200 and result.content)

        result = b2c_client.get_by_id("10101010-1")
        self.assertTrue(result.response.status == 200 and result.content)

        result = b2c_client.get_by_id('123456')
        self.assertTrue(result.response.status == 404)

        result = b2c_client.search({'first_name': 'Joh'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = b2c_client.delete("10101010-1")
        self.assertTrue(result.response.status == 204)

        result = b2c_client.create(b2c)
        self.assertTrue(result.response.status == 200 and result.content)

        b2c['first_name'] += 'n'
        result = b2c_client.update(b2c, "10101010-1")
        self.assertTrue(result.response.status == 200 and result.content)

        result = b2c_client.delete("10101010-1")
        self.assertTrue(result.response.status == 204)


if __name__ == '__main__':
    unittest.main()
