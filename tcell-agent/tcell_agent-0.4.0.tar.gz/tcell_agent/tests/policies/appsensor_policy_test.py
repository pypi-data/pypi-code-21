import json
import unittest

from collections import namedtuple
from mock import Mock, call, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.django import set_request
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor_policy import AppSensorPolicy


FakeRequest = namedtuple("FakeRequest", ["body", "META", "GET", "POST", "FILES", "COOKIES", "environ"], verbose=True)
FakeResponse = namedtuple("FakeResponse", ["content", "status_code"], verbose=True)

policy_v2_req_size = """
{
    "policy_id":"abc-abc-abc",
    "version":2,
    "data": {
        "options": {
            "payloads": {
                "send_payloads": false,
                "log_payloads": false
            }
        },
        "sensors": {
            "req_size": {
                "limit":1024,
                "exclude_routes":["2300"]
            }
        }
    }
}
"""

policy_v2_all_options = """
{
    "policy_id":"abc-abc-abc",
    "version":2,
    "data": {
        "options": {
            "payloads": {
                "send_payloads": true,
                "send_blacklist": {
                    "JSESSIONID": ["cookie"],
                    "ssn": ["*"],
                    "password": ["*"],
                    "xss_param": ["*"]
                },
                "log_payloads": true,
                "log_blacklist": {}
            },
            "uri_options":{
                "collect_full_uri": true
            }
        },
        "sensors": {
            "req_size": {
                "limit":1,
                "exclude_routes":["2300"]
            },
            "resp_size": {
                "limit":1,
                "exclude_routes":["2323"]
            },
            "resp_codes": {
                "series_400_enabled":true,
                "series_500_enabled":true
            },
            "xss": {
                "libinjection":true,
                "patterns":["1","2","8"],
                "exclusions":{
                    "bob":["*"]
                }
            },
            "sqli":{
                "libinjection":true,
                "exclude_headers":true,
                "patterns":["1"]
            },
            "fpt":{
                "patterns":["1","2"],
                "exclude_forms":true,
                "exclude_cookies":true,
                "exclusions":{
                    "somethingcommon":["form"]
                }
            },
            "cmdi":{
                 "patterns":["1","2"]
            },
            "nullbyte":{
                 "patterns":["1","2"]
            },
            "retr":{
                "patterns":["1","2"]
            },
            "ua": {
                "empty_enabled": true
            },
            "errors":{
                "csrf_exception_enabled": true,
                "sql_exception_enabled": true
            },
            "database":{
                "large_result": {
                    "limit": 10
                }
            }
        }
    }
}
"""


