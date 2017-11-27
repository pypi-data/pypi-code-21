#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from collections import defaultdict, namedtuple
from fractions import Fraction

TagBox = namedtuple('TagBox', 'content tag')

def pack_boxes(list_of_content, tag):
    return [TagBox(content, tag) for content in list_of_content]

def get_numerator(ratio, max_denominator):
    fraction = Fraction.from_float(ratio).limit_denominator(max_denominator)
    return int(fraction.numerator * max_denominator / fraction.denominator)

def get_denominator(ratio, max_numerator):
    return get_numerator(1/ratio, max_numerator)

class Report:
    """
    Holding the results of experiment, presenting the precision, recall,
    f1 score of the experiment.
    """
    def __init__(self, tp=[], fp=[], fn=[], title=None):
        """
        tp: the ture positive items
        fp: the false positive items
        fn: the false negative items
        title: the title of this report
        """
        self.tp = pack_boxes(tp, title)
        self.fp = pack_boxes(fp, title)
        self.fn = pack_boxes(fn, title)
        self.title = title

    def precision(self):
        try:
            return float(len(self.tp)) / (len(self.tp) + len(self.fp))
        except ZeroDivisionError:
            return 0.0

    def recall(self):
        try:
            return float(len(self.tp)) / (len(self.tp) + len(self.fn))
        except ZeroDivisionError:
            return 0.0

    def f1(self):
        r = self.recall()
        p = self.precision()
        try:
            return float(2 * r * p) / (r + p)
        except ZeroDivisionError:
            return 0.0

    def __repr__(self):
        r = self.recall()
        p = self.precision()
        f = self.f1()
        syntax = 'Report<P{p:.3f} R{r:.3f} F{f:.3f} {t!r}>'
        return syntax.format(p=p, r=r, f=f, t=self.title)

    @classmethod
    def from_reports(cls, reports, title):
        meta_report = cls([], [], [], title)
        for report in reports:
            meta_report.tp.extend(pack_boxes(report.tp, title))
            meta_report.fp.extend(pack_boxes(report.fp, title))
            meta_report.fn.extend(pack_boxes(report.fn, title))
        return meta_report

    def split(self):
        title2report = defaultdict(Report)
        try:
            for tagbox, _ in self.tp:
                title2report[tagbox.tag].tp.append(tagbox.content)
            for tagbox, _ in self.fp:
                title2report[tagbox.tag].fp.append(tagbox.content)
            for tagbox, _ in self.fn:
                title2report[tagbox.tag].fn.append(tagbox.content)
            for title, report in title2report.items():
                report.title = title
        except AttributeError:
            raise AssertionError('The report cannot be split')
        return list(title2report.values())

    @classmethod
    def from_scale(cls, gold_number, precision, recall, title):
        tp_count = get_numerator(recall, gold_number)
        positive_count = get_denominator(precision, tp_count)
        fp_count = positive_count - tp_count
        fn_count = gold_number - tp_count
        scale_report = cls(['tp'] * tp_count,
                           ['fp'] * fp_count,
                           ['fn'] * fn_count,
                           title)
        return scale_report
