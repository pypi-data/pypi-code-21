import re


class AppSensorRulePattern(object):
    def __init__(self, pattern_id, pattern_regex, enabled=True):
        self.pattern_id = pattern_id
        self.pattern_regex = pattern_regex
        self.enabled = enabled


class AppSensorRuleSet(object):
    def __init__(self):
        self.safe_pattern = None
        self.patterns = []

    def check_violation(self, param_name, param_value, active_pattern_ids, v1_compatability_enabled):
        try:
            if param_value is None or (self.safe_pattern and self.safe_pattern.search(param_value)):
                return None
            for pattern in self.patterns:
                if pattern is None or pattern.enabled is False:
                    continue

                if v1_compatability_enabled or pattern.pattern_id in active_pattern_ids:
                    match = pattern.pattern_regex.search(param_value)
                    if match:
                        return {"param": param_name, "value": param_value, "pattern": pattern.pattern_id}
        except:
            pass

        return None

    def add_pattern_from_dict(self, rule_dict):
        if rule_dict is None:
            return

        pattern_id = rule_dict.get("id")
        pattern = rule_dict.get("python", None)
        if pattern is None:
            pattern = rule_dict.get("common", None)
        elif pattern == "disabled":
            return

        if pattern_id is None or pattern is None:
            return

        pattern_regex = re.compile(pattern, flags=re.IGNORECASE | re.S | re.M)
        enabled = rule_dict.get("enabled", True)

        rule_pattern = AppSensorRulePattern(pattern_id, pattern_regex, enabled)
        self.add_pattern(rule_pattern)

    def set_safe_pattern_from_string(self, safe_pattern_str):
        if safe_pattern_str is not None:
            self.safe_pattern = re.compile(safe_pattern_str, flags=re.IGNORECASE | re.S | re.M)

    def add_pattern(self, pattern):
        self.patterns.append(pattern)
