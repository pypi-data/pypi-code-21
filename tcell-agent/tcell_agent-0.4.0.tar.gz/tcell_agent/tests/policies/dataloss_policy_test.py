import unittest
import json

from ...policies.dataloss_policy import DataLossPolicy

policy_one = """
{
  "v":1,
  "policy_id":"xyz-def",
  "data":{
    "db_protections":[
      {"tables":["work_infos"],
       "fields":["SSN"],
       "actions":{"body":["redact"]}
      },
      {"tables":["work_infos"],
       "fields":["income"],
       "actions":{"body":["redact"], "log":["redact"]}
      }
    ]
  }
}
"""

policy_db_protection_by_route = """
{
  "v":1,
  "policy_id":"xyz-def",
  "data":{
    "db_protections":[
      {"scope":"route",
       "route_ids":["abcdefg"],
       "tables":["work_infos"],
       "fields":["SSN"],
       "actions":{"body":["redact"]}
      },
      {"tables":["work_infos"],
       "fields":["income"],
       "actions":{"body":["redact"], "log":["redact"]}
      }
    ]
  }
}
"""

policy_session_protection_one = """
{
  "v":1,
  "policy_id":"xyz-def",
  "data":{
    "session_id_protections":{"body":["redact"], "log":["event"]}
  }
}
"""

policy_data_discovery = """
{
  "v":1,
  "policy_id":"xyz-def",
  "data":{
    "data_discovery":{
      "database_enabled":true
    },
    "session_id_protections":{"body":["redact"], "log":["event"]}
  }
}"""


class DataLossPolicyTest(unittest.TestCase):
    def session_test(self):
        policy_json = json.loads(policy_session_protection_one)
        policy = DataLossPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.get_actions_for_session_id().body_redact, True)
        self.assertEqual(policy.get_actions_for_session_id().log_event, True)

    def normal_policy_test(self):
        policy_json = json.loads(policy_one)
        policy = DataLossPolicy()
        policy.load_from_json(policy_json)
        actions_ssn = policy.get_actions_for_db_field("*", "*", "work_infos", "SSN")
        action_ssn = list(actions_ssn)[0]
        self.assertEqual(action_ssn.body_redact, True)
        self.assertEqual(action_ssn.log_redact, False)
        actions_income = policy.get_actions_for_db_field("test", "test", "work_infos", "income")
        action_income = list(actions_income)[0]
        self.assertEqual(action_income.body_redact, True)
        self.assertEqual(action_income.log_redact, True)

    def normal_policy_test_using_route(self):
        policy_json = json.loads(policy_db_protection_by_route)
        policy = DataLossPolicy()
        policy.load_from_json(policy_json)

        actions_ssn = policy.get_actions_for_db_field("*", "*", "work_infos", "SSN", route="abcdefg")
        action_ssn = list(actions_ssn)[0]
        self.assertEqual(action_ssn.body_redact, True)
        self.assertEqual(action_ssn.log_redact, False)

        actions_income = policy.get_actions_for_db_field("test", "test", "work_infos", "income")
        action_income = list(actions_income)[0]
        self.assertEqual(action_income.body_redact, True)
        self.assertEqual(action_income.log_redact, True)

    def discovery_policy_test(self):
        policy_json = json.loads(policy_data_discovery)
        policy = DataLossPolicy()
        self.assertEqual(policy.database_discovery_enabled, False)
        policy.load_from_json(policy_json)
        self.assertEqual(policy.database_discovery_enabled, True)
