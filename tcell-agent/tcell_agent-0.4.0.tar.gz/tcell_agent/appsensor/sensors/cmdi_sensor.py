from tcell_agent.appsensor.params import COOKIE_PARAM
from tcell_agent.appsensor.sensors.injection_sensor import InjectionSensor


class CmdiSensor(InjectionSensor):
    def __init__(self, policy_json=None):
        super(CmdiSensor, self).__init__("cmdi", policy_json)

    def applicable_for_param_type(self, param_type):
        return COOKIE_PARAM is not param_type
