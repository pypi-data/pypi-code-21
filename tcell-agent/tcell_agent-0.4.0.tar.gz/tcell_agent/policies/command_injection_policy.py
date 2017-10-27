import logging

import tcell_agent

from tcell_agent.config import CONFIGURATION
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.policies import TCellPolicy
from tcell_agent.sensor_events.command_injection import CommandInjectionEvent, CommandInjectionMatchEvent

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


class CommandRule(object):
    IGNORE = "ignore"
    REPORT = "report"
    BLOCK = "block"

    def __init__(self, policy_json):
        self.rule_id = None
        self.action = None
        self.command = None

        if policy_json:
            self.rule_id = policy_json.get("rule_id")
            self.action = policy_json.get("action")
            self.command = policy_json.get("command")

    def should_ignore(self):
        return self.action == self.IGNORE

    def should_report(self):
        return self.action == self.REPORT

    def should_block(self):
        return self.action == self.BLOCK

    def valid(self):
        return self.rule_id and self.action in [self.IGNORE, self.REPORT, self.BLOCK]


class CommandInjectionPolicy(TCellPolicy):
    api_identifier = "cmdi"

    def __init__(self, policy_json=None):
        super(CommandInjectionPolicy, self).__init__()
        self.enabled = False
        self.version = None
        self.overall_action = None
        self.command_rules = {}
        self.compound_statement_rule = None
        self.collect_full_commandline = False

        if policy_json is not None:
            self.load_from_json(policy_json)

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        if "version" in policy_json:
            self.version = policy_json["version"]

        if 1 is not self.version:
            LOGGER.warn("Patches Policy not supported: %s" % self.version)
            return

        policy_data = policy_json.get("data")

        if policy_data:
            self.collect_full_commandline = policy_data.get("collect_full_commandline") or False
            for command_rule_policy in (policy_data.get("command_rules") or []):
                command_rule = CommandRule(command_rule_policy)
                if command_rule.valid():
                    command = command_rule.command
                    if command:
                        if self.command_rules.get(command):
                            LOGGER.warn(
                                "CommandInjectionPolicy multiple rules for one command (dropping rule): {c} {a}".
                                format(c=command, a=command_rule.action))
                        else:
                            self.command_rules[command] = command_rule
                    elif not command_rule.should_ignore():
                        self.overall_action = command_rule

            compound_statement_rules = policy_data.get("compound_statement_rules")
            if compound_statement_rules and len(compound_statement_rules) > 0:
                self.compound_statement_rule = CommandRule(compound_statement_rules[0])
                if not self.compound_statement_rule.valid() or self.compound_statement_rule.should_ignore():
                    self.compound_statement_rule = None

            self.enabled = self.overall_action is not None or self.compound_statement_rule is not None or len(self.command_rules) > 0

    def block(self, cmd, tcell_context):
        if not self.enabled:
            return False

        commands = self._rust_parse_cmd(cmd).get('commands', [])
        command_injection_match_events = []
        block_command = False

        if len(commands) > 1 and self.compound_statement_rule:
            if not self.compound_statement_rule.should_ignore():
                command_injection_match_events.append(
                    CommandInjectionMatchEvent(self.compound_statement_rule.rule_id, self.compound_statement_rule.command))
                block_command = block_command or self.compound_statement_rule.should_block()

        for command_info in commands:
            command = command_info["command"]
            command_rule = self.command_rules.get(command) or self.overall_action
            if command_rule:
                if command_rule.should_ignore():
                    continue
                else:
                    command_injection_match_events.append(
                        CommandInjectionMatchEvent(command_rule.rule_id, command))
                    block_command = block_command or command_rule.should_block()

        if len(command_injection_match_events) > 0:
            method, remote_address, route_id, session_id, user_id, full_commandline = None, None, None, None, None, None
            if tcell_context:
                method = tcell_context.method
                remote_address = tcell_context.remote_addr
                route_id = tcell_context.route_id
                session_id = tcell_context.session_id
                user_id = tcell_context.user_id

            if self.collect_full_commandline and CONFIGURATION.allow_payloads:
                full_commandline = cmd

            tcell_agent.agent.TCellAgent.send(
                CommandInjectionEvent(
                    commands,
                    blocked=block_command,
                    matches=command_injection_match_events,
                    method=method,
                    remote_address=remote_address,
                    route_id=route_id,
                    session_id=session_id,
                    user_id=user_id,
                    full_commandline=full_commandline))

        return block_command

    # extract for easy testing
    def _rust_parse_cmd(self, cmd):
        from tcell_agent.rust.whisperer import parse_cmd
        command_info = safe_wrap_function("Parse command", parse_cmd, cmd)
        return command_info or {}
