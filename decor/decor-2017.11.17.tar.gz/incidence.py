#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import numpy as np

# transmission at normal incidence
T_AIR = 0.956
T_FACEPLATE = 0.931
T_PH = 0.765
T_PERP = T_PH/T_AIR
LOG_T_PERP = math.log(T_PERP)
FOUR_PI = 4 * math.pi


def correctFrelonIncidence(wl, res):
    """
    The correction of reflection intensities for incomplete absorption of
    high-energy X-rays in the CCD phosphor
    G. Wu, B. L. Rodrigues and P. Coppens
    J. Appl. Cryst
    Volume 35
    Part 3
    Pages 356-359
    June 2002

    eq 1
    Iperp = Iobs * ( 1 - Tperp ) / ( 1 - exp(ln(Tperp)/cos(alpha)))

    For a perpendicular detector alpha is twotheta
    """

    sinth = wl * res[0] / FOUR_PI
    costth = np.cos(np.arcsin(sinth) * 2)
    cor = res[1:] * (1 - T_PERP) / (1 - np.exp(LOG_T_PERP / costth))
    # noinspection PyUnresolvedReferences
    return np.array((res[0], cor[0], cor[1]))
