from unittest import TestCase

from rup.util import determine_run_number


class TestDermineRunNumber(TestCase):

    def test_2049_is_returned_for_2049_000_lmd_gz(self):
        self.assertEqual(2049, determine_run_number('2049_000.lmd.gz'))

    def test_2050_is_returned_for_2050_000_lmd_gz(self):
        self.assertEqual(2050, determine_run_number('2050_000.lmd.gz'))

    def test_2050_is_returned_for_2050_001_lmd_gz(self):
        self.assertEqual(2050, determine_run_number('2050_001.lmd.gz'))

    def test_2050_is_returned_for_2050_001_lmd_gz_with_path(self):
        self.assertEqual(2050, determine_run_number('/tmp/2050_001.lmd.gz'))

    def test_2050_is_returned_for_2050_001_lmd_gz_in_root(self):
        self.assertEqual(2050, determine_run_number('/2050_001.lmd.gz'))

    def test_2050_is_returned_for_2050_001_lmd_gz_nested_multiple_times(self):
        self.assertEqual(2050, determine_run_number('/tmp/test/2050_001.lmd.gz'))

    def test_2050_is_returned_for_2050_rup_yml(self):
        self.assertEqual(2050, determine_run_number('/tmp/test/2050_rup.yml'))
