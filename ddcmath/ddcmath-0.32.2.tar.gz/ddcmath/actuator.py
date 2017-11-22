#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 by Christian Tremblay, P.Eng <christian.tremblay@servisys.com>
#
# Licensed under GPLv3, see file LICENSE in this source tree.
from pint import UnitRegistry
u_ = UnitRegistry()

def force_required(area, Nm = True):
    """
    6 force_pound * inch for a 1 square_foot surface
    """
    if area:
        result = ((6 * u_('lbf')).to(u_('newton')) * (u_('inch').to(u_('m')) * area.to(u_('ft^2')).magnitude)).to(u_('Nm'))
        if Nm:
            return result    
        else:        
            return result.to(u_('in_lbf'))    
    else:
        raise ValueError('Provide duct area')


        
    