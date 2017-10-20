class Telemetry():
    def __init__(self, meters):
        self.meters = meters
        self.sinks = []
        self.step_num = 0

    def sink(self, conf, view_list=None, auto_view=False):
        if view_list is None:
            view_list = []
        if auto_view:
            meters_with_views = []
            for view in view_list:
                meters_with_views.extend(view.meter_names)
            meters_without_views = set(self.meters.keys()) - set(meters_with_views)
            for meter_name in sorted(meters_without_views):
                view = conf.make_auto_view(meter_name, self.meters[meter_name])
                if view is not None:
                    view_list.append(view)
        sink = conf.build(view_list)
        self.sinks.append(sink)
        return sink

    def step(self):
        for sink in self.sinks:
            rendered = sink.render_all(self.step_num, self.meters)
            sink.write(self.step_num, rendered)
        for meter_name, meter in self.meters.items():
            if not hasattr(meter, 'skip_reset') or not meter.skip_reset:
                meter.reset()
        self.step_num += 1

    def __getitem__(self, meter_name):
        return self.meters[meter_name]


# Descendants of this class are for internal use. They are built by their
# corresponding Conf.
class Sink:
    def __init__(self, cell_list):
        self.cell_list = cell_list

    def render_all(self, step_num, meters):
        rendered = []
        for cell in self.cell_list:
            cell_meters = [meters[mn] for mn in cell.meter_names]
            rendered.append(cell.render(step_num, cell_meters))
        return rendered

    def write(self, step_num, rendered):
        pass


# Descendants of this class are part of the public API, and are used to
# configure an output.
class Conf:
    def make_auto_view(self, meter_name, meter):
        return None

    def build(self, view_list):
        raise NotImplementedError()


# Descendants of this class are for internal use. They are built by
# their corresponding View.
class Cell:
    def __init__(self, meter_names):
        self.meter_names = meter_names

    def render(self, step_num, meters):
        raise NotImplementedError()


# Descendants of this class are part of the public API, and are used to
# specify how groups of one or more meters are displayed.
class View:
    def __init__(self, meter_names):
        self.meter_names = meter_names

    def build(self, *args):
        raise NotImplementedError()
