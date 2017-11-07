import unittest

from tcell_agent.config import CONFIGURATION
from tcell_agent.sensor_events import RedirectSensorEvent


class RedirectSensorEventTest(unittest.TestCase):
    def setUp(self):
        self.orig_hipaa_safe_mode = CONFIGURATION.hipaa_safe_mode
        self.orig_hmac_key = CONFIGURATION.hmac_key

    def tearDown(self):
        CONFIGURATION.hipaa_safe_mode = self.orig_hipaa_safe_mode
        CONFIGURATION.hmac_key = self.orig_hmac_key

    def user_id_missing_hipaa_mode_enabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"

        redirect_event = RedirectSensorEvent("hmac:1.1.1.1",
                                             "GET",
                                             "tcell.io",
                                             "http://tcell.io/some/path?q=erase_me",
                                             "302",
                                             "google.com")
        redirect_event.post_process()
        self.assertEqual(redirect_event["method"], "GET")
        self.assertEqual(redirect_event["remote_addr"], "hmac:1.1.1.1")
        self.assertEqual(redirect_event["from_domain"], "tcell.io")
        self.assertEqual(redirect_event["from"], "http://tcell.io/some/path?q=")
        self.assertEqual(redirect_event["status_code"], "302")
        self.assertEqual(redirect_event["to"], "google.com")

        self.assertIsNone(redirect_event.get("rid", None))
        self.assertIsNone(redirect_event.get("uid", None))
        self.assertIsNone(redirect_event.get("session_id", None))

    def user_present_hipaa_mode_enabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"
        redirect_event = RedirectSensorEvent("hmac:1.1.1.1",
                                             "GET",
                                             "tcell.io",
                                             "http://tcell.io/some/path?q=erase_me",
                                             "302",
                                             "google.com",
                                             "tcelluser@tcell.io")

        redirect_event.post_process()

        self.assertEqual(redirect_event["method"], "GET")
        self.assertEqual(redirect_event["remote_addr"], "hmac:1.1.1.1")
        self.assertEqual(redirect_event["from_domain"], "tcell.io")
        self.assertEqual(redirect_event["from"], "http://tcell.io/some/path?q=")
        self.assertEqual(redirect_event["status_code"], "302")
        self.assertEqual(redirect_event["to"], "google.com")

        self.assertIsNone(redirect_event.get("rid", None))
        self.assertEqual(redirect_event["uid"], "7a5c99b249e48fa7bbd3263029ecc907b24619b4d81361606b19f2696f50e43a")
        self.assertIsNone(redirect_event.get("session_id", None))

    def user_present_hipaa_mode_disabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = False
        CONFIGURATION.hmac_key = "secret_hmac_key"
        redirect_event = RedirectSensorEvent("hmac:1.1.1.1",
                                             "GET",
                                             "tcell.io",
                                             "http://tcell.io/some/path?q=erase_me",
                                             "302",
                                             "google.com",
                                             "tcelluser@tcell.io")

        redirect_event.post_process()

        self.assertEqual(redirect_event["method"], "GET")
        self.assertEqual(redirect_event["remote_addr"], "hmac:1.1.1.1")
        self.assertEqual(redirect_event["from_domain"], "tcell.io")
        self.assertEqual(redirect_event["from"], "http://tcell.io/some/path?q=")
        self.assertEqual(redirect_event["status_code"], "302")
        self.assertEqual(redirect_event["to"], "google.com")

        self.assertIsNone(redirect_event.get("rid", None))
        self.assertEqual(redirect_event["uid"], "tcelluser@tcell.io")
        self.assertIsNone(redirect_event.get("session_id", None))

    def session_id_present_hipaa_mode_enabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"

        redirect_event = RedirectSensorEvent("hmac:1.1.1.1",
                                             "GET",
                                             "tcell.io",
                                             "http://tcell.io/some/path?q=erase_me",
                                             "302",
                                             "google.com",
                                             user_id=None,
                                             session_id="hmacd_session_id")
        redirect_event.post_process()

        self.assertEqual(redirect_event["method"], "GET")
        self.assertEqual(redirect_event["remote_addr"], "hmac:1.1.1.1")
        self.assertEqual(redirect_event["from_domain"], "tcell.io")
        self.assertEqual(redirect_event["from"], "http://tcell.io/some/path?q=")
        self.assertEqual(redirect_event["status_code"], "302")
        self.assertEqual(redirect_event["to"], "google.com")

        self.assertIsNone(redirect_event.get("rid", None))
        self.assertIsNone(redirect_event.get("uid", None))
        self.assertEqual(redirect_event["sid"], "hmacd_session_id")

    def session_id_present_hipaa_mode_disabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = False
        CONFIGURATION.hmac_key = "secret_hmac_key"

        redirect_event = RedirectSensorEvent("hmac:1.1.1.1",
                                             "GET",
                                             "tcell.io",
                                             "http://tcell.io/some/path?q=erase_me",
                                             "302",
                                             "google.com",
                                             user_id=None,
                                             session_id="hmacd_session_id")
        redirect_event.post_process()

        self.assertEqual(redirect_event["method"], "GET")
        self.assertEqual(redirect_event["remote_addr"], "hmac:1.1.1.1")
        self.assertEqual(redirect_event["from_domain"], "tcell.io")
        self.assertEqual(redirect_event["from"], "http://tcell.io/some/path?q=")
        self.assertEqual(redirect_event["status_code"], "302")
        self.assertEqual(redirect_event["to"], "google.com")

        self.assertIsNone(redirect_event.get("rid", None))
        self.assertIsNone(redirect_event.get("uid", None))
        self.assertEqual(redirect_event["sid"], "hmacd_session_id")
