import urlparse
from unittest import TestCase


class BaseTestCase(TestCase):
    def assertURLEqual(self, first, second, msg=None):
        first_parsed = urlparse.urlparse(first)
        second_parsed = urlparse.urlparse(second)
        self.assertEqual(first_parsed.scheme, second_parsed.scheme, msg=msg)
        self.assertEqual(first_parsed.netloc, second_parsed.netloc, msg=msg)
        self.assertEqual(first_parsed.path, second_parsed.path, msg=msg)
        self.assertEqual(first_parsed.params, second_parsed.params, msg=msg)
        self.assertEqual(first_parsed.fragment, second_parsed.fragment, msg=msg)

        first_qsl = urlparse.parse_qsl(first_parsed.query)
        second_qsl = urlparse.parse_qsl(second_parsed.query)
        self.assertListEqual(sorted(first_qsl), sorted(second_qsl), msg=msg)
