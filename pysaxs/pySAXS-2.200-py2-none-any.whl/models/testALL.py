# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 10:41:17 2016

@author: tache
script for testing all the models
"""
import pySAXS
from pylab import *
from pySAXS.models import listOfModels
lm=listOfModels.listOfModels()
ion()
for  key in lm:
    r=raw_input(lm[key] +'?')
    
    if r=='':
        mm=getattr(pySAXS.models,lm[key])
        m=mm()
        cla()
        plot(m.q,m.getIntensity())
        loglog()
        grid()
        show()
