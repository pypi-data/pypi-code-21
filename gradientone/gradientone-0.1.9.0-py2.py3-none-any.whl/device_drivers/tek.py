from ivi.tektronix import tektronixMDO4104


class GOMDO4104(tektronixMDO4104):
    """
    Gradient One's customized tektronic MDO4104 object
    """
    def __init__(self, visa_address="TCPIP::192.168.1.108::INSTR"):
        super(tektronixMDO4104, self).__init__(visa_address)
        self.rf = RFCommands(self, 1)


class RFCommands:
    def __init__(self, scope_reference, channel):
        self.scope = scope_reference
        self.scope._write("select:rf_normal " + str(channel))
        self.amplitude = self.AmplitudeCommands(self.scope, 1)

    class AmplitudeCommands:
        def __init__(self, scope_reference, channel):
            self.scope = scope_reference
            self.scope._write("select:rf_amplitude " + str(channel))

        @property
        def vertical_position(self):
            return float(
                self.scope._write("rf:rf_amplitude:vertical:position?"))

        @vertical_position.setter
        def vertical_position(self, new_val):
            self.scope._write(
                "rf:rf_amplitude:vertical:position " + str(new_val))

        @property
        def vertical_scale(self):
            return float(self.scope._write("rf:rf_amplitude:vertical:scale?"))

        @vertical_scale.setter
        def vertical_scale(self, new_val):
            self.scope._write("rf:rf_amplitude:vertical:scale " + str(new_val))

    @property
    def frequency(self):
        return float(self.scope._ask("rf:frequency?"))

    @frequency.setter
    def frequency(self, new_val):
        self.scope._write("rf:frequency " + str(new_val))

    @property
    def span(self):
        return float(self.scope._ask("rf:span?"))

    @span.setter
    def span(self, new_val):
        self.scope._write("rf:span " + str(new_val))

    @property
    def reflevel(self):
        return float(self.scope._ask("rf:reflevel?"))

    @reflevel.setter
    def reflevel(self, new_val):
        self.scope._write("rf:reflevel " + str(new_val))

    @property
    def scale(self):
        return float(self.scope._ask("rf:scale?"))

    @scale.setter
    def scale(self, new_val):
        self.scope._write("rf:scale " + str(new_val))