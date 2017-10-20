import tele
from io import StringIO, BytesIO
import base64
from PIL import Image
import torchvision.transforms as transforms
import torchnet.meter
import numpy as np


class Cell(tele.Cell):
    def __init__(self, meter_names, frame):
        super().__init__(meter_names)
        self.frame = frame

    def render(self, step_num, meters):
        raise NotImplementedError()


class View(tele.View):
    def __init__(self, meter_names, frame_title='untitled'):
        super().__init__(meter_names)
        self.frame_title = frame_title

    def build(self, frame):
        raise NotImplementedError()


class _TextCell(Cell):
    def render(self, step_num, meters):
        stream = StringIO()
        for meter in meters:
            stream.write(str(meter.value()))
        self.frame.text(stream.getvalue())


class Text(View):
    def build(self, frame):
        return _TextCell(self.meter_names, frame)


class _InspectCell(Cell):
    def __init__(self, meter_names, frame, flatten):
        super().__init__(meter_names, frame)
        self.flatten = flatten

    def render(self, step_num, meters):
        items = []
        for meter_name, meter in zip(self.meter_names, meters):
            value = meter.value()
            if self.flatten and hasattr(value, 'items'):
                for k, v in value.items():
                    key = meter_name + '.' + k
                    str_value = str(v)
                    items.append((key, str_value))
            else:
                key = meter_name
                str_value = str(value)
                items.append((key, str_value))

        stream = StringIO()
        stream.write('<table style="width: 100%; table-layout: fixed;">')
        for key, str_value in items:
            stream.write('<tr><td>')
            stream.write(key)
            stream.write('</td></tr><tr><td><pre>')
            stream.write(str_value)
            stream.write('</pre></td></tr>')
        stream.write('</table>')
        self.frame.html(stream.getvalue())


class Inspect(View):
    def __init__(self, meter_names, frame_title, flatten=False):
        super().__init__(meter_names, frame_title)
        self.flatten = flatten

    def build(self, frame):
        return _InspectCell(self.meter_names, frame, self.flatten)


class _GraphvizCell(Cell):
    def render(self, step_num, meters):
        meter = meters[0]
        value = meter.value()
        svg_bytes = value.pipe(format='svg')
        b64_str = base64.b64encode(svg_bytes).decode('utf-8')
        img_tag_template = '<img style="width: 100%;" src=data:image/svg+xml;base64,{}>'
        self.frame.html(img_tag_template.format(b64_str))


class Graphviz(View):
    def build(self, frame):
        return _GraphvizCell(self.meter_names, frame)


class _LineGraphCell(Cell):
    def __init__(self, meter_names, frame):
        super().__init__(meter_names, frame)
        self.xs = []
        self.yss = None

    def render(self, step_num, meters):
        if self.yss is None:
            self.yss = [[] for _ in meters]
        self.xs.append(step_num)
        series_names = []
        for i, meter in enumerate(meters):
            value = meter.value()
            if isinstance(meter, torchnet.meter.AverageValueMeter):
                value = value[0]
            self.yss[i].append(value)
            series_names.append(self.meter_names[i])
        self.frame.line_graph(self.xs, self.yss, series_names=series_names)


class LineGraph(View):
    def build(self, frame):
        return _LineGraphCell(self.meter_names, frame)


class _HistogramCell(Cell):
    def __init__(self, meter_names, frame, bins, extent, x_title):
        super().__init__(meter_names, frame)
        self.bins = bins
        self.extent = extent
        self.x_title = x_title

    def render(self, step_num, meters):
        vals = []
        for meter in meters:
            vals.extend(meter.value())
        ys, xs = np.histogram(vals, bins=self.bins, range=self.extent)

        xs = [float(x1 + x2) / 2 for x1, x2 in zip(xs, xs[1:])]

        values = [{'x': '{:0.2f}'.format(x), 'y': int(y)} for x, y in zip(xs, ys)]

        spec = {
            'width': 420,
            'height': 250,
            'data': {'values': values},
            'mark': 'bar',
            'encoding': {
                'x': {
                    'field': 'x',
                    'type': 'ordinal',
                    'sort': False,
                    'axis': {'title': self.x_title, 'labelAngle': 0},
                },
                'y': {
                    'field': 'y',
                    'type': 'quantitative',
                    'axis': {'title': 'count'},
                }
            }
        }
        self.frame.vegalite(spec)


class Histogram(View):
    def __init__(self, meter_names, frame_title, bins=10, extent=None, x_title='x'):
        super().__init__(meter_names, frame_title)
        self.bins = bins
        self.extent = extent
        self.x_title = x_title

    def build(self, frame):
        return _HistogramCell(self.meter_names, frame, self.bins, self.extent, self.x_title)


class _ImageCell(Cell):
    def __init__(self, meter_names, frame, images_per_row):
        super().__init__(meter_names, frame)
        self.images_per_row = images_per_row

    def render(self, step_num, meters):
        images = []
        value = None
        for meter in meters:
            value = meter.value()
            if isinstance(value, list):
                images.extend(value)
            else:
                images.append(value)

        if self.images_per_row is None:
            img_tag_template = '<img src=data:image/png;base64,{}>'
        else:
            width = '{:0.2f}%'.format(100 / self.images_per_row)
            img_tag_template = '<img style="width: ' + width + ';" src=data:image/png;base64,{}>'

        stream = StringIO()
        stream.write(
            '<div style="background-image: linear-gradient(45deg, #808080 25%, transparent 25%), '
            + 'linear-gradient(-45deg, #808080 25%, transparent 25%), '
            + 'linear-gradient(45deg, transparent 75%, #808080 75%), '
            + 'linear-gradient(-45deg, transparent 75%, #808080 75%); '
            + 'background-size: 20px 20px; '
            + 'background-position: 0 0, 0 10px, 10px -10px, -10px 0px;">')
        for img in images:
            if not isinstance(img, Image.Image):
                img = transforms.ToPILImage()(value.cpu())
            buf = BytesIO()
            img.save(buf, format='PNG')
            b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
            stream.write(img_tag_template.format(b64_str))
        stream.write('</div>')
        self.frame.html(stream.getvalue())


class Images(View):
    def __init__(self, meter_names, frame_title, images_per_row=None):
        super().__init__(meter_names, frame_title)
        self.images_per_row = images_per_row

    def build(self, frame):
        return _ImageCell(self.meter_names, frame, self.images_per_row)