class AppSensorPolicyTest(unittest.TestCase):

    def classname_test(self):
        self.assertEqual(AppSensorPolicy.api_identifier, "appsensor")

    def read_appensor_v2_req_size_policy_test(self):
        policy_json = json.loads(policy_v2_req_size)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        self.assertTrue(policy.appfirewall_enabled)
        self.assertIsNotNone(policy.appfirewall_ptr)

    def read_appensor_v2_all_options_policy_test(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()

        policy.load_from_json(policy_json)

        self.assertTrue(policy.appfirewall_enabled)
        self.assertIsNotNone(policy.appfirewall_ptr)

    def test_response_codes(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        expected_dps = {
            400: "s4xx",
            401: "s401",
            402: "s4xx",
            403: "s403",
            404: "s404",
            405: "s4xx",
            500: "s500",
            501: "s5xx",
            502: "s5xx"
        }

        for status_code in [400, 401, 402, 403, 404, 405, 500, 501, 502]:
            appsensor_meta.request_processed = False
            appsensor_meta.response_processed = False

            request = FakeRequest("", {"CONTENT_LENGTH": 0, "HTTP_USER_AGENT": "Mozilla"}, {}, {}, {}, {}, {})
            response = FakeResponse(
                "",
                status_code)
            set_request(appsensor_meta, request)
            appsensor_meta.set_response(type(response), response)

            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                policy.process_appsensor_meta(appsensor_meta)

                patched_send.assert_has_calls(
                    [
                        call({
                            "event_type": "as",
                            "m": "request_method",
                            "uri": "abosolute_uri",
                            "sid": "session_id",
                            "full_uri": "abosolute_uri",
                            "meta": {"code": status_code},
                            "rid": "route_id",
                            "dp": expected_dps[status_code],
                            "uid": "user_id"
                        })
                    ]
                )

    def test_request_and_response_sizes(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        request = FakeRequest("", {"CONTENT_LENGTH": 1025, "HTTP_USER_AGENT": "Mozilla"}, {}, {}, {}, {}, {})
        response = FakeResponse(
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.process_appsensor_meta(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "meta": {"sz": 1025},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "reqsz",
                        "uid": "user_id"
                    }),
                    call({
                        "event_type": "as",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "meta": {"sz": 1035},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "rspsz",
                        "uid": "user_id"
                    })
                ]
            )

    def test_xss_event(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.location = "http://192.168.1.1/some/path?xss_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        request = FakeRequest("", {"CONTENT_LENGTH": 16, "HTTP_USER_AGENT": "Mozilla"}, {"xss_param": "<script>"}, {}, {}, {}, {})
        response = FakeResponse("some respose", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.process_appsensor_meta(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "pattern": "li",
                        "m": "GET",
                        "uri": "http://192.168.1.1/some/path?xss_param=",
                        "param": "xss_param",
                        "meta": {"l": "query"},
                        "sid": "session_id",
                        "full_uri": "http://192.168.1.1/some/path?xss_param=<script>",
                        "rid": "12345",
                        "dp": "xss",
                        "uid": "user_id"
                    })
                ]
            )

    def test_sqli_event(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "192.168.1.1"
        appsensor_meta.method = "GET"
        appsensor_meta.location = "http://192.168.1.1/some/path?sqli_param=<script>"
        appsensor_meta.route_id = "12345"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "Mozilla"

        request = FakeRequest("", {"CONTENT_LENGTH": 16, "HTTP_USER_AGENT": "Mozilla"}, {"sqli_param": "a\" OR \"5\"= \"5"}, {}, {}, {}, {})
        response = FakeResponse("some respose", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.process_appsensor_meta(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "pattern": "li",
                        "m": "GET",
                        "uri": "http://192.168.1.1/some/path?sqli_param=",
                        "param": "sqli_param",
                        "meta": {"l": "query"},
                        "sid": "session_id",
                        "full_uri": "http://192.168.1.1/some/path?sqli_param=<script>",
                        "rid": "12345",
                        "payload": "a\" OR \"5\"= \"5",
                        "dp": "sqli",
                        "uid": "user_id"
                    })
                ]
            )

    def test_csrf_rejected(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.csrf_rejected(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "payload": "[CSRF token missing or incorrect. No Stacktrace available.]",
                        "dp": "excsrf",
                        "uid": "user_id"
                    })
                ]
            )

    def test_sql_exception_detected_rejected(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        # make this big to ensure payloads are kept at a max of 150
        stack_trace = ["stack", "trace", "stack", "trace", "stack", "trace", "stack", "trace", "stack", "trace", "stack",
            "trace", "stack", "trace", "stack", "trace", "stack", "trace", "trace", "stack", "trace", "stack", "trace",
            "trace", "stack", "trace", "stack", "trace", "stack", "trace", "trace", "stack", "trace", "stack", "trace"]

        self.assertEqual(len(''.join(stack_trace)), 175)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            with patch("traceback.format_tb", return_value=stack_trace) as patched_format_tb:
                tb = Mock()
                policy.sql_exception_detected(appsensor_meta=appsensor_meta, exc_type_name="ProgrammingError", traceback=tb)

                patched_format_tb.assert_called_once_with(tb)

                expected_payload = "tracestacktracestacktracetracestacktracestacktracestacktracetracestack" + \
                    "tracestacktracetracestacktracestacktracestacktracestacktracestacktracestacktrace"
                self.assertEqual(len(expected_payload), 150)
                patched_send.assert_has_calls(
                    [
                        call({
                            "event_type": "as",
                            "remote_addr": "remote_addr",
                            "m": "request_method",
                            "uri": "abosolute_uri",
                            "param": "ProgrammingError",
                            "sid": "session_id",
                            "full_uri": "abosolute_uri",
                            "rid": "route_id",
                            "payload": expected_payload,
                            "dp": "exsql",
                            "uid": "user_id"
                        })
                    ]
                )

    def test_database_rows_rejected(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.load_from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_db_rows(appsensor_meta=appsensor_meta, number_of_records=11)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "meta": {"rows": 11},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "dbmaxrows",
                        "uid": "user_id"
                    })
                ]
            )
