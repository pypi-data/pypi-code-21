from future.utils import iteritems

from tcell_agent.appsensor.params import \
    GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM, URI_PARAM, HTTP_HEADER_PARAM
from tcell_agent.appsensor.rules import rule_manager


class InjectionAttempt(object):
    def __init__(self, type_of_param, detection_point, vuln_results):
        self.type_of_param = type_of_param
        self.param_name = vuln_results["param"]
        self.param_value = vuln_results["value"]
        self.pattern = vuln_results["pattern"]
        self.detection_point = detection_point


class InjectionSensor(object):
    def __init__(self, dp, policy_json=None):
        self.enabled = False
        self.dp = dp  # the name of the sensor as it appears sensors dict of the rules json
        self.exclude_headers = False
        self.exclude_forms = False
        self.exclude_cookies = False
        self.exclusions = {}
        self.active_pattern_ids = set()
        self.v1_compatability_enabled = False
        self.excluded_route_ids = set()

        if policy_json is not None:
            self.enabled = policy_json.get("enabled", False)
            self.exclude_headers = policy_json.get("exclude_headers", False)
            self.exclude_forms = policy_json.get("exclude_forms", False)
            self.exclude_cookies = policy_json.get("exclude_cookies", False)
            self.v1_compatability_enabled = policy_json.get("v1_compatability_enabled", False)
            self.excluded_route_ids = set(policy_json.get("exclude_routes", []))
            self.active_pattern_ids = set(policy_json.get("patterns", []))

            for common_word, locations in iteritems(policy_json.get("exclusions", {})):
                self.exclusions[common_word] = set(locations)

    def get_ruleset(self):
        return rule_manager.get_ruleset_for(self.dp)

    def applicable_for_param_type(self, param_type):  # pylint: disable=unused-argument
        return True

    def find_vulnerability(self, param_name, param_value):
        rules = self.get_ruleset()
        if rules:
            return rules.check_violation(param_name, param_value, self.active_pattern_ids,
                                         self.v1_compatability_enabled)

        return None

    def get_injection_attempt(self, type_of_param, appsensor_meta, param_name, param_value):
        if not self.enabled:
            return False

        if appsensor_meta.route_id in self.excluded_route_ids:
            return False

        if self.exclude_forms and type_of_param in (GET_PARAM, POST_PARAM, JSON_PARAM, URI_PARAM):
            return False

        if self.exclude_cookies and COOKIE_PARAM == type_of_param:
            return False

        if self.exclude_headers and HTTP_HEADER_PARAM == type_of_param:
            return False

        vuln_results = self.find_vulnerability(param_name, param_value)

        if vuln_results:
            return InjectionAttempt(type_of_param, self.dp, vuln_results)
        else:
            return False
