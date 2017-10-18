# -*- coding: utf-8 -*-

from trytond.pool import Pool
from .memo import PimMemo
from .category import Category
from .notereport import ReportOdt


def register():
    Pool.register(
        Category,
        PimMemo,
        module='pim_memos', type_='model')
    Pool.register(
        ReportOdt,
        module='pim_memos', type_='report')
