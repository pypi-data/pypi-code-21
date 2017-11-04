from unittest.case import TestCase

import pytest
import requests_mock
from .. import Rumetr, exceptions


@requests_mock.Mocker()
class TestDeveloperChecking(TestCase):
    TEST_URL = 'http://api.host.com/developers/{developer_id}/'

    def setUp(self):
        self.r = Rumetr('test', 'test', api_host='http://api.host.com')

    def test_developer_is_ok(self, m):
        self.r.developer = '100500'
        m.get(self.TEST_URL.format(developer_id=100500), json={})
        assert self.r.check_developer()
        assert self.r._last_checked_developer == '100500'  # last checked developer id is saved

    def test_developer_is_not_checked_for_the_second_time(self, *args):
        self.r.developer = self.r._last_checked_developer = 100500
        assert self.r.check_developer()

    def test_developer_is_not_found(self, m):
        self.r.developer = '100500'
        m.get(self.TEST_URL.format(developer_id=100500), status_code=404)
        with pytest.raises(exceptions.RumetrDeveloperNotFound):
            self.r.check_developer()
