import json

import unittest

from tcell_agent.config import CONFIGURATION
from tcell_agent.agent import TCellAgent


class AgentMetricsMetricsCountTest(unittest.TestCase):
    def setUp(self):
        CONFIGURATION.version = 1
        CONFIGURATION.api_key = "Test_-ApiKey=="
        CONFIGURATION.app_id = "TestAppId-AppId"
        CONFIGURATION.host_identifier = "TestHostIdentifier"
        CONFIGURATION.uuid = "test-uuid-test-uuid"
        CONFIGURATION.fetch_policies_from_tcell = False

        added_events = []
        self.added_events = added_events

        def addEvent(_, event):
            event.post_process()
            added_events.append(event)

        @classmethod
        def send(cls, event):
            cls.get_agent().addEvent(event)

        self.old_add_events = TCellAgent.addEvent
        TCellAgent.addEvent = addEvent
        self.old_send = TCellAgent.send
        TCellAgent.send = send

        self.old_tcell_agent = TCellAgent.tCell_agent
        TCellAgent.tCell_agent = TCellAgent()
        TCellAgent.tCell_agent.policies = {}

    def tearDown(self):
        TCellAgent.addEvent = self.old_add_events
        TCellAgent.send = self.old_send
        TCellAgent.tCell_agent = self.old_tcell_agent

    def test_event_on_metrics_accumulated(self):
        policy_one = """
        {
          "login":{
            "policy_id":"00a1",
            "data": {
              "options": {
                 "session_hijacking_enabled":true,
                 "login_success_enabled":true
              }
            }
          }
        }
        """
        policy_json = json.loads(policy_one)
        TCellAgent.get_agent().process_policies(policy_json, cache=False)

        old_send = TCellAgent.send

        @classmethod
        def send(cls, event):
            cls.get_agent().addEvent(event)
            if (event["event_type"] == "dummy"):
                cls.get_agent().agent_metrics.get_and_reset_sesssion_metric()

        TCellAgent.send = send

        try:
            for sessionid_num in range(0, 300):
                session_id = "a" * 40 + str(sessionid_num)
                TCellAgent.request_metric(
                    "route_1",
                    300,
                    "123.333.444.555",
                    "UserAgent x 4/05.31.2/2@23",
                    session_id=session_id,
                    user_id="bob@bob.com")

            self.assertEqual(self.added_events[0]["event_type"], "dummy")
            self.assertEqual(len(self.added_events), 3)
            self.assertEqual(TCellAgent.get_agent().agent_metrics.get_object_count(), 144)
        finally:
            TCellAgent.send = old_send

    def test_event_on_metrics_accumulated_policy_off(self):
        policy_one = """
        {
         "login":{
          "policy_id":"00a1",
          "data": {
            "options": {
               "session_hijacking_enabled":false,
               "login_success_enabled":true
            }
          }
         }
        }
        """
        policy_json = json.loads(policy_one)
        TCellAgent.get_agent().process_policies(policy_json, cache=False)

        old_send = TCellAgent.send

        @classmethod
        def send(cls, event):
            cls.get_agent().addEvent(event)
            if (event["event_type"] == "dummy"):
                cls.get_agent().agent_metrics.get_and_reset_sesssion_metric()

        TCellAgent.send = send

        try:
            for sessionid_num in range(0, 300):
                session_id = "a" * 40 + str(sessionid_num)
                TCellAgent.request_metric(
                    "route_1",
                    300,
                    "123.333.444.555",
                    "UserAgent x 4/05.31.2/2@23",
                    session_id=session_id,
                    user_id="bob@bob.com")

            self.assertEqual(len(self.added_events), 0)
            self.assertEqual(TCellAgent.get_agent().agent_metrics.get_object_count(), 0)
        finally:
            TCellAgent.send = old_send

    def test_count_of_metrics(self):
        from ...agent.metrics import AgentMetrics

        metrics = AgentMetrics()
        metrics.add_session_track_metric("sessid1", "userid1", "useragent2", "1.2.2.2")
        self.assertEqual(metrics.get_object_count(), 3)
        metrics.get_and_reset_sesssion_metric()
        self.assertEqual(metrics.get_object_count(), 0)

    def test_event_on_route_metrics_accumulated(self):
        old_send = TCellAgent.send

        @classmethod
        def send(cls, event):
            cls.get_agent().addEvent(event)
            cls.get_agent().agent_metrics.get_and_reset_route_count_table()

        TCellAgent.send = send
        try:
            for route in range(0, 320):
                route_id = "a" * 40 + str(route)
                TCellAgent.request_metric(route_id,
                                          300,
                                          "123.333.444.555",
                                          "UserAgent x 4/05.31.2/2@23",
                                          "abcdefg",
                                          user_id="bob@bob.com")
            self.assertEqual(len(self.added_events), 2)
            self.assertEqual(self.added_events[0]["event_type"], "dummy")
            self.assertEqual(len(TCellAgent.get_agent().agent_metrics._route_count_table), 20)
        finally:
            TCellAgent.send = old_send
