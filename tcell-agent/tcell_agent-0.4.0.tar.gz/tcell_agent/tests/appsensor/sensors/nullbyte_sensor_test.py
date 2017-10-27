import unittest

from mock import patch

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.params import GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM, URI_PARAM
from tcell_agent.appsensor.rules import AppSensorRuleManager
from tcell_agent.appsensor.sensors.nullbyte_sensor import NullbyteSensor


class NullbyteSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = NullbyteSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "null")
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def with_disabled_sensor_check_test(self):
        sensor = NullbyteSensor({"enabled": False, "patterns": ["1"]})
        appsensor_meta = AppSensorMeta()

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, "dirty", "\0blah\0\0\0")
        self.assertFalse(injection_attempt)

    def with_enabled_sensor_and_no_vuln_params_check_test(self):
        sensor = NullbyteSensor({"enabled": True, "patterns": ["1"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, None, None)
        self.assertFalse(injection_attempt)

    def with_enabled_sensor_and_vuln_params_check_test(self):
        sensor = NullbyteSensor({"enabled": True, "patterns": ["1"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, "dirty", "\0blah\0\0\0")
        self.assertEqual(injection_attempt.type_of_param, GET_PARAM)
        self.assertEqual(injection_attempt.param_name, "dirty")
        self.assertEqual(injection_attempt.param_value, "\0blah\0\0\0")
        self.assertEqual(injection_attempt.pattern, "1")
        self.assertEqual(injection_attempt.detection_point, sensor.dp)

    def override_get_ruleset_test(self):
        with patch.object(AppSensorRuleManager, "get_ruleset_for", return_value=None) as patched_get_ruleset_for:
            sensor = NullbyteSensor()
            sensor.get_ruleset()
            patched_get_ruleset_for.assert_called_once_with("nullbyte")

    def applicable_for_param_type_test(self):
        sensor = NullbyteSensor({"enabled": True})
        self.assertTrue(sensor.applicable_for_param_type(GET_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(POST_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(JSON_PARAM))
        self.assertFalse(sensor.applicable_for_param_type(COOKIE_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(URI_PARAM))
