from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_sdbmyuw import get_app_status, get_appstatus_url, invalid_system_key
from uw_sdbmyuw.exceptions import InvalidSystemKey
from uw_sdbmyuw.util import fdao_sdbmyuw_override


@fdao_sdbmyuw_override
class AppStatusTest(TestCase):

    def test_get_appstatus_url(self):
        self.assertEqual(get_appstatus_url('000000000'),
                         '/sdb_MyUW/appstatus.asp?s=000000000')

    def test_invalid_system_key(self):
        self.assertRaises(InvalidSystemKey,
                          get_app_status,
                          '000000000')
        self.assertFalse(invalid_system_key('000000001'))
        self.assertTrue(invalid_system_key(None))

    def test_get_app_status(self):
        status = get_app_status('000000001')
        self.assertIsNotNone(status)
        self.assertTrue(status.is_freshman)
        self.assertTrue(status.is_seattle)
        self.assertTrue(status.is_bothell)

        status = get_app_status('000000002')
        self.assertTrue(status.is_international_post_bac)
        self.assertTrue(status.is_tacoma)
        self.assertTrue(status.is_bothell)

        status = get_app_status('000000003')
        self.assertTrue(status.is_returning)
        self.assertTrue(status.is_seattle)

        status = get_app_status('000000004')
        self.assertTrue(status.is_transfer)
        self.assertTrue(status.is_seattle)

        status = get_app_status('000000005')
        self.assertTrue(status.is_ug_non_matriculated)
        self.assertTrue(status.is_bothell)
        self.assertEqual(status.quarter, "winter")
        self.assertEqual(status.year, 2018)

        status = get_app_status('000000006')
        self.assertTrue(status.no_ug_app)
