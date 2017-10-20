import tele.meter
import torchnet.meter
import tele.console.views


class Sink(tele.Sink):
    def write(self, step_num, rendered):
        print('[{:4d}] '.format(step_num) + ', '.join(rendered))


class Conf(tele.Conf):
    def make_auto_view(self, meter_name, meter):
        if isinstance(meter, torchnet.meter.AverageValueMeter) \
                or isinstance(meter, torchnet.meter.TimeMeter) \
                or isinstance(meter, tele.meter.ValueMeter):
            return tele.console.views.KeyValue([meter_name])
        return None

    def build(self, view_list):
        cell_list = [view.build() for view in view_list]
        return Sink(cell_list)
