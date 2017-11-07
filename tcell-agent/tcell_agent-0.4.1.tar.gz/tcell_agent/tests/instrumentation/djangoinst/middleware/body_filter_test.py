# -*- coding: utf-8 -*-

try:
    import django
    from django.conf import settings

    settings.configure()
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "mydatabase",
        }
    }
    django.setup()
except RuntimeError:
    print("Django already setup")

from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpResponse
from django.middleware.common import CommonMiddleware
from django.conf import settings

from mock import Mock

from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.afterauthmiddleware import AfterAuthMiddleware
from tcell_agent.instrumentation.djangoinst.middleware.body_filter_middleware import BodyFilterMiddleware
from tcell_agent.config import CONFIGURATION
from tcell_agent.agent import TCellAgent

try:
    settings.configure()
except:
    pass

settings.DEFAULT_CHARSET = "utf-8"


class BodyFilterMiddlewareTest(TestCase):
    _multiprocess_can_split_ = False

    def setUp(self):
        settings.ALLOWED_HOSTS = ["testserver", "test.tcell.io"]

        self.grm = GlobalRequestMiddleware()
        self.aam = AfterAuthMiddleware()
        self.cmw = CommonMiddleware()
        self.bfm = BodyFilterMiddleware()

        request_factory = RequestFactory()
        self.request = request_factory.get("http://test.tcell.io/hello/")

        self.request.session = Mock()
        self.request.session.session_key = "101012301200123"

        CONFIGURATION.version = 1
        CONFIGURATION.api_key = "Test_-ApiKey=="
        CONFIGURATION.app_id = "TestAppId-AppId"
        CONFIGURATION.host_identifier = "TestHostIdentifier"
        CONFIGURATION.uuid = "test-uuid-test-uuid"
        CONFIGURATION.fetch_policies_from_tcell = False

    def test_body_inject(self):

        def add_event(_, event):
            event.post_process()

        TCellAgent.addEvent = add_event
        TCellAgent.tCell_agent = TCellAgent()

        policy_json = {
            "csp-headers": {
                "policy_id": "nyzd",
                "data": {
                    "options": {
                        "js_agent_api_key": "000-000-1-2323"
                    }
                }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cmw.process_request(self.request)
        response = HttpResponse("<html>\n<head>Title</head><body>hello world</body><html>", content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cmw.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"<html>\n<head><script src=\"https://api.tcell.io/tcellagent.min.js\" " + \
            b"tcellappid=\"TestAppId-AppId\" tcellapikey=\"000-000-1-2323\"></script>Title</head><body>hello world</body><html>"
        self.assertEqual(response.content, expected)

    def test_non_html_body_inject(self):

        def add_event(_, event):
            event.post_process()

        TCellAgent.addEvent = add_event
        TCellAgent.tCell_agent = TCellAgent()

        policy_json = {
            "csp-headers": {
                "policy_id": "nyzd",
                "data": {
                    "options": {
                        "js_agent_api_key": "000-000-1-2323"
                    }
                }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cmw.process_request(self.request)
        resp = b"\x08\x01\x10\x01(\xc1\xca\x03JN\n\tajaxtoken\x1282cfc663150b955a7b8aad324f33364d5965f1a7397a545df76dea8bf\x18\x00 \x80\xc4\xff\x0e"
        response = HttpResponse(resp, content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cmw.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"""\x08\x01\x10\x01(\xc1\xca\x03JN\n\tajaxtoken\x1282cfc663150b955a7b8aad324f33364d5965f1a7397a545df76dea8bf\x18\x00 \x80\xc4\xff\x0e"""
        self.assertEqual(response.content, expected)

    def test_utf8_html_body_inject(self):

        def add_event(_, event):
            event.post_process()

        TCellAgent.addEvent = add_event
        TCellAgent.tCell_agent = TCellAgent()

        policy_json = {
            "csp-headers": {
                "policy_id": "nyzd",
                "data": {
                    "options": {
                        "js_agent_api_key": "000-000-1-2323"
                    }
                }
            }
        }
        TCellAgent.tCell_agent.process_policies(policy_json, cache=False)

        self.grm.process_request(self.request)
        self.aam.process_request(self.request)
        self.cmw.process_request(self.request)
        response = HttpResponse(u"<html>\n<head>Müller</head><body>holá mundo</body><html>", content_type="text/html")
        self.bfm.process_response(self.request, response)
        self.cmw.process_response(self.request, response)
        self.grm.process_response(self.request, response)
        expected = b"<html>\n<head><script src=\"https://api.tcell.io/tcellagent.min.js\" " + \
            b"tcellappid=\"TestAppId-AppId\" tcellapikey=\"000-000-1-2323\"></script>M\xc3\xbcller</head><body>hol\xc3\xa1 mundo</body><html>"
        self.assertEqual(response.content, expected)
