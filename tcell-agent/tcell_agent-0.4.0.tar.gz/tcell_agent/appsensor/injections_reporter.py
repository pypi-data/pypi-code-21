import json

import tcell_agent

from tcell_agent.sensor_events.appsensor import build_from_native_lib_event


def get_payloads_logger():
    from tcell_agent.tcell_logger import get_app_firewall_payloads_logger
    return get_app_firewall_payloads_logger().getChild(__name__)


def report_and_log(events):
    if events:
        for event in events:
            tcell_agent.agent.TCellAgent.send(
                build_from_native_lib_event(event)
            )

            if event.get("log_payload"):
                event_to_log = {}
                event_to_log.update(event)
                if "log_payload" in event_to_log:
                    event_to_log["payload"] = event_to_log["log_payload"]
                    del event_to_log["log_payload"]

                cleaned_event = build_from_native_lib_event(event_to_log)
                get_payloads_logger().info(json.dumps(cleaned_event))
