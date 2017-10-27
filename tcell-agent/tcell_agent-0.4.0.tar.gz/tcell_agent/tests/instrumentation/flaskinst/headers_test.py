import unittest

from mock import Mock, patch

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation.flaskinst.headers import add_clickjacking, \
    check_location_redirect, set_csp_headers, add_secure_headers


class RoutesTest(unittest.TestCase):

    def set_csp_headers_test(self):
        request = Mock(_appsensor_meta=AppSensorMeta(), path="/path")
        request._appsensor_meta.route_id = "route_id"
        request._appsensor_meta.session_id = "session_id"
        request._appsensor_meta.user_id = "user_id"
        response = Mock(headers={})
        csp_headers = Mock()
        csp_headers.headers.return_value = [
            ["Content-Security-Policy-Report-Only",
             "img-src \"self\""]]

        with patch.object(TCellAgent, "get_policy", return_value=csp_headers) as patched_get_policy:
            set_csp_headers(request, response, None)

            self.assertTrue(patched_get_policy.called)
            csp_headers.headers.assert_called_once_with(
                None, "route_id", "session_id", "user_id", "/path")

            self.assertEqual(response.headers["Content-Security-Policy-Report-Only"], "img-src \"self\"")

    def add_clickjacking_test(self):
        request = Mock(_appsensor_meta=AppSensorMeta(), path="/path")
        request._appsensor_meta.route_id = "route_id"
        request._appsensor_meta.session_id = "session_id"
        request._appsensor_meta.user_id = "user_id"
        response = Mock(headers={})
        clickjacking_headers = Mock()
        clickjacking_headers.headers.return_value = [
            ["Content-Security-Policy",
             "img-src \"self\""]]

        with patch.object(TCellAgent, "get_policy", return_value=clickjacking_headers) as patched_get_policy:
            add_clickjacking(request, response, None)

            self.assertTrue(patched_get_policy.called)
            clickjacking_headers.headers.assert_called_once_with(
                None, "route_id", "session_id", "user_id", "/path")

            self.assertEqual(response.headers["Content-Security-Policy"], "img-src \"self\"")

    def csp_with_add_clickjacking_test(self):
        request = Mock(_appsensor_meta=AppSensorMeta(), path="/path")
        request._appsensor_meta.route_id = "route_id"
        request._appsensor_meta.session_id = "session_id"
        request._appsensor_meta.user_id = "user_id"
        response = Mock(headers={})
        response.headers["Content-Security-Policy"] = "default-src \"none\""
        clickjacking_headers = Mock()
        clickjacking_headers.headers.return_value = [
            ["Content-Security-Policy",
             "img-src \"self\""]]

        with patch.object(TCellAgent, "get_policy", return_value=clickjacking_headers) as patched_get_policy:
            add_clickjacking(request, response, None)

            self.assertTrue(patched_get_policy.called)
            clickjacking_headers.headers.assert_called_once_with(
                None, "route_id", "session_id", "user_id", "/path")

            self.assertEqual(response.headers["Content-Security-Policy"], "default-src \"none\", img-src \"self\"")

    def add_secure_headers_test(self):
        request = Mock(_appsensor_meta=AppSensorMeta(), path="/path")
        request._appsensor_meta.route_id = "route_id"
        request._appsensor_meta.session_id = "session_id"
        request._appsensor_meta.user_id = "user_id"
        response = Mock(headers={})
        secure_headers = Mock()
        secure_headers.headers.return_value = [
            ["Strict-Transport-Security",
             "some secure value"]]

        with patch.object(TCellAgent, "get_policy", return_value=secure_headers) as patched_get_policy:
            add_secure_headers(response)

            self.assertTrue(patched_get_policy.called)
            secure_headers.headers.assert_called_once_with()

            self.assertEqual(response.headers["Strict-Transport-Security"], "some secure value")

    def check_location_redirect_test(self):
        request = Mock(
            _appsensor_meta=AppSensorMeta(),
            path="/path",
            host="host",

            environ={
                "REMOTE_ADDR": "192.168.1.115",
                "REQUEST_METHOD": "GET"})
        request._appsensor_meta.route_id = "route_id"
        request._appsensor_meta.session_id = "session_id"
        request._appsensor_meta.user_id = "user_id"
        response = Mock(headers={}, location="/redirect", status_code=200)
        redirect_policy = Mock()

        with patch.object(TCellAgent, "get_policy", return_value=redirect_policy) as patched_get_policy:
            check_location_redirect(request, response)

            patched_get_policy.assert_called_once_with(PolicyTypes.HTTP_REDIRECT)
            redirect_policy.process_location.assert_called_once_with(
                "192.168.1.115",
                "GET",
                "host",
                "/path",
                200,
                "/redirect",
                user_id="user_id",
                session_id="session_id",
                route_id="route_id")
