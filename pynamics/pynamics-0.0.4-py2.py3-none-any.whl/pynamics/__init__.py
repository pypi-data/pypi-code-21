# -*- coding: utf-8 -*-

#class FrameVector(object):
#    def __init__(self,frame,coords):
#        self.frame = frame
#        self.coords = sympy.Matrix(coords)
#    def __str__(self):
#        return str(self.frame)+str(self.coords[:])
#    def __repr__(self):
#        return str(self)

import sympy
import sys

ZERO = sympy.Number(0)
dimension = 3
script_mode = True

import logging
logger = logging.getLogger('pynamics')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    fh = logging.FileHandler('pynamics.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

systemname = '_system'

def PynamicsObject(object):
    
    def __init__(self,name):
        addself(self,name)

def addself(self,name,modulename='__main__',override = False):
    if script_mode or override:
        module = sys.modules[modulename]
        if hasattr(module,name):
            raise NameError('variable '+name+' exists')
        else:
            setattr(module, name, self)

def get_system():
    module = sys.modules['__main__']
    return getattr(module,systemname)
            
import time
time0 = 0
def tic():
    global time0
    time0 = time.time()
def toc():
    logger.info(str(time.time()-time0))

#t = sympy.Symbol('t')
