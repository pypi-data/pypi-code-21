# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:10:14 2017

@author: mel
"""
#import anypytools
#anypytools.abcutils.run_from_ipython = lambda: False
from anypytools import AnyPyProcess
app = AnyPyProcess()



macrolist = [
    'load "Knee.any"',
    'operation Main.MyStudy.Kinematics',
    'run',
]

app.start_macro(macrolist);