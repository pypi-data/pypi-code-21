#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.
from __future__ import division

def relative_error(result, answer):
    """
    Relative error in percent
    """
    if result - answer == 0:
        return 0
    return ((result - answer) / abs(answer) * 100)
    
def abs_relative_error(result, answer):
    """
    Absolute relative error in percent
    """
    return (abs(relative_error(result, answer)))
    