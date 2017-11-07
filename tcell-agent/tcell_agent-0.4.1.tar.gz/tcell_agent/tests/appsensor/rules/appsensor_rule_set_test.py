import unittest
import re

from mock import patch
from tcell_agent.appsensor.rules.appsensor_rule_set import AppSensorRulePattern
from tcell_agent.appsensor.rules.appsensor_rule_set import AppSensorRuleSet


class AppSensorRuleSetTest(unittest.TestCase):
    def test_create_default(self):
        ruleset = AppSensorRuleSet()
        self.assertIsNone(ruleset.safe_pattern)
        self.assertEqual(ruleset.patterns, [])

    def test_add_pattern_from_dict_with_empty_dict(self):
        ruleset = AppSensorRuleSet()
        ruleset.add_pattern_from_dict({})
        self.assertIsNone(ruleset.safe_pattern)
        self.assertEqual(ruleset.patterns, [])

    def test_add_pattern_from_dict_with_common_pattern(self):
        ruleset = AppSensorRuleSet()
        ruleset.add_pattern_from_dict({"id": "1", "common": "common_regex"})
        self.assertIsNone(ruleset.safe_pattern)
        self.assertEqual(len(ruleset.patterns), 1)

        rule = ruleset.patterns[0]
        self.assertEqual(rule.pattern_id, "1")
        self.assertIsNotNone(rule.pattern_regex.search("common_regex ftw"))
        self.assertTrue(rule.enabled)

    def test_disable_common_pattern_by_overriding_pattern(self):
        ruleset = AppSensorRuleSet()
        ruleset.add_pattern_from_dict({"id": "1", "common": "common_regex", "python": "disabled"})
        self.assertIsNone(ruleset.safe_pattern)
        self.assertEqual(ruleset.patterns, [])

    def test_add_pattern_from_dict_with_python_pattern(self):
        ruleset = AppSensorRuleSet()
        ruleset.add_pattern_from_dict({"id": "1", "common": "common_regex", "python": "python_regex"})
        self.assertIsNone(ruleset.safe_pattern)
        self.assertEqual(len(ruleset.patterns), 1)

        rule = ruleset.patterns[0]
        self.assertEqual(rule.pattern_id, "1")
        self.assertIsNotNone(rule.pattern_regex.search("python_regex ftw"))
        self.assertTrue(rule.enabled)

    def check_violation_with_nil_param_value_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation(None, None, {}, True)
        self.assertIsNone(result)

    def check_violation_with_empty_param_value_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("", "", {}, True)
        self.assertIsNone(result)

    def check_violation_with_param_value_matching_safe_pattern_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("param_name", "super_safe", {}, True)
        self.assertIsNone(result)

    def check_violation_with_param_value_matching_nothing_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("param_name", "inane", {}, True)
        self.assertIsNone(result)

    def check_violation_with_param_value_matching_a_pattern_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("param_name", "evil <script>", {}, True)
        self.assertIsNotNone(result)
        self.assertEqual(result["pattern"], "1")
        self.assertEqual(result["param"], "param_name")
        self.assertEqual(result["value"], "evil <script>")

    def check_violation_with_param_value_matching_a_pattern_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("param_name", "evil <script>", {}, True)
        self.assertIsNotNone(result)
        self.assertEqual(result["pattern"], "1")
        self.assertEqual(result["param"], "param_name")
        self.assertEqual(result["value"], "evil <script>")

    def check_violation_with_param_value_matching_a_pattern_v1_compatability_off_no_patterns_enabled_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("param_name", "evil <script>", {}, False)
        self.assertIsNone(result)

    def check_violation_with_param_value_matching_disabled_pattern_v1_compatability_off_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("param_name", "evil <script>", {"2": True}, False)
        self.assertIsNone(result)

    def check_violation_with_param_value_matching_enabled_pattern_v1_compatability_off_test(self):
        ruleset = AppSensorRuleSet()
        ruleset.set_safe_pattern_from_string("super_safe")
        ruleset.add_pattern_from_dict({"id": "1", "common": "<(script)"})
        ruleset.add_pattern_from_dict({"id": "2", "common": "<(iframe)"})

        result = ruleset.check_violation("param_name", "evil <script>", {"1": True}, False)
        self.assertIsNotNone(result)
        self.assertEqual(result["pattern"], "1")
        self.assertEqual(result["param"], "param_name")
        self.assertEqual(result["value"], "evil <script>")
