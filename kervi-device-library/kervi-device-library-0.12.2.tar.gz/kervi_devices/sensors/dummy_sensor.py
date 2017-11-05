from kervi.hal import SensorDeviceDriver

class DummySensorDeviceDriver(SensorDeviceDriver):
    def __init__(self):
        SensorDeviceDriver.__init__(self)
        self.value = 0
        self.delta = 4

    def read_value(self):
        self.value += self.delta
        if self.value == 100:
            self.delta *= -1
        if self.value == 0:
            self.delta *= -1
        return self.value

    @property
    def type(self):
        return "counter"

    @property
    def unit(self):
        return "%"


class DummyMultiDimSensorDeviceDriver(SensorDeviceDriver):
    def __init__(self):
        self.value = 0
        self.delta = 4

    def read_value(self):
        self.value += self.delta
        if self.value == 100:
            self.delta *= -1
        if self.value == 0:
            self.delta *= -1
        return [self.value, self.value, self.value]

    @property
    def dimensions(self):
        return 3

    @property
    def dimension_labels(self):
        return ["heading", "pitch", "roll"]

    @property
    def type(self):
        return "position"

    @property
    def unit(self):
        return "degree"