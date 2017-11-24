
import numpy as np
import scipy
import matcompat

# if available import pylab (from matlibplot)
try:
    import matplotlib.pylab as plt
except ImportError:
    pass

def estimate_PPP(dataset, rawim, model, PPPArray):

    # Local Variables: a, PPP_I, PPPArray, nc, dataset, nx, ny, PPP, logPPP, rawim, model, N, input_size
    # Function calls: sort, reshape, all, prod, log, max, nan, median, convn, estimate_PPP, round_to_targets, ones, exist, ismember, double, mean, exp, squeeze, strcmp, size
    #% [PPP, PPP_I]= estimate_PPP(dataset, rawim, model, PPPArray)
    #% estimate PPP from raw images rawim.
    #% if PPPArray is provided, enforce the PPP estimates to be
    #% elements within PPPArray, and provide the index PPP_I
    #% (c) 2016 Bo Chen
    #% bchen3@caltech.edu
    [nx, ny, nc, N] = matcompat.size(rawim)
    _switch_val=dataset
    if False: # switch 
        pass
    elif _switch_val == 'mnist':
        input_size = np.array(np.hstack((28., 28., 1.)))
        _switch_val=model.type
        if False: # switch 
            pass
        elif _switch_val == 'max_resp':
            a = np.squeeze(matcompat.max(matcompat.max(convn(rawim, (model.convParam.weights)), np.array([]), 1.), np.array([]), 2.))
            PPP = model.predFunc[int((model.predParam))-1,int(np.double(a))-1]
        elif _switch_val == 'avg_prc':
            a = np.sort(np.reshape(rawim, np.prod(input_size), np.array([])), 1., 'descend')
            a = np.mean(a[0:model.topK,:])
            PPP = model.predFunc[int((model.predParam))-1,int(np.double(a))-1]
        
    elif _switch_val == 'cifar':
        input_size = np.array(np.hstack((32., 32., 3.)))
        _switch_val=model.type
        if False: # switch 
            pass
        elif _switch_val == 'gray_max_resp':
            a = np.squeeze(matcompat.max(matcompat.max(convn(rawim, (model.convParam.weights)), np.array([]), 1.), np.array([]), 2.))
            PPP = model.predFunc[int((model.predParam))-1,int(np.double(a))-1]
        elif _switch_val == 'resp_prc':
            a = convn(rawim, matdiv(np.ones((model.S), (model.S), 1., 1.), model.S**2.))
            a = np.sort(np.reshape(a, np.array([]), N), 1., 'descend')
            a = np.median(a[0:model.topK,:])
            PPP = model.predFunc[int((model.predParam))-1,int(np.double(a))-1]
        
    
    PPP_I = np.nan(N, 1.)
    if exist('PPPArray', 'var'):
        [logPPP, PPP_I] = round_to_targets(np.log(PPP), np.log(PPPArray))
        PPP = np.exp(logPPP)
    
    
    return [PPP, PPP_I]