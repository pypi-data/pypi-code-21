import unittest

from tele.meter import ListMeter


class TestValueMeter(unittest.TestCase):
    def test_add(self):
        meter = ListMeter()
        self.assertListEqual(meter.value(), [])
        meter.add(3)
        meter.add(7)
        self.assertListEqual(meter.value(), [3, 7])

    def test_add_all(self):
        meter = ListMeter()
        self.assertListEqual(meter.value(), [])
        meter.add_all([1, 2])
        meter.add_all([3, 4])
        self.assertListEqual(meter.value(), [1, 2, 3, 4])
