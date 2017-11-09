from unittest.case import TestCase
from unittest.mock import patch

import pytest
import requests_mock
from .. import Rumetr, exceptions


@requests_mock.Mocker()
@patch.object(Rumetr, 'check_house', return_value=True)
class TestHouseChecking(TestCase):
    TEST_URL = 'http://api.host.com/developers/dvlpr/complexes/cmplx/houses/hs/appts/{appt}/'

    def setUp(self):
        self.r = Rumetr('test', developer='dvlpr', api_host='http://api.host.com')

    def test_house_ok(self, m, house_checker):
        m.get(self.TEST_URL.format(appt='100500'), json={})
        assert self.r.check_appt('cmplx', 'hs', 100500)
        assert 'cmplx__hs__100500' in self.r._checked_appts  # complex is saved in cached
        assert house_checker.call_count == 1  # delopver has been checked either

    def test_house_is_not_checked_for_the_second_time(self, *args):
        self.r._checked_appts = {'cmplx__hs__100500'}
        assert self.r.check_house('cmplx', 'hs', 100500)  # should return True without a mock

    def test_house_fail(self, m, *args):
        m.get(self.TEST_URL.format(appt='100500'), status_code=404)
        with pytest.raises(exceptions.RumetrApptNotFound):
            assert self.r.check_appt('cmplx', 'hs', 100500)

    def test_appt_exists_1(self, m, *args):
        m.get(self.TEST_URL.format(appt='100500'), json={})
        assert self.r.appt_exists('cmplx', 'hs', 100500)

    def test_appt_exists_2(self, m, *args):
        m.get(self.TEST_URL.format(appt='100500'), json={}, status_code=404)
        assert not self.r.appt_exists('cmplx', 'hs', 100500)
