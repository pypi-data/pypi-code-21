
import unittest
import reportutil
from reportutil import _metadata


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # Instantiation
    def test_version(self):
        self.assertEqual(reportutil.__version__, _metadata.__version__, u'Version is incorrect')


if __name__ == u'__main__':
    unittest.main()
