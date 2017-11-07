import json
import unittest

from ...policies.login_policy import LoginPolicy

policy_one = """
{
  "policy_id":"00a1",
  "data": {
    "options": {
       "login_failed_enabled":true,
       "login_success_enabled":true
    }
  }
}
"""


class LoginPolicyTest(unittest.TestCase):
    def classname_test(self):
        self.assertEqual(LoginPolicy.api_identifier, "login")

    def read_appensor_policy_test(self):
        policy_json = json.loads(policy_one)
        policy = LoginPolicy()
        self.assertEqual(policy.login_failed_enabled, False)
        self.assertEqual(policy.login_success_enabled, False)
        policy.load_from_json(policy_json)
        self.assertEqual(policy.login_failed_enabled, True)
        self.assertEqual(policy.login_success_enabled, True)
