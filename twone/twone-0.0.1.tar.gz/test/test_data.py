import unittest

import pandas as pd

from twone.container import Container


class ClassDataTestCase(unittest.TestCase):
    """Test for data/data.py"""

    def test_instantiate(self):
        weather_death_data = pd.read_csv('../interpolated_data.csv')
        data = Container(data_frame=weather_death_data)
        self.assertIsInstance(data, Container)

    def test_test(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
