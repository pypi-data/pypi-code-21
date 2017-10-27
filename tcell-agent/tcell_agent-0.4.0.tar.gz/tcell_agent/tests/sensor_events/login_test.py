import unittest

from tcell_agent.config import CONFIGURATION
from tcell_agent.sensor_events import LoginEvent


class LoginEventTest(unittest.TestCase):
    def setUp(self):
        self.orig_hipaa_safe_mode = CONFIGURATION.hipaa_safe_mode
        self.orig_hmac_key = CONFIGURATION.hmac_key

    def tearDown(self):
        CONFIGURATION.hipaa_safe_mode = self.orig_hipaa_safe_mode
        CONFIGURATION.hmac_key = self.orig_hmac_key

    def user_id_missing_hipaa_mode_enabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"

        login_event = LoginEvent().success(
            None,
            "user_agent",
            None,
            "hmac:1.1.1.1",
            [],
            "/users/sign_in?q=erase_me"
        )

        login_event.post_process()

        self.assertIsNone(login_event.get("user_id", None))
        self.assertEqual(login_event["user_agent"], "user_agent")
        self.assertIsNone(login_event.get("referrer", None))
        self.assertEqual(login_event["remote_addr"], "hmac:1.1.1.1")
        self.assertIsNone(login_event.get("header_keys", None))
        self.assertEqual(login_event["document_uri"], "/users/sign_in?q=")

    def user_id_present_hipaa_mode_enabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"

        login_event = LoginEvent().success(
            "tcelluser@tcell.io",
            "user_agent",
            None,
            "hmac:1.1.1.1",
            [],
            "/users/sign_in?q=erase_me"
        )

        login_event.post_process()

        self.assertEqual(login_event["user_id"], "7a5c99b249e48fa7bbd3263029ecc907b24619b4d81361606b19f2696f50e43a")
        self.assertEqual(login_event["user_agent"], "user_agent")
        self.assertIsNone(login_event.get("referrer", None))
        self.assertEqual(login_event["remote_addr"], "hmac:1.1.1.1")
        self.assertIsNone(login_event.get("header_keys", None))
        self.assertEqual(login_event["document_uri"], "/users/sign_in?q=")

    def user_id_present_hipaa_mode_disabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = False
        CONFIGURATION.hmac_key = "secret_hmac_key"

        login_event = LoginEvent().success(
            "tcelluser@tcell.io",
            "user_agent",
            None,
            "hmac:1.1.1.1",
            [],
            "/users/sign_in?q=erase_me"
        )

        login_event.post_process()

        self.assertEqual(login_event["user_id"], "tcelluser@tcell.io")
        self.assertEqual(login_event["user_agent"], "user_agent")
        self.assertIsNone(login_event.get("referrer", None))
        self.assertEqual(login_event["remote_addr"], "hmac:1.1.1.1")
        self.assertIsNone(login_event.get("header_keys", None))
        self.assertEqual(login_event["document_uri"], "/users/sign_in?q=")

    def referrer_present_hipaa_mode_enabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"

        login_event = LoginEvent().success(
            None,
            "user_agent",
            "http://tcell.io/users/sign_in?q=erase_me",
            "hmac:1.1.1.1",
            [],
            "/users/sign_in?q=erase_me"
        )

        login_event.post_process()

        self.assertIsNone(login_event.get("user_id", None))
        self.assertEqual(login_event["user_agent"], "user_agent")
        self.assertEqual(login_event["referrer"], "11b8b235371031ac100bbae1c642fab9097208735d2d32606ad17855254c85d9")
        self.assertEqual(login_event["remote_addr"], "hmac:1.1.1.1")
        self.assertIsNone(login_event.get("header_keys", None))
        self.assertEqual(login_event["document_uri"], "/users/sign_in?q=")

    def referrer_present_hipaa_mode_disabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = False
        CONFIGURATION.hmac_key = "secret_hmac_key"

        login_event = LoginEvent().success(
            None,
            "user_agent",
            "http://tcell.io/users/sign_in?q=erase_me",
            "hmac:1.1.1.1",
            [],
            "/users/sign_in?q=erase_me"
        )

        login_event.post_process()

        self.assertIsNone(login_event.get("user_id", None))
        self.assertEqual(login_event["user_agent"], "user_agent")
        self.assertEqual(login_event["referrer"], "http://tcell.io/users/sign_in?q=")
        self.assertEqual(login_event["remote_addr"], "hmac:1.1.1.1")
        self.assertIsNone(login_event.get("header_keys", None))
        self.assertEqual(login_event["document_uri"], "/users/sign_in?q=")

    def sessio_id_present_hipaa_mode_enabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = True
        CONFIGURATION.hmac_key = "secret_hmac_key"

        login_event = LoginEvent().success(
            None,
            "user_agent",
            None,
            "hmac:1.1.1.1",
            [],
            "/users/sign_in?q=erase_me",
            "hmacd_session_id"
        )

        login_event.post_process()

        self.assertIsNone(login_event.get("user_id", None))
        self.assertEqual(login_event["user_agent"], "user_agent")
        self.assertIsNone(login_event.get("referrer", None))
        self.assertEqual(login_event["remote_addr"], "hmac:1.1.1.1")
        self.assertIsNone(login_event.get("header_keys", None))
        self.assertEqual(login_event["document_uri"], "/users/sign_in?q=")
        self.assertEqual(login_event["session"], "hmacd_session_id")

    def session_id_present_hipaa_mode_disabled_post_process_test(self):
        CONFIGURATION.hipaa_safe_mode = False
        CONFIGURATION.hmac_key = "secret_hmac_key"

        login_event = LoginEvent().success(
            None,
            "user_agent",
            None,
            "hmac:1.1.1.1",
            [],
            "/users/sign_in?q=erase_me",
            "hmacd_session_id"
        )

        login_event.post_process()

        self.assertIsNone(login_event.get("user_id", None))
        self.assertEqual(login_event["user_agent"], "user_agent")
        self.assertIsNone(login_event.get("referrer", None))
        self.assertEqual(login_event["remote_addr"], "hmac:1.1.1.1")
        self.assertIsNone(login_event.get("header_keys", None))
        self.assertEqual(login_event["document_uri"], "/users/sign_in?q=")
        self.assertEqual(login_event["session"], "hmacd_session_id")
