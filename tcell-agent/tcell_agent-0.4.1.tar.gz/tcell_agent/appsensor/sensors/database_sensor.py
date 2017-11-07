import tcell_agent
from tcell_agent.sensor_events.appsensor import build_from_meta


class DatabaseSensor(object):
    POLICY_SENSOR_KEY = "database"
    DP_CODE = "dbmaxrows"

    def __init__(self, collect_full_uri=False, sensors_json=None):
        self.enabled = False
        self.max_rows = 1001
        self.excluded_route_ids = set()
        self.collect_full_uri = collect_full_uri

        if sensors_json is not None:
            self.enabled = self.POLICY_SENSOR_KEY in sensors_json
            policy_json = sensors_json.get(self.POLICY_SENSOR_KEY, {})
            large_result = policy_json.get("large_result", {})
            self.max_rows = large_result.get("limit", self.max_rows)

            self.excluded_route_ids = set(policy_json.get("exclude_routes", []))

    def should_check(self, route_id):
        return self.enabled and route_id not in self.excluded_route_ids

    def check(self, appsensor_meta, number_of_records):
        if self.should_check(appsensor_meta.route_id) and number_of_records > self.max_rows:
            event = build_from_meta(
                appsensor_meta=appsensor_meta,
                detection_point=self.DP_CODE,
                parameter=None,
                meta={"rows": number_of_records},
                payload=None,
                collect_full_uri=self.collect_full_uri
            )

            tcell_agent.agent.TCellAgent.send(event)
