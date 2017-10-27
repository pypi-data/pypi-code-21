from tcell_agent.instrumentation.djangoinst.utils import django15or16
if not django15or16:
    import unittest

    from mock import call, patch, Mock

    from django.db.utils import ProgrammingError, OperationalError

    from tcell_agent.agent import TCellAgent
    from tcell_agent.appsensor.meta import AppSensorMeta  # pylint: disable=ungrouped-imports
    from tcell_agent.appsensor.sensors.misc_sensor import MiscSensor

    class MiscSensorSqlExceptionTest(unittest.TestCase):

        def with_disabled_sensor_sql_exception_test(self):
            sensors_json = {
                "errors": {
                    "sql_exception_enabled": False
                }
            }
            sensor = MiscSensor(collect_full_uri=True, sensors_json=sensors_json)

            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                with patch("traceback.format_tb", return_value=["stack", "trace"]) as patched_format_tb:
                    meta = Mock()
                    exc_type = ProgrammingError
                    tb = Mock()

                    sensor.sql_exception_detected(meta, exc_type.__name__, tb)
                    self.assertFalse(patched_send.called)
                    self.assertFalse(patched_format_tb.called)

        def with_enabled_sensor_sql_exception_test(self):
            sensors_json = {
                "errors": {
                    "sql_exception_enabled": True,
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
                with patch("traceback.format_tb", return_value=["stack", "trace"]) as patched_format_tb:
                    exc_type = ProgrammingError
                    tb = Mock()

                    sensor.sql_exception_detected(appsensor_meta, exc_type.__name__, tb)

                    patched_format_tb.assert_called_once_with(tb)
                    patched_send.assert_has_calls(
                        [
                            call({
                                "event_type": "as",
                                "remote_addr": "remote_addr",
                                "m": "request_method",
                                "uri": "abosolute_uri",
                                "param": "ProgrammingError",
                                "sid": "session_id",
                                "full_uri": "abosolute_uri",
                                "rid": "23947",
                                "payload": "tracestack",
                                "dp": "exsql",
                                "uid": "user_id"
                            })
                        ]
                    )

        def with_enabled_sensor_sql_exception_operational_error_test(self):
            sensors_json = {
                "errors": {
                    "sql_exception_enabled": True,
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
                with patch("traceback.format_tb", return_value=["stack", "trace"]) as patched_format_tb:
                    exc_type = OperationalError
                    tb = Mock()

                    sensor.sql_exception_detected(appsensor_meta, exc_type.__name__, tb)

                    patched_format_tb.assert_called_once_with(tb)
                    patched_send.assert_has_calls(
                        [
                            call({
                                "event_type": "as",
                                "remote_addr": "remote_addr",
                                "m": "request_method",
                                "uri": "abosolute_uri",
                                "param": "OperationalError",
                                "sid": "session_id",
                                "rid": "23947",
                                "payload": "tracestack",
                                "dp": "exsql",
                                "uid": "user_id"
                            })
                        ]
                    )

        def with_enabled_sensor_sql_exception_matching_excluded_route_test(self):
            sensors_json = {
                "errors": {
                    "sql_exception_enabled": True,
                    "exclude_routes": ["23947"]
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
                with patch("traceback.format_tb", return_value=["stack", "trace"]) as patched_format_tb:
                    exc_type = ProgrammingError
                    tb = Mock()

                    sensor.sql_exception_detected(appsensor_meta, exc_type.__name__, tb)
                    self.assertFalse(patched_format_tb.called)
                    self.assertFalse(patched_send.called)

        def with_enabled_sensor_sql_exception_nonmatching_excluded_route_test(self):
            sensors_json = {
                "errors": {
                    "sql_exception_enabled": True,
                    "exclude_routes": ["nonmatching"]
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
                with patch("traceback.format_tb", return_value=["stack", "trace"]) as patched_format_tb:
                    exc_type = ProgrammingError
                    tb = Mock()

                    sensor.sql_exception_detected(appsensor_meta, exc_type.__name__, tb)
                    patched_format_tb.assert_called_once_with(tb)

                    patched_send.assert_has_calls(
                        [
                            call({
                                "event_type": "as",
                                "remote_addr": "remote_addr",
                                "m": "request_method",
                                "uri": "abosolute_uri",
                                "param": "ProgrammingError",
                                "sid": "session_id",
                                "rid": "23947",
                                "payload": "tracestack",
                                "dp": "exsql",
                                "uid": "user_id"
                            })
                        ]
                    )
