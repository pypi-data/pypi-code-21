import logging

from tcell_agent.appsensor.injections_matcher import InjectionsMatcher
from tcell_agent.sanitize.sanitize_utils import remove_trailing_slash


LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


class BlockRule(object):
    ACTIONS_TO_RESPONSES = {
        "block_403s": 403
    }

    def __init__(self, ips, rids, injections_matcher, action, exact_blocked_paths, starts_with_blocked_paths):
        self.ips = ips
        self.rids = rids
        self.injections_matcher = injections_matcher
        self.action = action
        self.exact_blocked_paths = exact_blocked_paths
        self.starts_with_blocked_paths = starts_with_blocked_paths

    def resp(self):
        return self.ACTIONS_TO_RESPONSES.get(self.action)

    def should_block(self, meta_data):
        if len(self.exact_blocked_paths) > 0 or len(self.starts_with_blocked_paths) > 0:
            if meta_data.path:
                if meta_data.path in self.exact_blocked_paths:
                    return True

                for blocked_path in self.starts_with_blocked_paths:
                    if meta_data.path.startswith(blocked_path):
                        return True

            return False

        else:
            if self.ips and meta_data.raw_remote_address not in self.ips:
                return False

            if self.rids and meta_data.route_id not in self.rids:
                return False

            return self.injections_matcher.any_matches(meta_data)

    @classmethod
    def from_json(cls, rule_json):
        action = rule_json.get("action", "block_403s")

        if action in cls.ACTIONS_TO_RESPONSES:
            ips = set(rule_json.get("ips", []))
            rids = set(rule_json.get("rids", []))

            exact_blocked_paths = set()
            starts_with_blocked_paths = set()
            for path_predicate in rule_json.get("paths", []):
                if path_predicate.get("exact", None):
                    exact_path = remove_trailing_slash(path_predicate["exact"])
                    exact_blocked_paths.add(exact_path)
                    if len(exact_path) > 1:
                        exact_blocked_paths.add(''.join([exact_path, "/"]))

                elif path_predicate.get("starts_with", None):
                    starts_with_blocked_paths.add(path_predicate["starts_with"])

            if not ips and not rids and len(exact_blocked_paths) == 0 and len(starts_with_blocked_paths) == 0:
                LOGGER.error("Patches Policy block rule cannot be global. Specify either ips and/or route ids or blocked paths")

                return None

            injections_matcher = InjectionsMatcher.from_json(rule_json.get("sensor_matches", {}))

            return BlockRule(ips, rids, injections_matcher, action, exact_blocked_paths, starts_with_blocked_paths)

        else:
            LOGGER.error("Patches Policy action not supported: #{action}")

            return None
