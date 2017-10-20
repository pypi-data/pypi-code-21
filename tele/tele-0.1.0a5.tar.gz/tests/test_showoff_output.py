import unittest

from tele import Telemetry
from tele.meter import ValueMeter
import tele.showoff
import tele.showoff.views
import pyshowoff


class DummyClient(pyshowoff.Client):
    def __init__(self, callback=None):
        super().__init__('dummy:1337', True)
        self.callback = callback

    def request(self, method, path, data=None):
        if self.callback:
            return self.callback(method, path, data)
        return None


class TestShowoffOutput(unittest.TestCase):
    def test_normal(self):
        patch_data = {}

        def callback(method, path, data):
            if method.lower() == 'post' and path == '/api/v2/frames':
                return {'data': {'id': '100'}}
            if method.lower() == 'patch' and path == '/api/v2/frames/100':
                patch_data.clear()
                patch_data.update(data)
                return None
            self.fail('unexpected Showoff request')

        client = DummyClient(callback)
        notebook = pyshowoff.Notebook(client, 1)
        t = Telemetry({'val': ValueMeter()})
        t['val'].set_value(42)
        t.sink(tele.showoff.Conf(notebook), [
            tele.showoff.views.Text(['val'], 'Value'),
        ])
        t.step()
        self.assertEqual(patch_data, {'data': {
            'id': '100',
            'type': 'frames',
            'attributes': {'type': 'text', 'content': {'body': '42'}}
        }})

    def test_histogram(self):
        patch_data = {}

        def callback(method, path, data):
            if method.lower() == 'post' and path == '/api/v2/frames':
                return {'data': {'id': '100'}}
            if method.lower() == 'patch' and path == '/api/v2/frames/100':
                patch_data.clear()
                patch_data.update(data)
                return None
            self.fail('unexpected Showoff request')

        client = DummyClient(callback)
        notebook = pyshowoff.Notebook(client, 1)
        t = Telemetry({'val': ValueMeter()})
        t['val'].set_value([0.9, 1, 1.1, 2, 2, 3, 4, 3])
        t.sink(tele.showoff.Conf(notebook), [
            tele.showoff.views.Histogram(['val'], 'Value', bins=10, extent=[0, 10], x_title='val'),
        ])
        t.step()
        self.assertEqual(patch_data, {'data': {
            'id': '100',
            'type': 'frames',
            'attributes': {
                'type': 'vegalite',
                'content': {'body': {
                    'width': 420,
                    'height': 250,
                    'data': {'values': [
                        {'x': '0.50', 'y': 1}, {'x': '1.50', 'y': 2}, {'x': '2.50', 'y': 2},
                        {'x': '3.50', 'y': 2}, {'x': '4.50', 'y': 1}, {'x': '5.50', 'y': 0},
                        {'x': '6.50', 'y': 0}, {'x': '7.50', 'y': 0}, {'x': '8.50', 'y': 0},
                        {'x': '9.50', 'y': 0}
                    ]},
                    'mark': 'bar',
                    'encoding': {
                        'x': {'field': 'x', 'type': 'ordinal', 'sort': False,
                              'axis': {'title': 'val', 'labelAngle': 0}},
                        'y': {'field': 'y', 'type': 'quantitative', 'axis': {'title': 'count'}}
                    }
                }}
            }
        }})
