from unittest.case import TestCase
from unittest.mock import patch

import pytest
import requests_mock
from .. import Rumetr, exceptions


@requests_mock.Mocker()
@patch.object(Rumetr, 'check_developer', return_value=True)
class TestComplexChecking(TestCase):
    TEST_URL = 'http://api.host.com/developers/dvlpr/complexes/{complex}/'

    def setUp(self):
        self.r = Rumetr('test', developer='dvlpr', api_host='http://api.host.com')

    def test_complex_ok(self, m, developer_checker):
        m.get(self.TEST_URL.format(complex='100500'), json={})
        assert self.r.check_complex(100500)
        assert 100500 in self.r._checked_complexes  # complex is saved in cached
        assert developer_checker.call_count == 1  # delopver has been checked either

    def test_complex_is_not_checked_for_the_second_time(self, *args):
        self.r._checked_complexes = {100500}
        assert self.r.check_complex(100500)

    def test_complex_fail(self, m, *args):
        m.get(self.TEST_URL.format(complex='100500'), status_code=404)
        with pytest.raises(exceptions.RumetrComplexNotFound):
            assert self.r.check_complex(100500)

    def test_complex_exists_1(self, m, *args):
        m.get(self.TEST_URL.format(complex='100500'), json={})
        assert self.r.complex_exists(100500)

    def test_complex_exists_2(self, m, *args):
        m.get(self.TEST_URL.format(complex='100500'), json={}, status_code=404)
        assert not self.r.complex_exists(100500)
