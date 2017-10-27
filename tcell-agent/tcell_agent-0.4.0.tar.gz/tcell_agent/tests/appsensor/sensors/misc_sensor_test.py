import unittest

from mock import call, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.sensors.misc_sensor import MiscSensor


class MiscSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = MiscSensor()
        self.assertFalse(sensor.csrf_exception_enabled)
        self.assertFalse(sensor.sql_exception_enabled)

    def create_enabled_sensor_test(self):
        sensors_json = {
            "errors": {
                "csrf_exception_enabled": True,
                "sql_exception_enabled": True
            }
        }
        sensor = MiscSensor(collect_full_uri=False, sensors_json=sensors_json)
        self.assertFalse(sensor.collect_full_uri)
        self.assertTrue(sensor.csrf_exception_enabled)
        self.assertTrue(sensor.sql_exception_enabled)

    def with_disabled_sensor_csrf_rejected_test(self):
        sensors_json = {
            "errors": {
                "csrf_exception_enabled": False
            }
        }
        sensor = MiscSensor(collect_full_uri=False, sensors_json=sensors_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            sensor.csrf_rejected(appsensor_meta)

            self.assertFalse(patched_send.called)

    def with_enabled_sensor_csrf_rejected_test(self):
        sensors_json = {
            "errors": {
                "csrf_exception_enabled": True
            }
        }
        sensor = MiscSensor(collect_full_uri=True, sensors_json=sensors_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            sensor.csrf_rejected(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "23947",
                        "payload": "[CSRF token missing or incorrect. No Stacktrace available.]",
                        "dp": "excsrf",
                        "uid": "user_id"
                    })
                ]
            )
