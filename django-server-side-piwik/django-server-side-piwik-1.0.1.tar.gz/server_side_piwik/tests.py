from django.test import TestCase
from unittest import mock
from piwikapi.tracking import PiwikTracker
from .tasks import record_analytic


class ServerSidePiwikTestCase(TestCase):
    @mock.patch('server_side_piwik.tasks.record_analytic.delay')
    def test_middleware(self, mocked):
        expected_headers = {'HTTPS': False, 'REMOTE_ADDR': '127.0.0.1', 'SERVER_NAME': 'testserver', 'PATH_INFO': '/admin/', 'QUERY_STRING': ''}
        expected_ip = '127.0.0.1'
        self.client.get('/admin/')
        mocked.assert_called_once_with(expected_headers, expected_ip)

    @mock.patch('piwikapi.tracking.PiwikTracker.do_track_page_view')
    def test_record_analytic(self, mocked):
        headers = {
            'HTTPS': False,
            'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'REMOTE_ADDR': '172.23.0.1',
            'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.9',
            'SERVER_NAME': 'a96cb4a08d4d',
            'PATH_INFO': '/admin/login/',
            'QUERY_STRING': 'next=/admin/',
        }
        ip = '172.23.0.1'
        record_analytic(headers, ip)
        mocked.assert_called_once_with('/admin/login/')
