# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>, 
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""Statistical tools"""

from sequana.lazy import numpy as np
from sequana.lazy import pandas as pd


__all__ = ["moving_average", "evenness"] 


def moving_average(data, n):
    """Compute moving average

    :param n: window's size (odd or even).

    ::

        >>> from sequana.stats import moving_average as ma
        >>> ma([1,1,1,1,3,3,3,3], 4)
        array([ 1. ,  1.5,  2. ,  2.5,  3. ])

    .. note:: the final vector does not have the same size as the input 
        vector. 


    """
    ret = np.cumsum(data, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    ma = ret[n - 1:] / n
    return ma


def evenness(data):
    """Return Evenness of the coverage

    :Reference: Konrad Oexle, Journal of Human Genetics 2016, Evaulation 
        of the evenness score in NGS.

    work before or after normalisation but lead to different results.
    """
    coverage = pd.Series(data)

    coverage = coverage.dropna()

    C = float(round(coverage.mean()))
    D2 = coverage[coverage<=C]
    if len(D2) == 0:
        return 1
    else:
        
        return 1. - (len(D2) - sum(D2) / C) / len(coverage)
