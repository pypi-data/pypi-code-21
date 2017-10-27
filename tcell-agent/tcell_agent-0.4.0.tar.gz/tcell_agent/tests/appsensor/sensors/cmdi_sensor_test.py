import unittest

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.params import GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM, URI_PARAM
from tcell_agent.appsensor.sensors.cmdi_sensor import CmdiSensor


class CmdiSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = CmdiSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.exclude_headers, False)
        self.assertEqual(sensor.exclude_forms, False)
        self.assertEqual(sensor.exclude_cookies, False)
        self.assertEqual(sensor.dp, "cmdi")
        self.assertEqual(sensor.active_pattern_ids, set())
        self.assertEqual(sensor.exclusions, {})

    def with_disabled_sensor_get_injection_attempt_test(self):
        sensor = CmdiSensor({"enabled": False})
        appsensor_meta = AppSensorMeta()

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, "dirty", "bob.txt;id")
        self.assertFalse(injection_attempt)

    def with_enabled_sensor_and_no_vuln_params_get_injection_attempt_test(self):
        sensor = CmdiSensor({"enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, "param_name", "safe_value")
        self.assertFalse(injection_attempt)

    def with_enabled_sensor_and_vuln_params_get_injection_attempt_test(self):
        sensor = CmdiSensor({"enabled": True, "patterns": ["2"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        injection_attempt = sensor.get_injection_attempt(GET_PARAM, appsensor_meta, "dirty", "bob.txt;id")
        self.assertEqual(injection_attempt.type_of_param, GET_PARAM)
        self.assertEqual(injection_attempt.param_name, "dirty")
        self.assertEqual(injection_attempt.param_value, "bob.txt;id")
        self.assertEqual(injection_attempt.pattern, "2")
        self.assertEqual(injection_attempt.detection_point, sensor.dp)

    def applicable_for_param_type_test(self):
        sensor = CmdiSensor({"enabled": True})
        self.assertTrue(sensor.applicable_for_param_type(GET_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(POST_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(JSON_PARAM))
        self.assertFalse(sensor.applicable_for_param_type(COOKIE_PARAM))
        self.assertTrue(sensor.applicable_for_param_type(URI_PARAM))
