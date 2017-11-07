# -*- coding: utf-8 -*-

import unittest

from mock import patch

from tcell_agent.agent import TCellAgent
from tcell_agent.policies.http_redirect_policy import HttpRedirectPolicy, wildcard_re
from tcell_agent.sensor_events.http_redirect import RedirectSensorEvent


class HttpRedirectPolicyTest(unittest.TestCase):
    def min_header_test(self):
        policy_json = {"policy_id": "xyzd"}
        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "xyzd")
        self.assertEqual(policy.enabled, False)
        self.assertEqual(policy.block, False)
        self.assertEqual(policy.whitelist, [])
        self.assertFalse(policy.data_scheme_allowed)

    def small_header_test(self):
        policy_json = {"policy_id": "nyzd", "data": {"enabled": True}}
        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, False)
        self.assertEqual(policy.whitelist, [])
        self.assertFalse(policy.data_scheme_allowed)

    def large_header_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertFalse(policy.data_scheme_allowed)

    def same_domain_redirect_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertFalse(policy.data_scheme_allowed)

        check = policy.process_location(
            "0.1.1.0",
            "GET",
            "localhost:8011",
            "/etc/123",
            200,
            "http://localhost:8011/abc/def")

        self.assertEqual(check, "http://localhost:8011/abc/def")

    def asterisk_in_domain_redirect_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["*.allowed*.com"],
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)

        check = policy.process_location(
            "0.1.1.0",
            "GET",
            "localhost:8011",
            "/etc/123",
            200,
            "http://allowed.com")

        self.assertEqual(check, "http://allowed.com")

        check = policy.process_location(
            "0.1.1.0",
            "GET",
            "localhost:8011",
            "/etc/123",
            200,
            "http://www.alloweddomain.com")

        self.assertEqual(check, "http://www.alloweddomain.com")

    def domains_with_ports_should_be_removed_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "block": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        self.assertFalse(policy.data_scheme_allowed)

        with patch.object(TCellAgent, 'send', return_value=None) as patched_send_event:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/some/path",
                200,
                "http://192.168.99.100:3000")

            self.assertEqual(check, "/")

            patched_send_event.assert_called_once_with(
                RedirectSensorEvent(
                    "0.1.1.0",
                    "GET",
                    "localhost",
                    "/some/path",
                    200,
                    "192.168.99.100",
                    None,
                    None,
                    None))

    def data_scheme_allowed_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True,
                "dataSchemeAllowed": True}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertTrue(policy.data_scheme_allowed)

        check = policy.process_location(
            "0.1.1.0",
            "GET",
            "localhost:8011",
            "/etc/123",
            200,
            "data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K")

        self.assertEqual(check, "data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K")

    def data_scheme_not_allowed_test(self):
        policy_json = {
            "policy_id": "nyzd",
            "data": {
                "enabled": True,
                "whitelist": ["whitelisted"],
                "block": True,
                "dataSchemeAllowed": False}}

        policy = HttpRedirectPolicy()
        policy.load_from_json(policy_json)
        self.assertEqual(policy.policy_id, "nyzd")
        self.assertEqual(policy.enabled, True)
        self.assertEqual(policy.block, True)
        whitelist = ["whitelisted"]
        compiled_re = [wildcard_re(item) for item in whitelist]
        self.assertEqual(policy.whitelist, compiled_re)
        self.assertFalse(policy.data_scheme_allowed)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send_event:
            check = policy.process_location(
                "0.1.1.0",
                "GET",
                "localhost:8011",
                "/etc/123",
                200,
                "data:text/html base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K")

            self.assertEqual(check, "/")

            patched_send_event.assert_called_once_with(
                RedirectSensorEvent(
                    "0.1.1.0",
                    "GET",
                    "localhost:8011",
                    "localhost:8011",
                    200,
                    "data:",
                    None,
                    None,
                    None))
