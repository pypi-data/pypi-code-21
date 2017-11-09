import logging

import qzig.value as value

LOGGER = logging.getLogger(__name__)


class Temperature(value.Value):
    _bind = True
    _attribute = 0

    def _init(self):
        self.data = {
            ":type": "urn:seluxit:xml:bastard:value-1.1",
            ":id": self.uuid,
            "name": "Temperature",
            "permission": value.ValuePermission.READ_ONLY,
            "type": "Temperature",
            "number": value.ValueNumberType(),
            "status": value.ValueStatus.OK,
            "state": []
        }
        self.data["number"].min = -273.15
        self.data["number"].max = 327.67
        self.data["number"].step = 0.01
        self.data["number"].unit = "celcius"

    def handle_report(self, attribute, data):
        if attribute == self._attribute:
            return (data / 100)
