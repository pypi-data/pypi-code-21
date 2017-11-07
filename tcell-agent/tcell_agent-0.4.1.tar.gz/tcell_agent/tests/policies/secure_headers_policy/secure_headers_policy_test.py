import unittest

from ....policies.secure_headers_policy import SecureHeadersPolicy


class SecureHeaderPolicyTest(unittest.TestCase):
    def reserved_header_test(self):
        policy_json = {"policy_id": "xyzd", "headers": [{"name": "content-Security-POLICY", "value": "test321"}]}
        policy = SecureHeadersPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.headers(), [])

    def one_header_test(self):
        policy_json = {"policy_id": "xyzd", "headers": [{"name": "X-Content-Type-Options", "value": "nosniff"}]}
        policy = SecureHeadersPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.headers(), [["X-Content-Type-Options", "nosniff"]])
