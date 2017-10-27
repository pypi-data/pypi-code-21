# -*- coding: utf-8 -*-

from future.backports.urllib.parse import parse_qs

from mock import Mock

try:
    import django # noqa
    from django.conf import settings

    settings.configure()
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "mydatabase",
        }
    }
    settings.ROOT_URLCONF = "tcell_agent.tests.instrumentation.djangoinst.middleware.test_urls"
    from tcell_agent.instrumentation.djangoinst.utils import django15or16
    if not django15or16:
        django.setup()
except RuntimeError:
    print("Django already setup")


try:
    settings.configure()
except:
    pass

from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpResponse
from django.middleware.common import CommonMiddleware

from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.afterauthmiddleware import AfterAuthMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.body_filter_middleware import BodyFilterMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.tcell_data_exposure_middleware import TCellDataExposureMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.tcelllastmiddleware import TCellLastMiddleware
from tcell_agent.config import CONFIGURATION
from tcell_agent.agent import TCellAgent

settings.DEFAULT_CHARSET = "utf-8"

policy_sample = {
    "appsensor": {
        "policy_id": "nyzd",
        "version": 2,
        "data": {
            "options": {
                "payloads": {
                    "send_payloads": True,
                    "log_payloads": False
                }
            },
            "sensors": {}
        }
    }
}


