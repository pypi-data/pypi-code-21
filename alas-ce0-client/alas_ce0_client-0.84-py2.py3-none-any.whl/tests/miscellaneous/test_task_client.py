import unittest

from sdp_dtv.management.task import TaskClient
from tests import API_ACCESS_CONFIG


class TestTaskClient(unittest.TestCase):
    def test_queue(self):
        task_client = TaskClient(**API_ACCESS_CONFIG)

        result = task_client.enqueue('delivery-order')
        self.assertTrue(result.response.status == 200)

if __name__ == '__main__':
    unittest.main()
