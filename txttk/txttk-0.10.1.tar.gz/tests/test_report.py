#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function) #, unicode_literals)
from builtins import *

"""
test_report
----------------------------------

Tests for `report` module.
"""

import unittest

from txttk import report

class TestReport(unittest.TestCase):

    def setUp(self):
        tp = [1, 2, 3, 4, 5, 6, 7]
        fp = [-2, -1, 0]
        fn = [8, 9, 10]
        title = 'testing'
        self.report = report.Report(tp, fp, fn, title)

    def test_zero(self):
        the_report = report.Report()
        self.assertEqual(str(the_report), 'Report<P0.000 R0.000 F0.000 None>')

    def test_precision(self):
        precision = self.report.precision()
        wanted = 7/10
        self.assertEqual(precision, wanted)

    def test_recall(self):
        recall = self.report.recall()
        wanted = 7/10
        self.assertEqual(recall, wanted)

    def test_f1(self):
        f1 = self.report.f1()
        wanted = 7/10
        self.assertEqual(f1, wanted)

    def test_str(self):
        wanted = "Report<P0.700 R0.700 F0.700 'testing'>"
        self.assertEqual(str(self.report), wanted )

    def test_from_reports(self):
        reports = [
            report.Report([1, 2, 3], [-2], [8], 'test1'),
            report.Report([4, 5], [-1], [9], 'test2'),
            report.Report([6, 7], [0], [10], 'test3'),
        ]
        meta_report = report.Report.from_reports(reports, 'testing')
        self.assertEqual(str(meta_report), str(self.report))

    def test_split(self):
        reports = [
            report.Report([1, 2, 3], [-2], [8], 'test1'),
            report.Report([4, 5], [-1], [9], 'test2'),
            report.Report([6, 7], [0], [10], 'test3'),
        ]
        meta_report = report.Report.from_reports(reports, 'testing')
        results = meta_report.split()
        result_surfaces = {str(result) for result in results}
        wanted_surfaces = {str(result) for result in reports}
        self.assertEqual(result_surfaces, wanted_surfaces)

    def test_split_error(self):
        the_report = report.Report(['ab', 'cd', 'ef'], ['gh'], ['ij'], 'test')
        with self.assertRaises(AssertionError):
            the_report.split()

    def test_from_scale(self):
        scale_report = report.Report.from_scale(gold_number=10, precision=0.7, recall=0.7, title='testing')
        self.assertEqual(str(scale_report), str(self.report))
