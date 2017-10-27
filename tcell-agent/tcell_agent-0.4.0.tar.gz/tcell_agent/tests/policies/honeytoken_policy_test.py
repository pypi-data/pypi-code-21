import unittest
import json

from ...policies.honeytoken_policy import HoneytokenPolicy

policy_one = """
{
  "v":1,
  "policy_id":"xyz-def",
  "data": {
    "token_salt":"abcddef",
    "credentials":[
        {"id":"myid1", "token":"jjtokenjj"}
    ]
  }
}
"""

policy_nosalt = """
{
  "v":1,
  "policy_id":"xyz-def",
  "data": {
    "credentials":[
        {"id":"myid1", "token":"jjtokenjj"}
    ]
  }
}
"""

policy_empty = """
{
  "v":1,
  "policy_id":"xyz-def",
  "data": {
  }
}
"""


class HoneytokenPolicyTest(unittest.TestCase):
    def create_token_test(self):
        policy = HoneytokenPolicy()
        token = policy.create_credential_token("admin@tcell.io", "admin", "testsalt")
        self.assertEqual(token, "5492df8eb107b81b24b91d84d72512a3c765cc013d2b7af7d5f9fa0832811624")

    def empty_policy_test(self):
        policy_json = json.loads(policy_empty)
        policy = HoneytokenPolicy()

        self.assertEqual(policy.token_salt, None)
        self.assertEqual(policy.cred_tokens, None)

        policy.load_from_json(policy_json)

        self.assertEqual(policy.token_salt, None)
        self.assertEqual(policy.cred_tokens, None)

    def no_salt_policy_test(self):
        policy_json = json.loads(policy_nosalt)
        policy = HoneytokenPolicy()

        self.assertEqual(policy.token_salt, None)
        self.assertEqual(policy.cred_tokens, None)

        policy.load_from_json(policy_json)

        self.assertEqual(policy.token_salt, None)
        self.assertEqual(policy.cred_tokens, None)

    def normal_policy_test(self):
        policy_json = json.loads(policy_one)
        policy = HoneytokenPolicy()
        policy.load_from_json(policy_json)

        self.assertEqual(policy.token_salt, "abcddef")
        self.assertEqual(policy.cred_tokens, {"jjtokenjj": "myid1"})
