import unittest

from future.backports.urllib.parse import urlparse
from future.backports.urllib.parse import parse_qs

from ...policies.clickjacking_policy import ClickjackingPolicy


class ContentSecurityPolicyTest(unittest.TestCase):
    def old_header_test(self):
        policy = ClickjackingPolicy()
        policy.loadFromHeaderString("Content-Security-Policy-Report-Only: test123")
        self.assertEqual(policy.headers(), [])

    def new_header_test(self):
        policy_json = {"policy_id": "xyzd", "headers": [{"name": "content-Security-POLICY", "value": "test321"}]}
        policy = ClickjackingPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.headers(), [["Content-Security-Policy", "test321"]])

    def header_with_report_uri_test(self):
        policy_json = {"policy_id": "xyzd",
                       "headers": [{"name": "content-Security-policy", "value": "normalvalue",
                                    "report-uri": "https://www.example.com/xys"}]}
        policy = ClickjackingPolicy()
        policy.load_from_json(policy_json)
        policy_headers = policy.headers("1", "2", "3")
        policy_header = policy_headers[0]
        print(policy_header)
        self.assertEqual(policy_header[0], "Content-Security-Policy")
        policy_header_value_parts = urlparse(policy_header[1].split(" ")[2])
        print(policy_header_value_parts)
        self.assertEqual(policy_header_value_parts.path, "/xys")
        print(policy_header_value_parts.query)
        query_params = parse_qs(policy_header_value_parts.query)
        print(query_params)
        self.assertEqual(query_params["tid"], ["1"])
        self.assertEqual(query_params["rid"], ["2"])
        self.assertEqual(query_params["sid"], ["3"])
