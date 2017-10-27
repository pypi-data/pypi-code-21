from tcell_agent.appsensor.params import COOKIE_PARAM
from tcell_agent.appsensor.rules import rule_manager
from tcell_agent.appsensor.sensors.injection_sensor import InjectionSensor


class NullbyteSensor(InjectionSensor):
    def __init__(self, policy_json=None):
        super(NullbyteSensor, self).__init__("null", policy_json)

    def get_ruleset(self):
        return rule_manager.get_ruleset_for("nullbyte")

    def applicable_for_param_type(self, param_type):
        return COOKIE_PARAM is not param_type
