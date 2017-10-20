import tele
import torchnet.meter


class _KeyValueCell(tele.Cell):
    def render(self, step_num, meters):
        meter_name = self.meter_names[0]
        meter = meters[0]
        value = meter.value()
        if isinstance(meter, torchnet.meter.AverageValueMeter):
            (mean, std) = value
            value_str = u'{:0.4f}\u00b1{:0.4f}'.format(mean, std)
        elif isinstance(value, float):
            value_str = '{:0.4f}'.format(value)
        else:
            value_str = str(value)
        return '='.join([meter_name, value_str])


class KeyValue(tele.View):
    def build(self):
        return _KeyValueCell(self.meter_names)
