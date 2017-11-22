#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.
from .temperature import delta_c2f, delta_f2c
from .airflow import cfm2ls

def heating_cfm(kw = None, btu = None, delta_t_celsius = None, delta_t_farenheit = None):
    if not kw:
        raise ValueError('kw must not be 0')
    if delta_t_farenheit and delta_t_celsius:
        raise ValueError('Provide only one value, in celsius or farenheit')
    if delta_t_farenheit == 0 or delta_t_celsius == 0 or (not delta_t_farenheit and not delta_t_celsius):
        raise ValueError('Delta T must be greater than 0')
    if delta_t_celsius:
        return heating_cfm(kw = kw, btu = None, delta_t_farenheit = delta_c2f(delta_t_celsius))
    else:
        return (kw * 3412 / (delta_t_farenheit * 1.08))


def heating_ls(kw = None, btu = None, delta_t_celsius = None, delta_t_farenheit = None):
    cfm = heating_cfm(kw = kw, 
                      btu = btu, 
                      delta_t_celsius = delta_t_celsius, 
                      delta_t_farenheit = delta_t_farenheit)
    return cfm2ls(cfm)
    
def heating_kw(cfm = None, ls = None, delta_t_celsius = None, delta_t_farenheit = None):
    if not cfm and not ls:
        raise ValueError('Provide at least one flow (CFM or LS)')
    if ls:
        cfm = ls / 0.4719475
    if delta_t_farenheit:
        kw = delta_t_farenheit * cfm * 1.08 / 3412
    elif delta_t_celsius:
        kw = delta_c2f(delta_t_celsius) * cfm * 1.08 / 3412
    return kw
    
def heating_deltaT_f(cfm = None, ls = None, kw = None):
    if not cfm and not ls:
        raise ValueError('Provide at least one flow (CFM or LS)')
    if ls:
        cfm = ls / 0.4719475
    if kw:
        delta_t_farenheit = kw / (cfm * 1.08 / 3412)
    else:
        raise ValueError('Provide at kW')

    return delta_t_farenheit
    
def heating_deltaT_c(cfm = None, ls = None, kw = None):
    if not cfm and not ls:
        raise ValueError('Provide at least one flow (CFM or LS)')
    if ls:
        cfm = ls / 0.4719475
    if kw:
        delta_t_farenheit = kw / (cfm * 1.08 / 3412)
    else:
        raise ValueError('Provide at kW')

    return delta_f2c(delta_t_farenheit)