import unittest

from mock import Mock, patch

from django.http.response import HttpResponseForbidden

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.djangoinst.middleware.tcelllastmiddleware import check_ip_blocking
from tcell_agent.policies import PatchesPolicy


class CheckIpBlockingTest(unittest.TestCase):
    def none_patches_policy_test(self):
        request = Mock()
        path_dict = {}

        with patch.object(TCellAgent, "get_policy", return_value=None) as patched_get_policy:
            result = check_ip_blocking(request, path_dict)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)
            self.assertIsNone(result)

    def disabled_patches_policy_test(self):
        request = Mock()
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {}
        })

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            result = check_ip_blocking(request, path_dict)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)
            self.assertIsNone(result)

    def wiki_example_one_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.raw_remote_addr = "1.2.3.4"
        tcell_context.route_id = "12345"
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(encoding="utf-8", _tcell_context=tcell_context, FILES={}, META={"REQUEST_METHOD": "GET"}, environ={})
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "block_rules": [
                    {
                        "ips": ["1.2.3.4"]
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
            self.assertTrue(tcell_context.ip_blocking_triggered)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

    def wiki_example_two_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(encoding="utf-8", _tcell_context=tcell_context, FILES={}, META={"REQUEST_METHOD": "GET"}, environ={})
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "block_rules": [
                    {
                        "rids": ["123213", "-3328888"]
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "123213"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
            self.assertTrue(tcell_context.ip_blocking_triggered)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "-3328888"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

    def wiki_example_three_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(
            encoding="utf-8",
            _tcell_context=tcell_context,
            FILES={}, META={"REQUEST_METHOD": "GET"},
            GET={},
            COOKIES={},
            environ={},
        )
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "block_rules": [
                    {
                        "ips": ["1.2.3.4"],
                        "sensor_matches": {
                            "xss": {
                                "libinjection": False,
                                "patterns": ["1", "2", "8"],
                                "exclusions": {
                                    "bob": ["*"]
                                }
                            }
                        }
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "11111"
            path_dict = {"xss_param": "<script>"}
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "11111"
            path_dict = {"sqli_param": "Erwin\" OR \"1\"=\"1"}
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            path_dict = {"xss_param": "<script>"}
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
            self.assertTrue(tcell_context.ip_blocking_triggered)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            path_dict = {"sqli_param": "bob;txt"}
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

    def wiki_example_four_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(
            encoding="utf-8",
            _tcell_context=tcell_context,
            FILES={}, META={"REQUEST_METHOD": "GET"},
            GET={},
            COOKIES={},
            environ={},
        )
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "block_rules": [
                    {
                        "ips": ["1.2.3.4"],
                        "rids": ["123213", "-3328888"]
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "123213"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "-3328888"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "123213"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
            self.assertTrue(tcell_context.ip_blocking_triggered)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "-3328888"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

    def wiki_example_five_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(
            encoding="utf-8",
            _tcell_context=tcell_context,
            FILES={}, META={"REQUEST_METHOD": "GET"},
            GET={},
            COOKIES={},
            environ={},
        )
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "block_rules": [
                    {
                        "ips": ["1.2.3.4"],
                        "sensor_matches": {
                            "xss": {},
                            "sqli": {}
                        }
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            path_dict = {"xss_param": "<script>"}
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            path_dict = {"sqli_param": "bob;txt"}
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

    def wiki_example_six_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(
            encoding="utf-8",
            _tcell_context=tcell_context,
            FILES={}, META={"REQUEST_METHOD": "GET"},
            GET={},
            COOKIES={},
            environ={},
        )
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "block_rules": [
                    {
                        "sensor_matches": {
                            "xss": {},
                            "sqli": {}
                        }
                    }
                ]
            }
        })

        self.assertFalse(policy.enabled)
        self.assertEqual(policy.block_rules, [])
        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

    def wiki_example_seven_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(
            _tcell_context=tcell_context,
            FILES={}, META={"REQUEST_METHOD": "GET"},
            GET={},
            COOKIES={},
            environ={},
        )
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{"ip": "1.1.1.1"}, {"ip": "2.2.2.2"}],
                "block_rules": [
                    {
                        "ips": ["3.3.3.3"],
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
            self.assertTrue(tcell_context.ip_blocking_triggered)

            request._tcell_context.raw_remote_addr = "2.2.2.2"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

            request._tcell_context.raw_remote_addr = "3.3.3.3"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

    def wiki_example_eight_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(
            encoding="utf-8",
            _tcell_context=tcell_context,
            FILES={}, META={"REQUEST_METHOD": "GET"},
            GET={},
            COOKIES={},
            environ={},
        )
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "block_rules": [
                    {
                        "ips": ["1.2.3.4"],
                    },
                    {
                        "rids": ["123213", "-3328888"],
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
            self.assertTrue(tcell_context.ip_blocking_triggered)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "123213"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "-3328888"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "123213"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

            request._tcell_context.raw_remote_addr = "1.2.3.4"
            request._tcell_context.route_id = "-3328888"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)

    def wiki_example_nine_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.session_id = "session_id"
        tcell_context.user_id = "tcelluser"

        request = Mock(
            encoding="utf-8",
            _tcell_context=tcell_context,
            FILES={}, META={"REQUEST_METHOD": "GET"},
            GET={},
            COOKIES={},
            environ={},
        )
        request.build_absolute_uri.return_value = "http://test.tcell.io"
        path_dict = {}

        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{"ip": "1.1.1.1"}, {"ip": "2.2.2.2"}],
                "block_rules": [
                    {
                        "ips": ["1.1.1.1", "2.2.2.2"],
                    }
                ]
            }
        })

        self.assertFalse(tcell_context.ip_blocking_triggered)

        with patch.object(TCellAgent, "get_policy", return_value=policy) as patched_get_policy:
            request._tcell_context.raw_remote_addr = "3.3.3.3"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertIsNone(result)

            patched_get_policy.assert_called_once_with(PolicyTypes.PATCHES)

            request._tcell_context.raw_remote_addr = "1.1.1.1"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
            self.assertTrue(tcell_context.ip_blocking_triggered)

            request._tcell_context.raw_remote_addr = "2.2.2.2"
            request._tcell_context.route_id = "11111"
            result = check_ip_blocking(request, path_dict)
            self.assertEqual(type(result), HttpResponseForbidden)
