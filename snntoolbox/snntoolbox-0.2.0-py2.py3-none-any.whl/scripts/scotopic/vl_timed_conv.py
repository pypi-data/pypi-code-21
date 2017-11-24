
import numpy as np
import scipy
import matcompat

# if available import pylab (from matlibplot)
try:
    import matplotlib.pylab as plt
except ImportError:
    pass

def vl_timed_conv(direction, res, dzdy, l):

    # Local Variables: ppp_I, direction, miniN, ppp_N, res, l, N, x, dzdy, nout
    # Function calls: reshape, bsxfun, vl_timed_conv, length, vl_nnconv, ndims, size
    #% res = vl_timed_conv(direction, res, dzdy, l)
    #% (c) 2016 Bo Chen
    #% bchen3@caltech.edu
    N = matcompat.size((res.x), 4.)
    ppp_N = length((l.PPPArray))
    miniN = matdiv(N, ppp_N)
    nout = matcompat.size((l.weights.cell[1]), 2.)
    _switch_val=direction
    if False: # switch 
        pass
    elif _switch_val == 'forward':
        res.x = vl_nnconv((res.x), (l.weights.cell[0]), np.array([]), 'pad', (l.pad), 'stride', (l.stride), (l.opts.cell[:]))
        for ppp_I in np.arange(1., (ppp_N)+1):
            res.x[:,:,:,int(np.dot(ppp_I-1., miniN)+1.)-1:np.dot(ppp_I, miniN)] = bsxfun(plus, (res.x[:,:,:,int(np.dot(ppp_I-1., miniN)+1.)-1:np.dot(ppp_I, miniN)]), np.reshape((l.weights.cell[1,int(ppp_I)-1,:]()), 1., 1., nout))
            
    elif _switch_val == 'backward':
        #% the following implementation is justified by tests/testGradConv.m
    
    return [res]