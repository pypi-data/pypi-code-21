import unittest

from tcell_agent.policies.command_injection_policy import CommandRule


class CommandRuleTest(unittest.TestCase):
    def none_policy_json(self):
        command_rule = CommandRule(None)

        self.assertFalse(command_rule.valid())
        self.assertIsNone(command_rule.rule_id)
        self.assertIsNone(command_rule.action)
        self.assertIsNone(command_rule.command)
        self.assertFalse(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertFalse(command_rule.should_block())

    def empty_policy_json(self):
        command_rule = CommandRule({})

        self.assertFalse(command_rule.valid())
        self.assertIsNone(command_rule.rule_id)
        self.assertIsNone(command_rule.action)
        self.assertIsNone(command_rule.command)
        self.assertFalse(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertFalse(command_rule.should_block())

    def rule_id_policy_test(self):
        command_rule = CommandRule({"rule_id": "1"})

        self.assertFalse(command_rule.valid())
        self.assertEqual(command_rule.rule_id, "1")
        self.assertIsNone(command_rule.action)
        self.assertIsNone(command_rule.command)
        self.assertFalse(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertFalse(command_rule.should_block())

    def action_policy_test(self):
        command_rule = CommandRule({"action": "block"})

        self.assertFalse(command_rule.valid())
        self.assertIsNone(command_rule.rule_id)
        self.assertEqual(command_rule.action, "block")
        self.assertIsNone(command_rule.command)
        self.assertFalse(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertTrue(command_rule.should_block())

    def unknown_action_policy_test(self):
        command_rule = CommandRule({"action": "blergh"})

        self.assertFalse(command_rule.valid())
        self.assertIsNone(command_rule.rule_id)
        self.assertEqual(command_rule.action, "blergh")
        self.assertIsNone(command_rule.command)
        self.assertFalse(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertFalse(command_rule.should_block())

    def command_policy_test(self):
        command_rule = CommandRule({"command": "nc"})

        self.assertFalse(command_rule.valid())
        self.assertIsNone(command_rule.rule_id)
        self.assertIsNone(command_rule.action)
        self.assertEqual(command_rule.command, "nc")
        self.assertFalse(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertFalse(command_rule.should_block())

    def ignore_action_policy_test(self):
        command_rule = CommandRule({"rule_id": "1", "action": "ignore"})

        self.assertTrue(command_rule.valid())
        self.assertEqual(command_rule.rule_id, "1")
        self.assertEqual(command_rule.action, "ignore")
        self.assertIsNone(command_rule.command)
        self.assertTrue(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertFalse(command_rule.should_block())

    def report_action_policy_test(self):
        command_rule = CommandRule({"rule_id": "1", "action": "report"})

        self.assertTrue(command_rule.valid())
        self.assertEqual(command_rule.rule_id, "1")
        self.assertEqual(command_rule.action, "report")
        self.assertIsNone(command_rule.command)
        self.assertFalse(command_rule.should_ignore())
        self.assertTrue(command_rule.should_report())
        self.assertFalse(command_rule.should_block())

    def block_action_policy_test(self):
        command_rule = CommandRule({"rule_id": "1", "action": "block"})

        self.assertTrue(command_rule.valid())
        self.assertEqual(command_rule.rule_id, "1")
        self.assertEqual(command_rule.action, "block")
        self.assertIsNone(command_rule.command)
        self.assertFalse(command_rule.should_ignore())
        self.assertFalse(command_rule.should_report())
        self.assertTrue(command_rule.should_block())
