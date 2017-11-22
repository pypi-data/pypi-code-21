#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.
from .temperature import delta_c2f, delta_f2c
from .airflow import cfm2ls

NMLBINRATIO = 8.850745792

def nm_2_inlb(nm = None):   
    return nm * NMLBINRATIO;
    
def inlb_2_nm(inlb = None):   
    return inlb / NMLBINRATIO;