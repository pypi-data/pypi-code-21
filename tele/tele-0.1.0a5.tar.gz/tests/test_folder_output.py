import unittest

from tele import Telemetry
from tele.meter import ValueMeter
import tele.folder
import tele.folder.views
from tempfile import TemporaryDirectory
import os
import json


class TestFolderOutput(unittest.TestCase):
    def test_normal(self):
        t = Telemetry({'val': ValueMeter()})
        t['val'].set_value(42)
        with TemporaryDirectory() as tmpdir:
            t.sink(tele.folder.Conf(tmpdir), [
                tele.folder.views.JSON(['val'], 'test.json')
            ])
            t.step()

            file_path = os.path.join(tmpdir, 'test.json')
            self.assertTrue(os.path.isfile(file_path), '{} is not a file'.format(file_path))
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data, {'val': 42})
