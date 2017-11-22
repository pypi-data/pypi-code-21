#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.
from __future__ import division

from ddcmath.temperature import c2f

# Thanks Joel Bender for the formulae
def enthalpy(oat = None, rh = None, celsius = True):
    if rh < 0 or rh > 100:
        raise ValueError('rh must be between 0-100%')
    if celsius:
        oat = c2f(oat)
    return 0.24*oat + 0.0010242*rh*(2.7182818**(oat / 28.116)) * (13.147+0.0055*oat)