# coding=utf-8

import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.params import GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM, URI_PARAM
from tcell_agent.appsensor.sensors.sqli_sensor import SqliSensor
from tcell_agent.appsensor.sensors.injection_sensor import InjectionSensor


class SqliSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = SqliSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_enabled_sensor_test(self):
        sensor = SqliSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_headers_sensor_test(self):
        sensor = SqliSensor({"exclude_headers": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, True)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_forms_sensor_test(self):
        sensor = SqliSensor({"exclude_forms": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, True)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_excluded_cookies_sensor_test(self):
        sensor = SqliSensor({"exclude_cookies": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, True)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_libinjection_sensor_test(self):
        sensor = SqliSensor({"libinjection": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, True)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def create_active_pattern_ids_sensor_test(self):
        sensor = SqliSensor({"patterns": ["1", "2", "3"]})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set(["1", "2", "3"]))
        self.assertEqual(sensor.exclusions, {})

    def create_exclusions_sensor_test(self):
        sensor = SqliSensor({"exclusions": {"word": ["form", "header"]}})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "sqli")
        self.assertEqual(sensor.libinjection, False)
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {"word": set(["form", "header"])})

    def applicable_for_param_type_test(self):
        sensor = SqliSensor({"enabled": True})
        self.assertTrue(sensor.applicable_for_param_type(GET_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(POST_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(JSON_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(COOKIE_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(URI_PARAM))

    def with_disabled_sensor_get_injection_attempt_test(self):
        sensor = SqliSensor({"enabled": False})
        appsensor_meta = AppSensorMeta()

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, "dirty", "Erwin\" OR \"1\"=\"1")
        self.assertFalse(injection_attempt)

    def with_enabled_sensor_and_no_vuln_params_get_injection_attempt_test(self):
        sensor = SqliSensor({"enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, None, None)
        self.assertFalse(injection_attempt)

    def with_enabled_sensor_and_vuln_params_get_injection_attempt_test(self):
        sensor = SqliSensor({"enabled": True, "patterns": ["1"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, "dirty", "Erwin\" OR \"1\"=\"1")
        self.assertEqual(injection_attempt.type_of_param, GET_PARAM)
        self.assertEqual(injection_attempt.param_name, "dirty")
        self.assertEqual(injection_attempt.param_value, "Erwin\" OR \"1\"=\"1")
        self.assertEqual(injection_attempt.pattern, "1")
        self.assertEqual(injection_attempt.detection_point, sensor.dp)

    def with_enabled_libinjection_sensor_and_vuln_params_check_test(self):
        sensor = SqliSensor({"enabled": True, "patterns": ["1"], "libinjection": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(InjectionSensor, "find_vulnerability") as patched_find_vulnerability:
            result = sensor.find_vulnerability("dirty", "Erwin\" OR \"1\"=\"1")
            self.assertFalse(patched_find_vulnerability.called)
            self.assertEqual(result, {"pattern": "li", "value": "Erwin\" OR \"1\"=\"1", "param": "dirty"})

    def with_enabled_libinjection_sensor_and_vuln_utf8_params_check_test(self):
        sensor = SqliSensor({"enabled": True, "patterns": ["1"], "libinjection": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(InjectionSensor, "find_vulnerability") as patched_find_vulnerability:
            result = sensor.find_vulnerability("dirty", "Müller\" OR \"1\"=\"1")
            self.assertFalse(patched_find_vulnerability.called)
            self.assertEqual(result, {"param": "dirty", "pattern": "li", "value": "Müller\" OR \"1\"=\"1"})

    def with_enabled_libinjection_nonmatching_params_sensor_and_vuln_params_check_test(self):
        sensor = SqliSensor({"enabled": True, "patterns": ["1"], "libinjection": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(InjectionSensor, "find_vulnerability", return_value=None) as patched_find_vulnerability:
            result = sensor.find_vulnerability("dirty", "missed by libinjection")
            self.assertFalse(result)
            patched_find_vulnerability.assert_called_once_with(sensor, "dirty", "missed by libinjection")
