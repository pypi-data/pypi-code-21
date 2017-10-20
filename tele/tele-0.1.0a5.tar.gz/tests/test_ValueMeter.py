import unittest

from tele.meter import ValueMeter


class TestValueMeter(unittest.TestCase):
    def test_set_value(self):
        meter = ValueMeter()
        self.assertIsNone(meter.value())
        meter.set_value(42)
        self.assertEqual(meter.value(), 42)
