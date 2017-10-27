from tcell_agent.libinjection import is_sqli
from tcell_agent.appsensor.sensors.injection_sensor import InjectionSensor


class SqliSensor(InjectionSensor):
    def __init__(self, policy_json=None):
        super(SqliSensor, self).__init__("sqli", policy_json)

        self.libinjection = False

        if policy_json is not None:
            self.libinjection = policy_json.get("libinjection", False)

    def find_vulnerability(self, param_name, param_value):
        if param_value:
            param_type = str(type(param_value))
            if param_type.startswith("<type 'unicode'"):
                param_value = param_value.encode('utf-8')

            if self.libinjection and is_sqli(param_value) == 1:
                return {"param": param_name, "value": param_value, "pattern": "li"}

            return InjectionSensor.find_vulnerability(self, param_name, param_value)

        else:
            return False
