import unittest

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.patches import BlockRule


class BlockRuleTest(unittest.TestCase):
    def empty_action_from_json_test(self):
        block_rule = BlockRule.from_json({"action": None})

        self.assertIsNone(block_rule)

    def unknown_action_from_json_test(self):
        block_rule = BlockRule.from_json({"action": "bogus"})
        self.assertIsNone(block_rule)

    def with_no_ips_or_rids_provided_from_json_test(self):
        block_rule = BlockRule.from_json({"action": "block_403s"})
        self.assertIsNone(block_rule)

    def with_all_the_fields_provided_from_json_test(self):
        policy_json = {
            "ips": ["1.1.1.1", "1.3.3.3"],
            "rids": ["1396482959514716287", "1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)
        self.assertEqual(block_rule.ips, set(["1.1.1.1", "1.3.3.3"]))
        self.assertEqual(block_rule.rids, set(["1396482959514716287", "1396482959514716237"]))
        self.assertEqual(block_rule.action, "block_403s")

    def empty_ips_rid_matches_request_no_sensors_block_test(self):
        policy_json = {
            "ips": [],
            "rids": ["1396482959514716237"],
            "paths": [],
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "1396482959514716237"

        self.assertTrue(block_rule.should_block(appsensor_meta))

    def empty_ips_rid_matches_request_and_sensors_that_dont_match_block_test(self):
        policy_json = {
            "ips": [],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "1396482959514716237"
        appsensor_meta.get_dict = {"normal_param": "hi"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def empty_ips_rid_matches_request_and_sensors_that_match_block_test(self):
        policy_json = {
            "ips": [],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "1396482959514716237"
        appsensor_meta.get_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertTrue(block_rule.should_block(appsensor_meta))

    def empty_ips_rid_does_not_match_request_no_sensors_block_test(self):
        policy_json = {
            "ips": [],
            "rids": ["1396482959514716237"],
            "paths": [],
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "11111"

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def empty_ips_rid_does_not_match_request_and_sensors_that_dont_match_block_test(self):
        policy_json = {
            "ips": [],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "11111"
        appsensor_meta.get_dict = {"normal_param": "hi"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def empty_ips_rid_does_not_match_request_and_sensors_that_match_block_test(self):
        policy_json = {
            "ips": [],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "11111"
        appsensor_meta.get_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def ip_does_not_match_rid_matches_request_no_sensors_block_test(self):
        policy_json = {
            "ips": ["1.2.3.4"],
            "rids": ["1396482959514716237"],
            "paths": [],
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.1.1.1"
        appsensor_meta.route_id = "1396482959514716237"

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def ip_matches_rid_matches_request_no_sensors_block_test(self):
        policy_json = {
            "ips": ["1.2.3.4"],
            "rids": ["1396482959514716237"],
            "paths": [],
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "1396482959514716237"

        self.assertTrue(block_rule.should_block(appsensor_meta))

    def ip_matches_rid_matches_request_and_sensors_that_dont_match_block_test(self):
        policy_json = {
            "ips": ["1.2.3.4"],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "1396482959514716237"
        appsensor_meta.get_dict = {"normal_param": "hi"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def ip_matches_rid_matches_request_and_sensors_that_match_block_test(self):
        policy_json = {
            "ips": ["1.2.3.4"],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.2.3.4"
        appsensor_meta.route_id = "1396482959514716237"
        appsensor_meta.get_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertTrue(block_rule.should_block(appsensor_meta))

    def ip_does_not_match_rid_does_not_match_request_and_sensors_that_dont_match_block_test(self):
        policy_json = {
            "ips": ["1.2.3.4"],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.1.1.1"
        appsensor_meta.route_id = "11111"
        appsensor_meta.get_dict = {"normal_param": "hi"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def ip_does_not_match_rid_does_not_match_request_and_sensors_that_match_block_test(self):
        policy_json = {
            "ips": ["1.2.3.4"],
            "rids": ["1396482959514716237"],
            "paths": [],
            "sensor_matches": {
                "xss": {"patterns": ["1"]}
            },
            "action": "block_403s"
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.raw_remote_address = "1.1.1.1"
        appsensor_meta.route_id = "11111"
        appsensor_meta.get_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}
        appsensor_meta.headers_dict = {}

        self.assertFalse(block_rule.should_block(appsensor_meta))

    def exact_paths_block_test(self):
        policy_json = {
            "ips": [],
            "paths": [{"exact": "/"}, {"exact": "/index/"}, {"exact": "/home"}]
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.path = "/"
        appsensor_meta.raw_remote_address = "1.1.1.1"
        appsensor_meta.route_id = "11111"
        appsensor_meta.get_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}

        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/index"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/index/"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/home"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/home/"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/welcome"
        self.assertFalse(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/welcome/"
        self.assertFalse(block_rule.should_block(appsensor_meta))

    def exact_paths_with_blocked_ips_block_test(self):
        policy_json = {
            "ips": ["1.1.1.1"],
            "paths": [{"exact": "/"}, {"exact": "/index/"}, {"exact": "/home"}]
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.path = "/"
        appsensor_meta.raw_remote_address = "1.1.1.1"
        appsensor_meta.route_id = "11111"
        appsensor_meta.get_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}

        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/index"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/index/"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/home"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/home/"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/welcome"
        self.assertFalse(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/welcome/"
        self.assertFalse(block_rule.should_block(appsensor_meta))

    def starts_with_paths_block_test(self):
        policy_json = {
            "ips": [],
            "paths": [{"starts_with": "/index"}]
        }
        block_rule = BlockRule.from_json(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.path = "/"
        appsensor_meta.raw_remote_address = "1.1.1.1"
        appsensor_meta.route_id = "11111"
        appsensor_meta.get_dict = {"xss_param": "<script>"}
        appsensor_meta.post_dict = {}
        appsensor_meta.files_dict = {}
        appsensor_meta.cookie_dict = {}

        self.assertFalse(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/index"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/index/"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/index/subpath"
        self.assertTrue(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/home"
        self.assertFalse(block_rule.should_block(appsensor_meta))

        appsensor_meta.path = "/home/"
        self.assertFalse(block_rule.should_block(appsensor_meta))
