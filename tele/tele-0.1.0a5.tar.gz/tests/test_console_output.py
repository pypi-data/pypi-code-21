import unittest

from tele import Telemetry
from tele.meter import ValueMeter
import tele.console
import tele.console.views

from tests import captured_output


class TestConsoleOutput(unittest.TestCase):
    def test_normal(self):
        t = Telemetry({'val': ValueMeter()})
        t['val'].set_value(42)
        t.sink(tele.console.Conf(), [
            tele.console.views.KeyValue(['val'])
        ])
        with captured_output() as (out, err):
            t.step()
            self.assertEqual(out.getvalue().strip(), '[   0] val=42')

    def test_auto_view(self):
        t = Telemetry({'val': ValueMeter()})
        t['val'].set_value(42)
        t.sink(tele.console.Conf(), auto_view=True)
        with captured_output() as (out, err):
            t.step()
            self.assertEqual(out.getvalue().strip(), '[   0] val=42')
