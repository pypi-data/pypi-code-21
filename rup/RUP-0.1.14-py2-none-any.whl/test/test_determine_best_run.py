from datetime import *
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzlocal
from unittest import TestCase

from rup.collector import RunFiles
from rup.rundb import RunDbEntry

from rup.processor import determine_best_match


class TestDermineBestRun(TestCase):

    @staticmethod
    def date_to_str(date):
        return date.strftime("%a, %d %b %Y %H:%M:%S %z")

    NOW = datetime.now(tz=tzlocal())
    STR_NOW = NOW.strftime("%a, %d %b %Y %H:%M:%S %z")


    def test_best_match_of_empty_is_none(self):
        run = RunFiles(2000)
        run.append_file("/tmp/t.lmd.gz")
        self.assertIsNone(determine_best_match([], run))

    def test_best_match_to_single_entry_now_is_that(self):
        run = RunFiles(2000)
        run.append_file("/tmp/t.lmd.gz")

        entry = RunDbEntry("TestExp", "IFA4", 2000, self.STR_NOW, 2000, 1)

        self.assertEqual(entry, determine_best_match([entry], run))

    def test_best_match_to_single_entry_with_wrong_number_is_none(self):
        run = RunFiles(2000)
        run.append_file("/tmp/t.lmd.gz")

        entry = RunDbEntry("TestExp", "IFA4", 1, self.STR_NOW, 2000, 1)

        self.assertIsNone(determine_best_match([entry], run))

    def test_entries_older_than_one_day_is_ignored(self):
        run = RunFiles(2000)
        run.append_file("/tmp/t.lmd.gz")

        time = self.date_to_str(self.NOW - relativedelta(days=1, minutes=1))

        entry = RunDbEntry("TestExp", "IFA4", 2000, time, 2000, 1)

        self.assertIsNone(determine_best_match([entry], run))

    def test_if_to_few_files_found_none_is_returned(self):
        run = RunFiles(2000)
        run.append_file("/tmp/t.lmd.gz")

        entry = RunDbEntry("TestExp", "IFA4", 2000, self.STR_NOW, 2000, 2)

        self.assertIsNone(determine_best_match([entry], run))

