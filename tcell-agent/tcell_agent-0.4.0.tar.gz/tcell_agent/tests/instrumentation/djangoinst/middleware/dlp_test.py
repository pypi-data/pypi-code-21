# -*- coding: utf-8 -*-

from tcell_agent.instrumentation.djangoinst.utils import django15or16
if not django15or16:
    from django.test import TestCase
    from django.http import HttpResponse

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

    from mock import Mock

    from django.middleware.common import CommonMiddleware
    from django.conf import settings
    from django.test.client import RequestFactory

    from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware
    from tcell_agent.instrumentation.djangoinst.middleware.afterauthmiddleware import AfterAuthMiddleware
    from tcell_agent.instrumentation.djangoinst.middleware.body_filter_middleware import BodyFilterMiddleware
    from tcell_agent.instrumentation.djangoinst.middleware.tcell_data_exposure_middleware import TCellDataExposureMiddleware
    from tcell_agent.instrumentation.djangoinst.middleware.tcelllastmiddleware import TCellLastMiddleware

    from tcell_agent.config import CONFIGURATION
    from tcell_agent.agent import TCellAgent

    try:
        settings.configure()
    except:
        pass
    settings.DEFAULT_CHARSET = "utf-8"

    import logging

    class MockLoggingHandler(logging.Handler):
        """Mock logging handler to check for expected logs.

        Messages are available from an instance's ``messages`` dict, in order, indexed by
        a lowercase log level string (e.g., 'debug', 'info', etc.).
        """

        def __init__(self, *args, **kwargs):
            self.messages = {"debug": [], "info": [], "warning": [], "error": [],
                             "critical": []}
            super(MockLoggingHandler, self).__init__(*args, **kwargs)

        def emit(self, record):
            "Store a message from ``record`` in the instance's ``messages`` dict."
            self.acquire()
            try:
                self.messages[record.levelname.lower()].append(record.getMessage())
            finally:
                self.release()

        def reset(self):
            self.acquire()
            try:
                for message_list in self.messages.values():
                    message_list.clear()
            finally:
                self.release()

    class DLPMiddlewareTest(TestCase):
        def setUp(self):
            settings.ALLOWED_HOSTS = ["testserver", "test.tcell.io"]
            settings.ROOT_URLCONF = "tcell_agent.tests.instrumentation.djangoinst.middleware.test_urls"

            self.grm = GlobalRequestMiddleware()
            self.aam = AfterAuthMiddleware()
            self.cm = CommonMiddleware()
            self.bfm = BodyFilterMiddleware()
            self.data_exposure_middleware = TCellDataExposureMiddleware()
            self.tcell_last_middleware = TCellLastMiddleware()

            self.rf = RequestFactory()

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

            self.mock_logger = logging.getLogger("mockery")
            for h in list(self.mock_logger.handlers):
                self.mock_logger.removeHandler(h)
            mock_handler = MockLoggingHandler(level="DEBUG")
            self.mock_logger.addHandler(mock_handler)
            self.mock_logger_messages = mock_handler.messages

        def request_with_session(self,
                                 url="http://test.tcell.io/hello/",
                                 session_key="101012301200123",
                                 post_form_data=None):
            if post_form_data is not None:
                request = self.rf.post(url, post_form_data)
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

        def test_sesssion_id_protect(self):

            request = self.request_with_session()
            policy_json = {
                "dlp": {
                    "policy_id": "nyzd",
                    "data": {
                        "session_id_protections": {"body": ["redact"], "log": ["event"]}
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_json, cache=False)
            self.middleware_before(request)
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            expected = b"<html>\n<head>Title</head><body>hello world: [redact] [redact]</body><html>"
            self.assertEqual(response.content, expected)

        def test_db_protect(self):
            request = self.request_with_session()
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "db_protections": [
                            {"scope": "route",
                             "route_ids": ["abcdefg"],
                             "tables": ["work_infos"],
                             "fields": ["SSN"],
                             "actions": {"body": ["redact"]}},
                            {"id": 6,
                             "tables": ["work_infos"],
                             "fields": ["income"],
                             "actions": {"body": ["redact"], "log": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)
            self.middleware_before(request)
            actions = TCellAgent.get_policy("dlp").get_actions_for_db_field("test", "test", "work_infos", "income")
            for action in actions:
                request._tcell_context.add_response_db_filter("hello", action, "test", "test", "work_infos", "income")
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 \n\nhello 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            expected = b"<html>\n<head>Title</head><body>[redact] world: 101012301200123 \n\n[redact] 101012301200123</body><html>"
            self.assertEqual(response.content, expected)

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], 6)
            self.assertEqual(self.added_events[0]["table"], "work_infos")

        def test_db_protect_by_route(self):
            request = self.request_with_session()
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "db_protections": [
                            {"scope": "route",
                             "route_ids": ["abcdefg"],
                             "tables": ["work_infos"],
                             "fields": ["SSN"],
                             "actions": {"body": ["redact"]}},
                            {"id": 6,
                             "tables": ["work_infos"],
                             "fields": ["income"],
                             "actions": {"body": ["redact"], "log": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)

            self.middleware_before(request, route_id="abcdefg")
            actions = TCellAgent.get_policy("dlp").get_actions_for_db_field("test", "test", "work_infos", "income",
                                                                            route="abcdefg")
            for action in actions:
                request._tcell_context.add_response_db_filter("hello", action, "test", "test", "work_infos", "SSN")
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 \n\nhello 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            expected = b"<html>\n<head>Title</head><body>[redact] world: 101012301200123 \n\n[redact] 101012301200123</body><html>"
            self.assertEqual(response.content, expected)

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], 6)
            self.assertEqual(self.added_events[0]["table"], "work_infos")

        def test_request_protect_by_route(self):
            request = self.request_with_session(url="http://test.tcell.io/hello/?password=hello")
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "request_protections": [
                            {"id": 6,
                             "scope": "route",
                             "route_ids": ["abcdef"],
                             "variable_context": "form",
                             "variables": ["password"],
                             "actions": {"body": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)
            self.middleware_before(request, route_id="abcdef")
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 \n\nhello 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            expected = b"<html>\n<head>Title</head><body>[redact] world: 101012301200123 \n\n[redact] 101012301200123</body><html>"
            self.assertEqual(response.content, expected)

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], 6)

        def test_request_protect_by_route_post(self):
            request = self.request_with_session(
                url="http://test.tcell.io/hello/login",
                post_form_data={"a": "b", "password": "hello world"})
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "request_protections": [
                            {"id": 22,
                             "scope": "route",
                             "route_ids": ["abcdef"],
                             "variable_context": "form",
                             "variables": ["password"],
                             "actions": {"body": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)
            self.middleware_before(request, route_id="abcdef")
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 \n\nhello 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            expected = b"<html>\n<head>Title</head><body>[redact]: 101012301200123 \n\nhello 101012301200123</body><html>"
            self.assertEqual(response.content, expected)

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], 22)

        def test_request_cookie_protect_by_route(self):
            request = self.request_with_session(url="http://test.tcell.io/hello/?password=sammy")
            request.COOKIES["MyCookie"] = "hello"
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "request_protections": [
                            {"id": 6,
                             "scope": "route",
                             "route_ids": ["abcdef"],
                             "variable_context": "cookie",
                             "variables": ["MyCookie"],
                             "actions": {"body": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)

            self.middleware_before(request, route_id="abcdef")
            response = HttpResponse(
                "<html>\n<head>Title</head><body>hello world: 101012301200123 \n\nhello 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            expected = b"<html>\n<head>Title</head><body>[redact] world: 101012301200123 \n\n[redact] 101012301200123</body><html>"
            self.assertEqual(response.content, expected)

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], 6)

        def test_request_header_protect_by_route(self):
            request = self.request_with_session(url="http://test.tcell.io/hello/?password=sammy")
            request.META["HTTP_MY_HEADER"] = "heyathere"
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "request_protections": [
                            {"id": "100",
                             "scope": "route",
                             "route_ids": ["abcdef"],
                             "variable_context": "header",
                             "variables": ["My_Header"],
                             "actions": {"body": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)

            self.middleware_before(request, route_id="abcdef")
            response = HttpResponse(
                "<html>\n<head>Title</head><body>heyathere world: 101012301200123 \n\nheyathere hello 101012301200123</body><html>",
                content_type="application/html")
            self.middleware_after(request, response)

            expected = b"<html>\n<head>Title</head><body>[redact] world: 101012301200123 \n\n[redact] hello 101012301200123</body><html>"
            self.assertEqual(response.content, expected)

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], "100")

        def test_logger_header_protect_by_route(self):
            request = self.request_with_session(url="http://test.tcell.io/hello/?password=sammy")
            request.META["HTTP_MY_HEADER"] = "heyathere"
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "request_protections": [
                            {"id": "100",
                             "scope": "route",
                             "route_ids": ["abcdef"],
                             "variable_context": "header",
                             "variables": ["My_Header"],
                             "actions": {"body": ["redact"], "log": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)
            self.middleware_before(request, route_id="abcdef")

            from tcell_agent.instrumentation.djangoinst.dlp import dlp_instrumentation
            dlp_instrumentation()

            self.mock_logger.warn("Hi heyathere There")

            self.assertEqual(self.mock_logger_messages["warning"][0], "Hi [redact] There")

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], "100")

        def test_logger_header_protect_global(self):
            request = self.request_with_session(url="http://test.tcell.io/hello/?password=sammy")
            request.META["HTTP_MY_HEADER"] = "heyathere"
            policy_db_protection_by_route = {
                "dlp": {
                    "v": 1,
                    "policy_id": "xyz-def",
                    "data": {
                        "request_protections": [
                            {"id": "100",
                             "variable_context": "header",
                             "variables": ["My_Header"],
                             "actions": {"body": ["redact"], "log": ["redact"]}}
                        ]
                    }
                }
            }
            TCellAgent.tCell_agent.process_policies(policy_db_protection_by_route, cache=False)
            self.middleware_before(request, route_id=None)

            from tcell_agent.instrumentation.djangoinst.dlp import dlp_instrumentation
            dlp_instrumentation()

            self.mock_logger.warn("Hi heyathere There")
            self.assertEqual(self.mock_logger_messages["warning"][0], "Hi [redact] There")

            self.assertEqual(len(self.added_events), 1)
            self.assertEqual(self.added_events[0]["event_type"], "dlp")
            self.assertEqual(self.added_events[0]["rule"], "100")
