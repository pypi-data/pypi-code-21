#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.
import math

def cfm2ls(cfm = 0):
    return cfm * 0.4719475
    
def ls2cfm(ls = 0):
    return ls / 0.4719475

def calculate_kfactor(area = 0, flow = 0, diff_pressure = 0, si=True, offset = 0.02):
    """
    This function is able to compute the pickup_gain or K-Factor
    for PCV controllers or other VAV controllers using a similar
    equation.
    
    gain = ((AREA * 4005) / FLOW)**2 * velocity_pressure
    velocity is calculated with an error (offset or 0.005inwc)
    
    area : in square meters
    flow : by the flow hood
    diff_pressure : read by the controller transmitter on the pitot
    si = if True, use SI conversions.
    offset : typical correction of pressure reading
    
    """
    if si:
        area = area/0.0929
        flow = flow / 0.4720
        velocity_pressure = (diff_pressure-(offset*diff_pressure))/248.84
    else:
        velocity_pressure = diff_pressure-(offset*diff_pressure)
    
    return round(((area * 4005/flow)**2) * velocity_pressure,2)

def calculate_flow(area, k_factor, diff_pressure, si=True, offset=0.02):
    """
    This function is able to compute the pickup_gain or K-Factor
    for PCV controllers or other VAV controllers using a similar
    equation.
    
    gain = ((AREA * 4005) / FLOW)**2 * velocity_pressure
    velocity is calculated with an error (offset or 0.005inwc)
    
    area : in square meters
    k_factor : SA-KFACTOR
    diff_pressure : read by the controller transmitter on the pitot
    si = if True, use SI conversions.
    offset : typical correction of pressure reading
    
    """
    if si:
        area = area/0.0929
        velocity_pressure = (diff_pressure-(offset*diff_pressure))/248.84
    else:
        velocity_pressure = diff_pressure-(offset*diff_pressure)
    
    flow = ((area * 4005) * math.sqrt(velocity_pressure/k_factor))
    flow = flow * 0.4720
    return round(flow,2)