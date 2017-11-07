import traceback

import tcell_agent
from tcell_agent.sensor_events.appsensor import build_from_meta


class MiscSensor(object):
    POLICY_SENSOR_KEY = "errors"

    def __init__(self, collect_full_uri=False, sensors_json=None):
        self.csrf_exception_enabled = False
        self.sql_exception_enabled = False
        self.excluded_route_ids = {}
        self.collect_full_uri = collect_full_uri

        if sensors_json is not None:
            policy_json = sensors_json.get(self.POLICY_SENSOR_KEY, {})
            self.csrf_exception_enabled = policy_json.get("csrf_exception_enabled", False)
            self.sql_exception_enabled = policy_json.get("sql_exception_enabled", False)

            for route_id in policy_json.get("exclude_routes", []):
                self.excluded_route_ids[route_id] = True

    def csrf_rejected(self, appsensor_meta):
        if not self.csrf_exception_enabled:
            return

        if self.excluded_route_ids.get(appsensor_meta.route_id, False):
            return False

        event = build_from_meta(
            appsensor_meta=appsensor_meta,
            detection_point="excsrf",
            parameter=None,
            meta=None,
            payload="[CSRF token missing or incorrect. No Stacktrace available.]",
            collect_full_uri=self.collect_full_uri
        )

        tcell_agent.agent.TCellAgent.send(event)

    def sql_exception_detected(self, appsensor_meta, exc_type_name, tb):
        if not self.sql_exception_enabled:
            return

        if self.excluded_route_ids.get(appsensor_meta.route_id, False):
            return False

        stack_trace = traceback.format_tb(tb)
        stack_trace.reverse()

        event = build_from_meta(
            appsensor_meta=appsensor_meta,
            detection_point="exsql",
            parameter=exc_type_name,
            meta=None,
            payload=''.join(stack_trace),
            collect_full_uri=self.collect_full_uri
        )

        tcell_agent.agent.TCellAgent.send(event)
