import sys

# features from py 3.0 are used in order to set up the tests properly
if sys.version_info >= (3, 0):
    import unittest

    from types import ModuleType

    from mock import MagicMock, patch

    from tcell_agent.agent import TCellAgent
    from tcell_agent.instrumentation.hooks.login_fraud import _instrument

    def send_login_event(status,  # pylint: disable=unused-argument
                         session_id,  # pylint: disable=unused-argument
                         user_agent,  # pylint: disable=unused-argument
                         referrer,  # pylint: disable=unused-argument
                         remote_addr,  # pylint: disable=unused-argument
                         header_keys,  # pylint: disable=unused-argument
                         user_id,  # pylint: disable=unused-argument
                         document_uri,  # pylint: disable=unused-argument
                         user_valid=None):  # pylint: disable=unused-argument
        pass

    def send_django_login_event(status, django_request, user_id, session_id, user_valid=None):   # pylint: disable=unused-argument
        pass

    def send_flask_login_event(status, flask_request, user_id, session_id, user_valid=None):  # pylint: disable=unused-argument
        pass


    m_login = ModuleType("tcell_hooks")  # noqa
    mv_login = ModuleType("v1")  # noqa


    class HooksTest(unittest.TestCase):  # noqa
        @classmethod
        def setUpClass(cls):
            m_login.__file__ = m_login.__name__ + ".py"
            m_login.__path__ = []
            mv_login.__file__ = mv_login.__name__ + ".py"
            sys.modules["tcell_hooks"] = m_login
            sys.modules["tcell_hooks.v1"] = mv_login

            setattr(m_login, "v1", mv_login)
            setattr(mv_login, "LOGIN_SUCCESS", "success")
            setattr(mv_login, "LOGIN_FAILURE", "failure")
            setattr(mv_login, "send_login_event", send_login_event)
            setattr(mv_login, "send_django_login_event", send_django_login_event)
            setattr(mv_login, "send_flask_login_event", send_flask_login_event)

            _instrument()

        @classmethod
        def tearDownClass(cls):
            del sys.modules["tcell_hooks"]
            del sys.modules["tcell_hooks.v1"]

        def login_success_hooks_test(self):
            patched_login_fraud_policy = MagicMock(is_enabled=True, login_success_enabled=True)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_SUCCESS,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertTrue(patched_send.called)
                    args, _ = patched_send.call_args
                    event = args[0]
                    self.assertEqual(event["event_type"], "login")
                    self.assertSetEqual(set(event["header_keys"]), set(["HOST", "REFERER", "USER_AGENT"]))
                    self.assertEqual(event["session"], "d9599221c57bcbeb5dee38cb6eeb0a60")
                    self.assertEqual(event["event_name"], "login-success")
                    self.assertEqual(event["remote_addr"], "192.168.99.1")
                    self.assertEqual(event["user_id"], "tcell@tcell.io")
                    self.assertEqual(event["user_agent"], "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")

        def login_failure_hooks_test(self):
            patched_login_fraud_policy = MagicMock(is_enabled=True, login_failed_enabled=True)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_FAILURE,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertTrue(patched_send.called)
                    args, _ = patched_send.call_args
                    event = args[0]
                    self.assertEqual(event["event_type"], "login")
                    self.assertSetEqual(set(event["header_keys"]), set(["HOST", "REFERER", "USER_AGENT"]))
                    self.assertEqual(event["session"], "d9599221c57bcbeb5dee38cb6eeb0a60")
                    self.assertEqual(event["event_name"], "login-failure")
                    self.assertEqual(event["remote_addr"], "192.168.99.1")
                    self.assertEqual(event["user_id"], "tcell@tcell.io")
                    self.assertEqual(event["user_agent"], "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")

        def django_login_success_hooks_test(self):
            django_request = MagicMock(
                "FakeRequest",
                META={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ..."})
            django_request.get_full_path = MagicMock(return_value="/users/auth/doorkeeper/callbackuri")

            patched_login_fraud_policy = MagicMock(is_enabled=True, login_success_enabled=True)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_django_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_django_login_event(
                        mv_login.LOGIN_SUCCESS,
                        django_request,
                        "tcell@tcell.io",
                        "124KDJFL3234")

                    self.assertTrue(patched_send.called)
                    args, _ = patched_send.call_args
                    event = args[0]
                    self.assertEqual(event["event_type"], "login")
                    self.assertSetEqual(set(event["header_keys"]), set(["HOST", "USER_AGENT"]))
                    self.assertEqual(event["session"], "d9599221c57bcbeb5dee38cb6eeb0a60")
                    self.assertEqual(event["event_name"], "login-success")
                    self.assertEqual(event["remote_addr"], "192.168.99.1")
                    self.assertEqual(event["user_id"], "tcell@tcell.io")
                    self.assertEqual(event["user_agent"], "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")

        def django_login_failure_hooks_test(self):
            django_request = MagicMock(
                "FakeRequest",
                META={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ..."})
            django_request.get_full_path = MagicMock(return_value="/users/auth/doorkeeper/callbackuri")

            patched_login_fraud_policy = MagicMock(is_enabled=True, login_failed_enabled=True)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_django_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_django_login_event(
                        mv_login.LOGIN_FAILURE,
                        django_request,
                        "tcell@tcell.io",
                        "124KDJFL3234")

                    self.assertTrue(patched_send.called)
                    args, _ = patched_send.call_args
                    event = args[0]
                    self.assertEqual(event["event_type"], "login")
                    self.assertSetEqual(set(event["header_keys"]), set(["HOST", "USER_AGENT"]))
                    self.assertEqual(event["session"], "d9599221c57bcbeb5dee38cb6eeb0a60")
                    self.assertEqual(event["event_name"], "login-failure")
                    self.assertEqual(event["remote_addr"], "192.168.99.1")
                    self.assertEqual(event["user_id"], "tcell@tcell.io")
                    self.assertEqual(event["user_agent"], "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")

        def flask_login_success_hooks_test(self):
            flask_request = MagicMock(
                "FakeRequest",
                url="/users/auth/doorkeeper/callbackuri",
                environ={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ..."})

            patched_login_fraud_policy = MagicMock(is_enabled=True, login_success_enabled=True)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_flask_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_flask_login_event(
                        mv_login.LOGIN_SUCCESS,
                        flask_request,
                        "tcell@tcell.io",
                        "124KDJFL3234")

                    self.assertTrue(patched_send.called)
                    args, _ = patched_send.call_args
                    event = args[0]
                    self.assertEqual(event["event_type"], "login")
                    self.assertSetEqual(set(event["header_keys"]), set(["HOST", "USER_AGENT"]))
                    self.assertEqual(event["session"], "d9599221c57bcbeb5dee38cb6eeb0a60")
                    self.assertEqual(event["event_name"], "login-success")
                    self.assertEqual(event["remote_addr"], "192.168.99.1")
                    self.assertEqual(event["user_id"], "tcell@tcell.io")
                    self.assertEqual(event["user_agent"], "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")

        def flask_login_failure_hooks_test(self):
            flask_request = MagicMock(
                "FakeRequest",
                url="/users/auth/doorkeeper/callbackuri",
                environ={
                    "REMOTE_ADDR": "192.168.99.1",
                    "HTTP_HOST": "http://192.168.99.1",
                    "HTTP_USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ..."})

            patched_login_fraud_policy = MagicMock(is_enabled=True, login_failed_enabled=True)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_flask_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_flask_login_event(
                        mv_login.LOGIN_FAILURE,
                        flask_request,
                        "tcell@tcell.io",
                        "124KDJFL3234")

                    self.assertTrue(patched_send.called)
                    args, _ = patched_send.call_args
                    event = args[0]
                    self.assertEqual(event["event_type"], "login")
                    self.assertSetEqual(set(event["header_keys"]), set(["HOST", "USER_AGENT"]))
                    self.assertEqual(event["session"], "d9599221c57bcbeb5dee38cb6eeb0a60")
                    self.assertEqual(event["event_name"], "login-failure")
                    self.assertEqual(event["remote_addr"], "192.168.99.1")
                    self.assertEqual(event["user_id"], "tcell@tcell.io")
                    self.assertEqual(event["user_agent"], "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...")

        def unknown_status_hooks_test(self):
            mock_logger = MagicMock()
            mock_logger.error.return_value = None

            patched_login_fraud_policy = MagicMock(is_enabled=True, login_success_enabled=True, login_failed_enabled=True)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    with patch("tcell_agent.instrumentation.hooks.login_fraud.get_logger") as patched_get_logger:
                        patched_get_logger.return_value = mock_logger

                        from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                        send_login_event(
                            "blergh",
                            "124KDJFL3234",
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                            "http://192.168.99.100:3000/",
                            "192.168.99.1",
                            ["HOST", "USER_AGENT", "REFERER"],
                            "tcell@tcell.io",
                            "/users/auth/doorkeeper/callbackuri")

                        self.assertFalse(patched_send.called)
                        mock_logger.error.assert_called_once_with("Unkown login status: blergh")

        def login_success_disabled_login_send_test(self):
            patched_login_fraud_policy = MagicMock(is_enabled=True, login_success_enabled=False)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_SUCCESS,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertFalse(patched_send.called)

        def login_failed_disabled_login_send_test(self):
            patched_login_fraud_policy = MagicMock(is_enabled=True, login_failed_enabled=False)
            with patch.object(TCellAgent, "get_policy", return_value=patched_login_fraud_policy):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_FAILURE,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertFalse(patched_send.called)

        def no_login_policy_login_send_test(self):
            with patch.object(TCellAgent, "get_policy", return_value=None):
                with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                    from tcell_hooks.v1 import send_login_event  # pylint: disable=import-error,no-name-in-module,redefined-outer-name
                    send_login_event(
                        mv_login.LOGIN_FAILURE,
                        "124KDJFL3234",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) ...",
                        "http://192.168.99.100:3000/",
                        "192.168.99.1",
                        ["HOST", "USER_AGENT", "REFERER"],
                        "tcell@tcell.io",
                        "/users/auth/doorkeeper/callbackuri")

                    self.assertFalse(patched_send.called)
