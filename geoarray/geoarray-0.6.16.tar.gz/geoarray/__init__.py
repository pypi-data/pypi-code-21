# -*- coding: utf-8 -*-

import os
if 'MPLBACKEND' not in os.environ:
    os.environ['MPLBACKEND'] = 'Agg'

from .baseclasses import GeoArray  # noqa: E402
from .masks import BadDataMask  # noqa: E402
from .masks import NoDataMask  # noqa: E402
from .masks import CloudMask  # noqa: E402


__author__ = """Daniel Scheffler"""
__email__ = 'danschef@gfz-potsdam.de'
__version__ = '0.6.16'
__versionalias__ = 'v20171019.01'
__all__ = ['GeoArray',
           'BadDataMask',
           'NoDataMask',
           'CloudMask'
           ]
