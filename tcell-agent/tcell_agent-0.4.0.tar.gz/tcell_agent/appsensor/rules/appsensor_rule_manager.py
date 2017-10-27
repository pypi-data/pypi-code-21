import json
from .appsensor_rule_set import AppSensorRuleSet


class AppSensorRuleManager(object):
    def __init__(self, filename=None):
        self.rule_info = {}
        if (filename):
            self.load_rules_file(filename)

    def load_rules_file(self, filename):
        self.rule_info.clear()
        with open(filename, 'r') as f:
            rules_from_file = json.loads(f.read())
            rule_types = rules_from_file.get("sensors")
            if (rule_types):
                for rule_type in rule_types:
                    rule_info_json = rule_types[rule_type]

                    rule_set = AppSensorRuleSet()
                    rule_set.set_safe_pattern_from_string(rule_info_json.get("safe_pattern"))

                    for rule_pattern_dict in rule_info_json.get("patterns", []):
                        rule_set.add_pattern_from_dict(rule_pattern_dict)
                    self.rule_info[rule_type] = rule_set

    def get_ruleset_for(self, rule_type):
        return self.rule_info.get(rule_type)
