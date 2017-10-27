import unittest

from mock import patch
from nose.tools import raises

from tcell_agent.agent import TCellAgent
from tcell_agent.config import CONFIGURATION
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.policies.command_injection_policy import CommandInjectionPolicy, CommandRule


class CommandInjectionPolicyTest(unittest.TestCase):
    def classname_test(self):
        self.assertEqual(CommandInjectionPolicy.api_identifier, "cmdi")

    def none_policy_test(self):
        policy = CommandInjectionPolicy()

        self.assertIsNone(policy.policy_id)
        self.assertIsNone(policy.version)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.overall_action, None)
        self.assertEqual(policy.command_rules, {})
        self.assertEqual(policy.compound_statement_rule, None)
        self.assertEqual(policy.collect_full_commandline, False)

    @raises(Exception)
    def empty_policy_test(self):
        CommandInjectionPolicy({})

    def empty_version_policy_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id"
        })

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertIsNone(policy.version)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.overall_action, None)
        self.assertEqual(policy.command_rules, {})
        self.assertEqual(policy.compound_statement_rule, None)
        self.assertEqual(policy.collect_full_commandline, False)

    def empty_command_rules_policy_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": []}})

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.overall_action, None)
        self.assertEqual(policy.command_rules, {})
        self.assertEqual(policy.compound_statement_rule, None)
        self.assertEqual(policy.collect_full_commandline, False)

    def empty_compound_statement_rules_policy_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": []}})

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertFalse(policy.enabled)
        self.assertEqual(policy.overall_action, None)
        self.assertEqual(policy.command_rules, {})
        self.assertEqual(policy.compound_statement_rule, None)
        self.assertEqual(policy.collect_full_commandline, False)

    def populated_command_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [{
                    "rule_id": "1",
                    "action": "block"
                }, {
                    "rule_id": "2",
                    "command": "nc",
                    "action": "ignore"}]}})

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertTrue(policy.enabled)
        self.assertIsNotNone(policy.overall_action)
        self.assertEqual(policy.overall_action.rule_id, "1")
        self.assertEqual(policy.overall_action.action, CommandRule.BLOCK)
        self.assertIsNone(policy.overall_action.command)
        self.assertEqual(len(policy.command_rules), 1)
        self.assertIsNotNone(policy.command_rules["nc"])
        self.assertEqual(policy.command_rules["nc"].rule_id, "2")
        self.assertEqual(policy.command_rules["nc"].action, CommandRule.IGNORE)
        self.assertEqual(policy.command_rules["nc"].command, "nc")
        self.assertIsNone(policy.compound_statement_rule)
        self.assertEqual(policy.collect_full_commandline, False)

    def populated_compound_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [{
                    "rule_id": "3",
                    "action": "block"}]}})

        self.assertEqual(policy.policy_id, "policy_id")
        self.assertEqual(policy.version, 1)
        self.assertTrue(policy.enabled)
        self.assertEqual(policy.overall_action, None)
        self.assertEqual(policy.command_rules, {})
        self.assertIsNotNone(policy.compound_statement_rule)
        self.assertEqual(policy.compound_statement_rule.rule_id, "3")
        self.assertEqual(policy.compound_statement_rule.action, CommandRule.BLOCK)
        self.assertIsNone(policy.compound_statement_rule.command)
        self.assertEqual(policy.collect_full_commandline, False)

    def none_collect_full_command_line_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "collect_full_commandline": None}})

        self.assertEqual(policy.collect_full_commandline, False)

    def false_collect_full_command_line_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "collect_full_commandline": False}})

        self.assertEqual(policy.collect_full_commandline, False)

    def true_collect_full_command_line_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "collect_full_commandline": True}})

        self.assertEqual(policy.collect_full_commandline, True)

    def blank_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": []}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            self.assertFalse(patched_send.called)

    def ignore_all_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [{"rule_id": "1", "action": "ignore"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            self.assertFalse(patched_send.called)

    def report_all_command_rules_disabled_allow_payloads_block_test(self):
        old_allow = CONFIGURATION.allow_payloads
        CONFIGURATION.allow_payloads = False

        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "collect_full_commandline": True,
                "command_rules": [{"rule_id": "1", "action": "report"}]}})
        tcell_context = TCellInstrumentationContext()
        tcell_context.method = "GET"
        tcell_context.remote_addr = "1.1.1.1"
        tcell_context.route_id = "12345"
        tcell_context.session_id = "sldfjk2343"
        tcell_context.user_id = "user_id"

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)

            CONFIGURATION.allow_payloads = old_allow

            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "1"}, {"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": False
            })

    def block_all_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "collect_full_commandline": True,
                "command_rules": [{"rule_id": "1", "action": "block"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "1"}, {"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True,
                "full_commandline": "cat /etc/passwd && grep root"
            })

    def ignore_all_ignore_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "collect_full_commandline": True,
                "command_rules": [
                    {"rule_id": "1", "action": "ignore"},
                    {"rule_id": "2", "action": "ignore", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            self.assertFalse(patched_send.called)

    def ignore_all_report_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "ignore"},
                    {"rule_id": "2", "action": "report", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "2"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": False
            })

    def ignore_all_block_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "ignore"},
                    {"rule_id": "2", "action": "block", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "2"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True
            })

    def report_all_ignore_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "report"},
                    {"rule_id": "2", "action": "ignore", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": False
            })

    def report_all_report_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "report"},
                    {"rule_id": "2", "action": "report", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": False
            })

    def report_all_block_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "report"},
                    {"rule_id": "2", "action": "block", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True
            })

    def block_all_ignore_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "block"},
                    {"rule_id": "2", "action": "ignore", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True
            })

    def block_all_report_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "block"},
                    {"rule_id": "2", "action": "report", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True
            })

    def block_all_block_cat_command_rules_block_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "command_rules": [
                    {"rule_id": "1", "action": "block"},
                    {"rule_id": "2", "action": "block", "command": "cat"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True
            })

    def ignore_one_command_compound_statement_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [
                    {"rule_id": "1", "action": "ignore"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd", None)
            self.assertFalse(patched_send.called)

    def ignore_two_command_compound_statement_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [
                    {"rule_id": "1", "action": "ignore"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            self.assertFalse(patched_send.called)

    def report_one_command_compound_statement_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [
                    {"rule_id": "1", "action": "report"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd", None)
            self.assertFalse(patched_send.called)

    def report_two_command_compound_statement_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [
                    {"rule_id": "1", "action": "report"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": False
            })

    def block_one_command_compound_statement_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [
                    {"rule_id": "1", "action": "block"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd", None)
            self.assertFalse(patched_send.called)

    def block_two_command_compound_statement_rules_test(self):
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [
                    {"rule_id": "1", "action": "block"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True
            })

    def multiple_compound_statemetns_block_two_command_compound_statement_rules_test(self):
        # multiple compound statements present only first one is taken
        policy = CommandInjectionPolicy({
            "policy_id": "policy_id",
            "version": 1,
            "data": {
                "compound_statement_rules": [
                    {"rule_id": "1", "action": "block"}, {"rule_id": "2", "action": "ignore"}]}})

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.block("cat /etc/passwd && grep root", None)
            patched_send.assert_called_once_with({
                "event_type": "cmdi",
                "matches": [{"rule_id": "1"}],
                "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                "blocked": True
            })
