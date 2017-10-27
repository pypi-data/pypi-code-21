import unittest

from collections import namedtuple
from nose.tools import raises

from django.utils.datastructures import MultiValueDict

from tcell_agent.appsensor.django import set_request
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies import PatchesPolicy

FakeFile = namedtuple("FakeFile", ["name"], verbose=True)
FakeRequest = namedtuple("FakeRequest", ["body", "META", "GET", "POST", "FILES", "COOKIES", "environ"], verbose=True)
FakeResponse = namedtuple("FakeResponse", ["content", "status_code"], verbose=True)


class PatchesPolicyTest(unittest.TestCase):
    def classname_test(self):
        self.assertEqual(PatchesPolicy.api_identifier, "patches")

    def none_policy_test(self):
        policy = PatchesPolicy()

        self.assertIsNone(policy.policy_id)
        self.assertIsNone(policy.version)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.block_rules, [])

    @raises(Exception)
    def empty_policy_test(self):
        PatchesPolicy({})

    def empty_version_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id"
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertIsNone(policy.version)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.block_rules, [])

    def empty_data_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {}
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.enabled)
        self.assertEqual(len(policy.block_rules), 0)

    def empty_blocked_ips_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": []
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.enabled)
        self.assertEqual(len(policy.block_rules), 0)

    def populated_blocked_ips_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertTrue(policy.enabled)
        self.assertEqual(len(policy.block_rules), 1)
        self.assertEqual(policy.block_rules[0].ips, set(["1.1.1.1"]))
        self.assertEqual(policy.block_rules[0].rids, set())
        self.assertEqual(policy.block_rules[0].action, "block_403s")

    def populated_blocked_ips_with_wrong_version_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 2,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 2)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.block_rules, [])

    def populated_blocked_ips_with_missing_ip_policy_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip_wrong": "1.1.1.1"
                }]
            }
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.block_rules, [])

    def disabled_ip_blocking_check_ip_blocking_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
            }
        })

        meta_data = {}

        self.assertFalse(policy.check_ip_blocking(meta_data))

    def enabled_ip_blocking_check_ip_blocking_with_none_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = None
        appsensor_meta.raw_remote_address = None
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        self.assertFalse(policy.check_ip_blocking(appsensor_meta))

    def enabled_ip_blocking_check_ip_blocking_with_empty_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = ""
        appsensor_meta.raw_remote_address = ""
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        self.assertFalse(policy.check_ip_blocking(appsensor_meta))

    def enabled_ip_blocking_check_ip_blocking_with_blocked_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "1.1.1.1"
        appsensor_meta.raw_remote_address = "1.1.1.1"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        resp = policy.check_ip_blocking(appsensor_meta)

        self.assertEqual(resp, 403)

    def enabled_ip_blocking_check_ip_blocking_with_non_blocked_ip_test(self):
        policy = PatchesPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "blocked_ips": [{
                    "ip": "1.1.1.1"
                }]
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "2.2.2.2"
        appsensor_meta.raw_remote_address = "2.2.2.2"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        self.assertFalse(policy.check_ip_blocking(appsensor_meta))
