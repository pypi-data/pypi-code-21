from unittest import TestCase

from trunity_migrator.utils.static import url_repair


class UrlRepairTestCase(TestCase):

    def test_url_repair_if_url_doesnt_has_base_url(self):
        result_url = url_repair(
            url='/path/to/images/pic1.png',
            url_base='http://example.com'
        )
        self.assertEqual(
            result_url,
            'http://example.com/path/to/images/pic1.png'
        )

    def test_url_repair_if_url_has_base_url(self):
        result_url = url_repair(
            url='http://google.com/path/to/images/pic1.png',
            url_base='http://example.com'
        )
        self.assertEqual(
            result_url,
            'http://google.com/path/to/images/pic1.png'
        )
