from tcell_agent.appsensor.params import POST_PARAM, JSON_PARAM
from tcell_agent.appsensor.sensors.injection_sensor import InjectionSensor


class RetrSensor(InjectionSensor):
    def __init__(self, policy_json=None):
        super(RetrSensor, self).__init__("retr", policy_json)

    def applicable_for_param_type(self, param_type):
        return POST_PARAM is not param_type and JSON_PARAM is not param_type
