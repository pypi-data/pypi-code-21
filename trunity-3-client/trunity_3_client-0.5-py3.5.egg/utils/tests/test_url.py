from unittest import TestCase

from utils.url import Url


class UrlTestCase(TestCase):

    def setUp(self):
        self.root = 'http://test.com/path/to/paradise'

    def test_url_list(self):
        url = Url(self.root)
        url.tail = 'foo'

        self.assertEqual(
            url.list,
            'http://test.com/path/to/paradise/foo',
            'List url does not constructed properly!'
        )

    def test_list_if_root_has_slash_in_the_end(self):
        root = self.root + '/'
        url = Url(root)
        url.tail = 'foo'

        self.assertEqual(
            url.list,
            'http://test.com/path/to/paradise/foo'
        )

    def test_detail(self):
        url = Url(self.root)
        url.tail = 'foo'

        self.assertEqual(
            url.detail,
            'http://test.com/path/to/paradise/foo/{id}',
            'Detail url does not constructed properly!'
        )

    def test_raises_error_if_tail_is_not_set(self):
        url = Url(self.root)

        # miss url.tail = 'foo'

        with self.assertRaises(NotImplementedError):
            url.list
