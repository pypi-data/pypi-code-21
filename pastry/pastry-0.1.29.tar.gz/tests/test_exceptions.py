import mock
import unittest

from pastry.exceptions import HttpError

def raise_error():
    raise HttpError('message', 'statuscode')


class PastryClientTestCase(unittest.TestCase):


    def test_init(self):
        self.assertRaises(HttpError, raise_error)

    def test_str(self):
        error = HttpError('message', 'statuscode')
        self.assertEqual(str(error), '(statuscode) message')