class AppSensorMiddlewareTest(TestCase):
    def setUp(self):
        settings.ALLOWED_HOSTS = ["testserver", "test.tcell.io"]

        self.grm = GlobalRequestMiddleware()
        self.aam = AfterAuthMiddleware()
        self.cm = CommonMiddleware()
        self.bfm = BodyFilterMiddleware()
        self.data_exposure_middleware = TCellDataExposureMiddleware()
        self.tcell_last_middleware = TCellLastMiddleware()

        self.rf = RequestFactory(HTTP_USER_AGENT="Mozilla/5.0")

        CONFIGURATION.version = 1
        CONFIGURATION.api_key = "Test_-ApiKey=="
        CONFIGURATION.app_id = "TestAppId-AppId"
        CONFIGURATION.host_identifier = "TestHostIdentifier"
        CONFIGURATION.uuid = "test-uuid-test-uuid"
        CONFIGURATION.fetch_policies_from_tcell = False

        added_events = []
        self.added_events = added_events

        def addEvent(_, event):
            event.post_process()
            added_events.append(event)

        self.old_add_events = TCellAgent.addEvent
        TCellAgent.addEvent = addEvent

        self.old_tcell_agent = TCellAgent.tCell_agent
        TCellAgent.tCell_agent = TCellAgent()
        TCellAgent.tCell_agent.policies = {}

    def request_with_session(self,
                             url="http://test.tcell.io/hello/",
                             session_key="101012301200123",
                             content_type=None,
                             post_form_data=None):
        if post_form_data is not None:
            if content_type is not None:
                request = self.rf.post(url, content_type=content_type, data=post_form_data)
            else:
                request = self.rf.post(url, data=post_form_data)
        else:
            request = self.rf.get(url)
        request.session = Mock()
        request.session.session_key = session_key
        return request

    def middleware_before(self, request, route_id="mock_request_id"):
        self.grm.process_request(request)
        request._tcell_context.route_id = route_id
        self.data_exposure_middleware.process_request(request)
        self.aam.process_request(request)
        self.cm.process_request(request)
        self.tcell_last_middleware.process_request(request)

    def middleware_after(self, request, response):
        self.tcell_last_middleware.process_response(request, response)
        self.bfm.process_response(request, response)
        self.cm.process_response(request, response)
        self.grm.process_response(request, response)

    def test_appsensor_xss(self):
        request = self.request_with_session(url="http://test.tcell.io/hello/?someparam=<SCRIPT>alert(1)</SCRIPT>")
        request.META["SERVER_NAME"] = "test.tcell.io"
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "sqli": {"patterns": ["1", "2", "3", "4", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 1)
        appsensor_event = self.added_events[0]

        self.assertEqual(appsensor_event["dp"], "xss")
        self.assertEqual(appsensor_event["meta"], {"l": "query"})
        self.assertEqual(appsensor_event["param"], "someparam")
        self.assertEqual(appsensor_event["m"], "GET")
        self.assertEqual(appsensor_event["uri"], "http://test.tcell.io/hello/?someparam=")
        self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")

    def test_appsensor_sqli_and_xss(self):
        request = self.request_with_session(
            url="http://test.tcell.io/hello/?someparam=<script>alert(1)</script>&def=%30\"%20OR%20\"2\"=\"2")
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "sqli": {"patterns": ["1", "2", "3", "4", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)
        old_allow = CONFIGURATION.allow_payloads
        CONFIGURATION.allow_payloads = False
        try:
            self.middleware_before(request)
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            self.assertEqual(len(self.added_events), 2)
            sorted_events = sorted(self.added_events, key=lambda item: item["dp"])
            appsensor_event = sorted_events[1]

            self.assertEqual(appsensor_event["dp"], "xss")
            self.assertEqual(appsensor_event["meta"], {"l": "query"})
            self.assertEqual(appsensor_event["param"], "someparam")
            self.assertEqual(appsensor_event["m"], "GET")
            self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")
            self.assertEqual(appsensor_event.get("payload"), None)
            self.assertEqual(("payload" in appsensor_event), False)

            appsensor_event = sorted_events[0]

            self.assertEqual(appsensor_event["dp"], "sqli")
            self.assertEqual(appsensor_event["param"], "def")
            self.assertEqual(appsensor_event["m"], "GET")
            self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")
            self.assertEqual(appsensor_event.get("payload"), None)
            self.assertEqual(("payload" in appsensor_event), False)
        finally:
            CONFIGURATION.allow_payloads = old_allow

    def test_appsensor_post(self):
        request = self.request_with_session(
            url="http://test.tcell.io/hello/",
            post_form_data={"name": "fred", "passwd": "secret<SCRIPT>prompt(\"xss\")</SCRIPT>"})
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "sqli": {"patterns": ["1", "2", "3", "4", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 1)
        appsensor_event = self.added_events[0]

        self.assertEqual(appsensor_event["dp"], "xss")
        self.assertEqual(appsensor_event["meta"], {"l": "body"})
        self.assertEqual(appsensor_event["param"], "passwd")
        self.assertEqual(appsensor_event["m"], "POST")
        self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")

    def test_appsensor_json_xss(self):
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        body = """{"a":[{"b":"<script>alert(1)</script>"}]}"""
        request = self.request_with_session(post_form_data=body, content_type="application/json")
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 1)
        appsensor_event = self.added_events[0]

        self.assertEqual(appsensor_event["dp"], "xss")
        self.assertEqual(appsensor_event["meta"], {"l": "body"})
        self.assertEqual(appsensor_event["param"], "b")
        self.assertEqual(appsensor_event["m"], "POST")
        self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")

    def test_appsensor_json_xss_type_form(self):
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }

        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        body = """{"a=":[{"b":"<script>alert(1)</script>"}]}"""
        request = self.request_with_session(post_form_data=body, content_type="application/x-www-form-urlencoded")
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 1)
        appsensor_event = self.added_events[0]

        self.assertEqual(appsensor_event["dp"], "xss")
        self.assertEqual(appsensor_event["meta"], {"l": "body"})
        self.assertEqual(appsensor_event["param"], "b")
        self.assertEqual(appsensor_event["m"], "POST")
        self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")

    def test_appsensor_invalid_json_xss_type_form(self):
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }

        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        body = """{"a="[{"b":"<script>alert(1)</script>"}]}"""
        request = self.request_with_session(post_form_data=body, content_type="application/x-www-form-urlencoded")
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 1)
        appsensor_event = self.added_events[0]

        self.assertEqual(appsensor_event["dp"], "xss")
        self.assertEqual(appsensor_event["meta"], {"l": "body"})
        self.assertEqual(appsensor_event["param"], "{\"a")
        self.assertEqual(appsensor_event["m"], "POST")
        self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")

    def test_appsensor_json_clean(self):
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }

        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        body = """{"a":[{"b":"this is not an xss script"}]}"""
        request = self.request_with_session(post_form_data=body, content_type="application/json")
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 0)

    def test_appsensor_request_size(self):
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "req_size": {"limit": 1024},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }

        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        request = self.request_with_session(url="http://test.tcell.io/hello/", post_form_data={"A": "B"})
        request.META["CONTENT_LENGTH"] = str(524288 * 1025)
        request.META["SERVER_NAME"] = "test.tcell.io"
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 1)
        appsensor_event = self.added_events[0]
        self.assertEqual(appsensor_event["dp"], "reqsz")
        self.assertEqual(appsensor_event["uri"], "http://test.tcell.io/hello/")
        self.assertEqual(appsensor_event["meta"]["sz"], 524288 * 1025)

    def test_appsensor_request_size_small(self):
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "req_size": {"limit": 1024},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }

        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        request = self.request_with_session(post_form_data={"A": "B"})
        request.META["CONTENT_LENGTH"] = (1024 * 512) - 1
        self.middleware_before(request)
        response = HttpResponse(
            "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
            content_type="application/html")
        self.middleware_after(request, response)

        self.assertEqual(len(self.added_events), 0)

    def test_appsensor_payloads(self):
        request = self.request_with_session(
            url="http://test.tcell.io/hello/abc?someparam=<script>alert(1)</script>&def=%30\"%20OR%20\"2\"=\"2")
        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "sqli": {"patterns": ["1", "2", "3", "4", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }

        old_allow = CONFIGURATION.allow_payloads
        CONFIGURATION.allow_payloads = True
        try:
            TCellAgent.tCell_agent.process_policies(policy_json, cache=False)
            self.middleware_before(request)
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)
            self.assertEqual(len(self.added_events), 2)
            sorted_events = sorted(self.added_events, key=lambda item: item["dp"])
            appsensor_event = sorted_events[1]

            self.assertEqual(appsensor_event["dp"], "xss")
            self.assertEqual(appsensor_event["meta"], {"l": "query"})
            self.assertEqual(appsensor_event["param"], "someparam")
            self.assertEqual(appsensor_event["m"], "GET")
            self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")

            self.assertEqual(appsensor_event["payload"], "<script>alert(1)</script>")

            query_params = parse_qs("query_string")
            self.assertEqual(len(query_params), 0)

            appsensor_event = sorted_events[0]

            self.assertEqual(appsensor_event["dp"], "sqli")
            self.assertEqual(appsensor_event["param"], "def")
            self.assertEqual(appsensor_event["m"], "GET")
            self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")
            self.assertEqual(appsensor_event["payload"], "0\" OR \"2\"=\"2")
        finally:
            CONFIGURATION.allow_payloads = old_allow

    def test_appsensor_payloads_default_blacklist(self):
        request = self.request_with_session(
            url="http://test.tcell.io/hello/abc?password=<script>alert(1)</script>&def=%30\"%20OR%20\"2\"=\"2")

        policy_json = policy_sample.copy()
        policy_json["appsensor"]["data"]["sensors"] = {
            "xss": {"patterns": ["1", "2", "4", "5", "6", "7", "8"]},
            "sqli": {"patterns": ["1", "2", "3", "4", "7", "8"]},
            "cmdi": {"patterns": ["1", "2", "3"]},
        }

        old_allow = CONFIGURATION.allow_payloads
        CONFIGURATION.allow_payloads = True
        try:
            TCellAgent.tCell_agent.process_policies(policy_json, cache=False)
            self.middleware_before(request)
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            self.assertEqual(len(self.added_events), 2)
            sorted_events = sorted(self.added_events, key=lambda item: item["dp"])
            appsensor_event = sorted_events[1]

            self.assertEqual(appsensor_event["dp"], "xss")
            self.assertEqual(appsensor_event["meta"], {"l": "query"})
            self.assertEqual(appsensor_event["param"], "password")
            self.assertEqual(appsensor_event["m"], "GET")
            self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")
            self.assertEqual(appsensor_event["payload"], "<script>alert(1)</script>")

            query_params = parse_qs("query_string")
            self.assertEqual(len(query_params), 0)

            appsensor_event = sorted_events[0]

            self.assertEqual(appsensor_event["dp"], "sqli")
            self.assertEqual(appsensor_event["param"], "def")
            self.assertEqual(appsensor_event["m"], "GET")
            self.assertEqual(appsensor_event["remote_addr"], "127.0.0.1")
            self.assertEqual(appsensor_event["payload"], "0\" OR \"2\"=\"2")
        finally:
            CONFIGURATION.allow_payloads = old_allow
