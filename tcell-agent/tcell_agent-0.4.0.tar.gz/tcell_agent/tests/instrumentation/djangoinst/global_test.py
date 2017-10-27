# -*- coding: utf-8 -*-

from mock import Mock

from django.test import TestCase
from django.http import HttpResponse
from django.test.client import RequestFactory


from django.middleware.common import CommonMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.afterauthmiddleware import AfterAuthMiddleware
from tcell_agent.config import CONFIGURATION
from tcell_agent.agent import TCellAgent

try:
    import django
    from django.conf import settings

    settings.configure()
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "mydatabase"
            }
        }
    django.setup()
except RuntimeError:
    print("Django already setup")

try:
    settings.configure()
except:
    pass

settings.DEFAULT_CHARSET = "utf-8"


class GlobalRequestMiddlewareTest(TestCase):
    def setUp(self):
        settings.ALLOWED_HOSTS = ["testserver", "test.tcell.io"]

        self.grm = GlobalRequestMiddleware()
        self.aam = AfterAuthMiddleware()
        self.cm = CommonMiddleware()

        rf = RequestFactory()
        self.request = rf.get("http://test.tcell.io/hello/")

        self.request.session = Mock()
        self.request.session.session_key = "101012301200123"

        CONFIGURATION.version = 1
        CONFIGURATION.reverse_proxy = True
        CONFIGURATION.api_key = "Test_-ApiKey=="
        CONFIGURATION.app_id = "TestAppId-AppId"
        CONFIGURATION.host_identifier = "TestHostIdentifier"
        CONFIGURATION.uuid = "test-uuid-test-uuid"
        CONFIGURATION.fetch_policies_from_tcell = False

    def test_session_id_is_added(self):
        self.assertEqual(self.grm.process_request(self.request), None)
        self.assertEqual(self.aam.process_request(self.request), None)
        self.assertEqual(self.request._tcell_context.raw_session_id, "101012301200123")

    def test_remote_addr_is_added(self):
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_addr, "1.1.2.2")

    def test_reverse_proxy_is_added_single(self):
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_FORWARDED_FOR"] = "2.3.3.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_addr, "2.3.3.2")

    def test_reverse_proxy_is_added_multiple(self):
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_FORWARDED_FOR"] = "2.2.2.2 ,3.3.3.3,4.4.4.4"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_addr, "2.2.2.2")

    def test_reverse_proxy_is_igored(self):
        CONFIGURATION.reverse_proxy = False
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_FORWARDED_FOR"] = "2.2.2.2,3.3.3.3,4.4.4.4"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_addr, "1.1.2.2")

    def test_reverse_proxy_with_custom_header_name(self):
        CONFIGURATION.reverse_proxy = True
        CONFIGURATION.reverse_proxy_ip_address_header = "X-ReaL-IP"
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_REAL_IP"] = "2.2.2.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_addr, "2.2.2.2")

    def test_reverse_proxy_with_custom_header_name_is_igored(self):
        CONFIGURATION.reverse_proxy = False
        CONFIGURATION.reverse_proxy_ip_address_header = "X-ReaL-IP"
        self.request.META["REMOTE_ADDR"] = "1.1.2.2"
        self.request.META["HTTP_X_REAL_IP"] = "2.2.2.2"
        self.grm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.remote_addr, "1.1.2.2")

    def test_redirect_normal(self):
        def addEvent(_, event):
            event.post_process()

        TCellAgent.addEvent = addEvent
        TCellAgent.tCell_agent = TCellAgent()

        policy_json = {
            "http-redirect": {
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["whitelisted"],
                    "block": False
                }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.raw_session_id, "101012301200123")
        response = HttpResponse("hello world", content_type="application/html")
        response["Location"] = "http://www.yahoo.com/sam/5?x=asfasdfdsa"
        self.request._tcell_context.route_id = -231123123
        self.cm.process_response(self.request, response)
        self.grm.process_response(self.request, response)

        self.assertEqual(response["location"], "http://www.yahoo.com/sam/5?x=asfasdfdsa")

    def test_redirect_blocked(self):
        def addEvent(_, event):
            event.post_process()

        TCellAgent.addEvent = addEvent
        TCellAgent.tCell_agent = TCellAgent()

        policy_json = {
            "http-redirect": {
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["*.google.com", "*yahoo"],
                    "block": True
                }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.raw_session_id, "101012301200123")
        response = HttpResponse("hello world", content_type="application/html")
        response["Location"] = "http://www.yahoo.com/sam/5?x=asfasdfdsa"
        self.request._tcell_context.route_id = -231123123

        self.cm.process_response(self.request, response)
        self.grm.process_response(self.request, response)

        self.assertEqual(response["location"], "/")

    def test_redirect_blocked_but_whitelisted(self):
        def addEvent(_, event):
            event.post_process()

        TCellAgent.addEvent = addEvent
        TCellAgent.tCell_agent = TCellAgent()

        policy_json = {
            "http-redirect": {
                "policy_id": "nyzd",
                "data": {
                    "enabled": True,
                    "whitelist": ["*.google.com", "*.yahoo.com"],
                    "block": True
                }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cm.process_request(self.request)
        self.assertEqual(self.request._tcell_context.raw_session_id, "101012301200123")
        response = HttpResponse("hello world", content_type="application/html")
        response["Location"] = "http://www.yahoo.com/sam/5?x=asfasdfdsa"
        self.request._tcell_context.route_id = -231123123

        self.cm.process_response(self.request, response)
        self.grm.process_response(self.request, response)

        self.assertEqual(response["location"], "http://www.yahoo.com/sam/5?x=asfasdfdsa")
