# coding=utf-8

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.params import GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM, URI_PARAM
from tcell_agent.appsensor.rules import AppSensorRuleManager
from tcell_agent.appsensor.sensors.xss_sensor import XssSensor
from tcell_agent.appsensor.sensors.injection_sensor import InjectionSensor


class XssSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = XssSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_enabled_sensor_test(self):
        sensor = XssSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_headers_sensor_test(self):
        sensor = XssSensor({"exclude_headers": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, True)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_forms_sensor_test(self):
        sensor = XssSensor({"exclude_forms": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, True)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_cookies_sensor_test(self):
        sensor = XssSensor({"exclude_cookies": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, True)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_libinjection_sensor_test(self):
        sensor = XssSensor({"libinjection": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, True)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_active_pattern_ids_sensor_test(self):
        sensor = XssSensor({"patterns": ["1", "2", "3"]})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set(["1", "2", "3"]))
        self.assertEqual(sensor.exclusions, {})

    def create_exclusions_sensor_test(self):
        sensor = XssSensor({"exclusions": {"word": ["form", "header"]}})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "xss")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {"word": set(["form", "header"])})

    def does_not_override_get_ruleset_test(self):
        with patch.object(AppSensorRuleManager, "get_ruleset_for", return_value=None) as patched_get_ruleset_for:
            sensor = XssSensor()
            sensor.get_ruleset()
            patched_get_ruleset_for.assert_called_once_with("xss")

    def param_has_no_vuln_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "param_name",
            "param_value"
        )

        self.assertFalse(result)

    def param_has_no_vuln_no_excluded_routes_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_routes": []})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "param_name",
            "param_value"
        )

        self.assertFalse(result)

    def param_has_no_vuln_excluded_routes_matches_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_routes": ["23947"]})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "param_name",
            "param_value"
        )

        self.assertFalse(result)

    def param_has_no_vuln_excluded_routes_does_not_match_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_routes": ["9875"]})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "param_name",
            "param_value"
        )

        self.assertFalse(result)

    def uri_param_has_vuln_exclude_forms_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_forms": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            URI_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertFalse(result)

    def uri_param_has_vuln_exclude_cookies_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_cookies": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            URI_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertEqual(result.type_of_param, URI_PARAM)
        self.assertEqual(result.param_name, "dirty")
        self.assertEqual(result.param_value, "<script>alert()</script>")
        self.assertEqual(result.pattern, "1")
        self.assertEqual(result.detection_point, sensor.dp)

    def get_param_has_vuln_exclude_forms_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_forms": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertFalse(result)

    def get_param_has_vuln_exclude_cookies_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_cookies": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertEqual(result.type_of_param, GET_PARAM)
        self.assertEqual(result.param_name, "dirty")
        self.assertEqual(result.param_value, "<script>alert()</script>")
        self.assertEqual(result.pattern, "1")
        self.assertEqual(result.detection_point, sensor.dp)

    def get_param_has_vuln_exclude_cookies_exclude_route_id_matches_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_cookies": True, "patterns": ["1"], "exclude_routes": ["23947"]})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertFalse(result)

    def get_param_has_vuln_exclude_cookies_exclude_route_id_does_not_match_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_cookies": True, "patterns": ["1"], "exclude_routes": ["3333"]})
        result = sensor.get_injection_attempt(
            GET_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertEqual(result.type_of_param, GET_PARAM)
        self.assertEqual(result.param_name, "dirty")
        self.assertEqual(result.param_value, "<script>alert()</script>")
        self.assertEqual(result.pattern, "1")
        self.assertEqual(result.detection_point, sensor.dp)

    def post_param_has_vuln_exclude_forms_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_forms": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            POST_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertFalse(result)

    def post_param_has_vuln_exclude_cookies_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_cookies": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            POST_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertEqual(result.type_of_param, POST_PARAM)
        self.assertEqual(result.param_name, "dirty")
        self.assertEqual(result.param_value, "<script>alert()</script>")
        self.assertEqual(result.pattern, "1")
        self.assertEqual(result.detection_point, sensor.dp)

    def json_param_has_vuln_exclude_forms_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_forms": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            JSON_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertFalse(result)

    def json_param_has_vuln_exclude_cookies_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_cookies": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            JSON_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertEqual(result.type_of_param, JSON_PARAM)
        self.assertEqual(result.param_name, "dirty")
        self.assertEqual(result.param_value, "<script>alert()</script>")
        self.assertEqual(result.pattern, "1")
        self.assertEqual(result.detection_point, sensor.dp)

    def cookie_param_has_vuln_exclude_forms_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_forms": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            COOKIE_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertEqual(result.type_of_param, COOKIE_PARAM)
        self.assertEqual(result.param_name, "dirty")
        self.assertEqual(result.param_value, "<script>alert()</script>")
        self.assertEqual(result.pattern, "1")
        self.assertEqual(result.detection_point, sensor.dp)

    def cookie_param_has_vuln_exclude_cookies_get_injection_attempt_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensor = XssSensor({"enabled": True, "exclude_cookies": True, "patterns": ["1"]})
        result = sensor.get_injection_attempt(
            COOKIE_PARAM,
            appsensor_meta,
            "dirty",
            "<script>alert()</script>"
        )

        self.assertFalse(result)

    def applicable_for_param_type_test(self):
        sensor = XssSensor({"enabled": True})
        self.assertTrue(sensor.applicable_for_param_type(GET_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(POST_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(JSON_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(COOKIE_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(URI_PARAM))

    def with_enabled_libinjection_sensor_and_vuln_params_check_test(self):
        sensor = XssSensor({"enabled": True, "patterns": ["1"], "libinjection": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(InjectionSensor, "find_vulnerability") as patched_find_vulnerability:
            result = sensor.find_vulnerability("dirty", "<script></script>")
            self.assertFalse(patched_find_vulnerability.called)
            self.assertEqual(result, {"param": "dirty", "pattern": "li", "value": "<script></script>"})

    def with_enabled_libinjection_sensor_and_vuln_utf8_params_check_test(self):
        sensor = XssSensor({"enabled": True, "patterns": ["1"], "libinjection": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(InjectionSensor, "find_vulnerability") as patched_find_vulnerability:
            result = sensor.find_vulnerability("dirty", "<script>Müller</script>")
            self.assertFalse(patched_find_vulnerability.called)
            self.assertEqual(result, {"param": "dirty", "pattern": "li", "value": "<script>Müller</script>"})

    def with_enabled_libinjection_nonmatching_params_sensor_and_vuln_params_check_test(self):
        sensor = XssSensor({"enabled": True, "patterns": ["1"], "libinjection": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(InjectionSensor, "find_vulnerability", return_value=None) as patched_find_vulnerability:
            result = sensor.get_injection_attempt("get", appsensor_meta, "dirty", "missed by libinjection")
            self.assertFalse(result)
            patched_find_vulnerability.assert_called_once_with(sensor, "dirty", "missed by libinjection")
