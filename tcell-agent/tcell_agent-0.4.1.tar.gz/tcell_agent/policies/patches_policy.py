import logging

from tcell_agent.policies import TCellPolicy
from tcell_agent.patches import BlockRule

logger = logging.getLogger('tcell_agent').getChild(__name__)


class PatchesPolicy(TCellPolicy):
    api_identifier = "patches"

    def __init__(self, policy_json=None):
        super(PatchesPolicy, self).__init__()
        self.policy_id = None
        self.version = None
        self.enabled = False
        self.block_rules = []

        if policy_json is not None:
            self.load_from_json(policy_json)

    def check_ip_blocking(self, meta_data):
        if not self.enabled:
            return None

        for block_rule in self.block_rules:
            if block_rule.should_block(meta_data):
                return block_rule.resp()

        return None

    def load_from_json(self, policy_json):
        if "policy_id" in policy_json:
            self.policy_id = policy_json["policy_id"]
        else:
            raise Exception("Policy Id Not Found")

        if "version" in policy_json:
            self.version = policy_json["version"]

        if 1 is not self.version:
            logger.warn("Patches Policy not supported: %s" % self.version)
            return

        policy_data = policy_json.get("data")

        if policy_data:
            if "block_rules" in policy_data:
                block_rules_json = policy_data.get("block_rules", [])

                for block_rule_json in block_rules_json:
                    block_rule = BlockRule.from_json(block_rule_json)
                    if block_rule:
                        self.block_rules.append(block_rule)

            if "blocked_ips" in policy_data:
                blocked_ips = []
                for ip_info in policy_data.get("blocked_ips", []):
                    if "ip" in ip_info:
                        blocked_ips.append(ip_info["ip"])

                if len(blocked_ips) > 0:
                    block_rule = BlockRule.from_json({
                        "ips": blocked_ips
                    })

                    if block_rule:
                        self.block_rules.append(block_rule)

            self.enabled = len(self.block_rules) > 0
