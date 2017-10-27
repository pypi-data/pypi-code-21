import unittest

from mock import call, patch

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.sensors.database_sensor import DatabaseSensor


class DatabaseSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = DatabaseSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.max_rows, 1001)
        self.assertEqual(sensor.excluded_route_ids, set())
        self.assertFalse(sensor.collect_full_uri)

    def create_enabled_sensor_test(self):
        sensor = DatabaseSensor(collect_full_uri=False, sensors_json={"database": {}})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.max_rows, 1001)
        self.assertEqual(sensor.excluded_route_ids, set())
        self.assertFalse(sensor.collect_full_uri)

    def create_sensor_with_max_rows_test(self):
        sensors_json = {
            "database": {
                "large_result": {"limit": 1024}
            }
        }
        sensor = DatabaseSensor(collect_full_uri=False, sensors_json=sensors_json)
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.max_rows, 1024)
        self.assertEqual(sensor.excluded_route_ids, set())
        self.assertFalse(sensor.collect_full_uri)

    def create_sensor_with_exclude_routes_test(self):
        sensors_json = {
            "database": {
                "exclude_routes": ["1", "10", "20"]
            }
        }
        sensor = DatabaseSensor(collect_full_uri=False, sensors_json=sensors_json)
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.max_rows, 1001)
        self.assertEqual(sensor.excluded_route_ids, set(["1", "10", "20"]))

    def with_disabled_sensor_should_check_test(self):
        sensor = DatabaseSensor()
        self.assertFalse(sensor.should_check(None))

    def with_enabled_sensor_and_excluded_routes_will_check_test(self):
        sensors_json = {
            "database": {
                "exclude_routes": ["1", "10", "20"]
            }
        }
        sensor = DatabaseSensor(collect_full_uri=False, sensors_json=sensors_json)
        self.assertFalse(sensor.should_check("1"))
        self.assertTrue(sensor.should_check(None))

    def with_disabled_sensor_check_test(self):
        sensor = DatabaseSensor(collect_full_uri=False)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            sensor.check(appsensor_meta, 3072)
            self.assertFalse(patched_send.called)

    def with_enabled_sensor_and_number_of_records_is_too_big_but_route_id_is_excluded_check_test(self):
        sensors_json = {
            "database": {
                "large_result": {"limit": 1024},
                "exclude_routes": ["23947"]
            }
        }
        sensor = DatabaseSensor(collect_full_uri=False, sensors_json=sensors_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            sensor.check(appsensor_meta, 2048)
            self.assertFalse(patched_send.called)

    def with_enabled_sensor_and_number_of_records_is_ok_check_test(self):
        sensors_json = {
            "database": {
                "large_result": {"limit": 1024}
            }
        }
        sensor = DatabaseSensor(collect_full_uri=False, sensors_json=sensors_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            sensor.check(appsensor_meta, 10)
            self.assertFalse(patched_send.called)

    def with_enabled_sensor_and_number_of_records_is_too_big_check_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        sensors_json = {
            "database": {
                "large_result": {"limit": 1024}
            }
        }
        sensor = DatabaseSensor(collect_full_uri=True, sensors_json=sensors_json)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            sensor.check(appsensor_meta, 3072)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "meta": {"rows": 3072},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "dbmaxrows",
                        "uid": "user_id"
                    })
                ]
            )
