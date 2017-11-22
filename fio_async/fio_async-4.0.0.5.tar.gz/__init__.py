# -*- coding: utf-8 -*-
from trytond.pool import Pool
from .async import Async, task    # noqa
from .mock_result import MockResult  # noqa


def register():
    Pool.register(
        Async,
        module='async', type_='model'
    )
