import unittest


class BaseComputeTest(unittest.TestCase):

    def setUp(self):
        from ext_cloud.TestCases.utils import get_cloud_obj
        self.cloud_obj = get_cloud_obj()

    def test_list_instances(self):
        self.cloud_obj.compute.list_instances()


if __name__ == "__main__":
    unittest.main()
