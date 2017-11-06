import unittest

import time

from alas_ce0.management.employee import EmployeeClient

from config import API_ACCESS_CONFIG


class TestEmployeeApi(unittest.TestCase):
    def test_crud(self):
        # Employee Tests

        employee_client = EmployeeClient(**API_ACCESS_CONFIG)
        employee = {
            'code': '22222222-2',
            'first_name': 'First Nam',
            'last_name': 'Last Name',
            'birth_date': '1991-01-01',
            'gender': 1,
            'internal_code': '1',
            'status': 1
        }

        result = employee_client.create(employee)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = employee_client.get_by_id(result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)

        result = employee_client.get_by_id('55555555-5')
        self.assertTrue(result.response.status == 404)

        result = employee_client.search({'birth_date': '1991-01-01', 'last_name': 'Last Name'})
        self.assertTrue(result.response.status == 200 and result.content)

        result = employee_client.delete(result.content['items'][0]['code'])
        self.assertTrue(result.response.status == 204)
        time.sleep(0.5)

        result = employee_client.create(employee)
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        employee['first_name'] += 'e'
        result = employee_client.update(employee, result.content['code'])
        self.assertTrue(result.response.status == 200 and result.content)
        time.sleep(0.5)

        result = employee_client.delete("22222222-2")
        self.assertTrue(result.response.status == 204)
        time.sleep(1)


if __name__ == '__main__':
    unittest.main()
