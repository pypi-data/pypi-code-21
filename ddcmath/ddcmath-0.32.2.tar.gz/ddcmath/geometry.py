#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.
from math import pi

def area(width = 0, height = 0, radius = 0):
    if radius:
        return (pi * (radius ** 2))
    elif width and height:
        return (width * height)
    else:
        raise ValueError('Provide width + height OR radius')
    
