#!/usr/bin/env janus-submit.sh

import numpy as np
import time, sys
import ctypes
import bobo.app
import bobo.util
import sklearn.cross_validation

########### A few small functions
class OneVsRestModel:
    """
    Contains the learned OVR model parameters
    """

    def __init__(self, W, b):
        self.W = W
        self.b = b

def params_to_tuple(params):
    "convert param block to tuple (suitable as key in a hash table) " 
    if params == None: return None
    return tuple(sorted(params.items()))

def train_one_vs_rest_svm(labels, # an N-length array of feature labels
                          features,
                          eval_freq = 5,
                          n_epoch = 10,
                          verbose = 2,
                          n_thread = 48,
                          _lambda = 1e-7,
                          beta = 10,
                          eta0 = 0,
                          bias_term = 0.001,
                          stop_valid_threshold = -0.02,
                          temperature = 1.0,
                          topk = 1,
                          n_folds = 10):
    """jsgd-61 parallel One-vs-Rest SVM SGD training"""

    # jsgd-61 library
    svm = bobo.app.loadlibrary('jsgd-61')

    kf = sklearn.cross_validation.KFold(len(labels),n_folds=n_folds,shuffle=True)
    folds = [(train,test) for (train,test) in kf]

    # just train/test on the first fold, to speed things up...
    (train,test) = folds[0]
    Ltrain = np.ascontiguousarray(labels[train].astype(np.int32), dtype=np.int32)
    Ltest = np.ascontiguousarray(labels[test].astype(np.int32), dtype=np.int32)
    Xtrain = np.ascontiguousarray(features[train,:].astype(np.float32), dtype=np.float32)
    Xtest = np.ascontiguousarray(features[test,:].astype(np.float32), dtype=np.float32)

    # Preallocate output buffer
    K = len(np.unique(Ltrain))
    (N,D) = Xtrain.shape
    best_accuracy = np.zeros((1,),dtype=np.float32)
    best_epoch = np.zeros((1,),dtype=np.int32)
    W = np.ascontiguousarray(np.zeros((K,D),dtype=np.float32), dtype=np.float32)
    b = np.ascontiguousarray(np.zeros((1,K),dtype=np.float32).squeeze(), dtype=np.float32)
    svm.lib.one_vs_rest_train(ctypes.c_int(K), # number of class labels
                              Ltrain.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), # label for each feature
                              Xtrain.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), # features
                              ctypes.c_int(D), # dimension of each feature
                              ctypes.c_int(N), # number of features
                              Ltest.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), # label for each validation feature
                              Xtest.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), # validation features
                              ctypes.c_int(len(Ltest)), # number of validation features
                              ctypes.c_int(eval_freq), # evaluate accuracy every eval_freq epochs
                              ctypes.c_int(n_epoch), # the number of training epochs
                              ctypes.c_int(verbose), # the verbosity for debug output
                              ctypes.c_int(n_thread), # the number of threads
                              ctypes.c_float(_lambda), # learning rate?
                              ctypes.c_int(beta), # number of negatives to sample per training vector
                              ctypes.c_float(eta0), # intial value of the gradient step
                              ctypes.c_float(bias_term), # this term is appended to each training vector
                              ctypes.c_float(stop_valid_threshold), # stop if the accuracy is lower than the accuracy at the previous evaluation + this much
                              ctypes.c_float(temperature), # inverse temperature parameter for Stiff loss
                              ctypes.c_int(topk), # use topk accuracy metric
                              W.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), # output KxD weight matrix
                              b.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                              best_accuracy.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                              best_epoch.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))

    accuracy = best_accuracy[0]
    epoch = best_epoch[0]
    b *= bias_term
    model = OneVsRestModel(W=W,b=b)

    print 'OVR model has top-%d accuracy %.3f' % (topk,accuracy)

    return (model, accuracy, epoch)

class CrossvalOptimization:
    """
    Optimizes the parameters _lambda bias_term eta0 beta using
    cross-validation. First call the constructor, adjust optimization
    parameters and call optimize(), which returns the set of optimal
    parameters it could find.
    """

    def __init__(self, Xtrain, Ltrain, topk, n_folds, verbose):

        # maximum number of epochs we are willing to perform
        self.max_epoch = 100

        # frequency of evaluations
        self.eval_freq = 5

        # topk accuracy metric
        self.topk = max(1,topk)

        # verbosity
        self.verbose = max(0,verbose)

        # num folds
        self.n_folds = max(2,n_folds)

        # starting point for optimization (also specifies which parameters
        # should be considered for optimization)
        self.init_point = {
            '_lambda': 1e-4, 
            'bias_term': 0.1, 
            'eta0': 0.1, 
            'beta': 2,
            "temperature":1}

        # consider all starting points that are within 5% of best seen so far 
        self.score_tol = 0.05

        # this tolerance decreases by this ratio at each iteration
        self.score_tol_factor = 0.5 

        self.Xtrain = Xtrain
        self.Ltrain = Ltrain

        self.nclass = max(self.Ltrain) + 1

        pow10range = [ 10**i for i in range(-8,8) ]

        # ranges for parameters in init_point
        self.ranges = {
            '_lambda': [0.0] + pow10range,
            'bias_term': [0.0] + pow10range,
            'eta0': pow10range,
            'beta': [b for b in [2,5,10,20,50,100,200,500] if b < self.nclass], 
            'temperature': pow10range}

        # all params can be changed after constructor

    def eval_params(self, params):
        import pdb
        if params is None:
            pdb.set_trace()
        kw = params.copy()
        (model,accuracy,epoch) = train_one_vs_rest_svm(
            features=self.Xtrain,
            labels=self.Ltrain,
            eval_freq = self.eval_freq,
            n_epoch = self.max_epoch,
            verbose = self.verbose,
            topk = self.topk,
            n_folds = self.n_folds,
            **kw)
        return (model,accuracy,epoch)

    def params_step(self, name, pm):
        " step parameter no in direction pm "
        new_params = self.params.copy()
        if name == None and pm == 0:
            return new_params
        curval = self.params[name]
        r = self.ranges[name]
        i = r.index(curval)
        try: 
            new_params[name] = r[i + pm]
            return new_params
        except IndexError:
            return None

    def do_exp(self, (pname, pm)):
        # perform experiment if it is not in cache
        params_i = self.params_step(pname, pm)
        if params_i is None:
            return (None, 0.0, 0.0)

        k = params_to_tuple(params_i)
        if k in self.cache:
            (model,best_accuracy,best_epoch) = self.cache[k]
        else: 
            (model,best_accuracy,best_epoch) = self.eval_params(params_i)
            self.cache[k] = (model,best_accuracy,best_epoch)

        return (model,best_accuracy,best_epoch)

    def optimize(self):
        self.nclass = int(max(self.Ltrain) + 1)

        # cache for previous results
        self.cache = dict()

        # best score so far
        best_accuracy = 0.0
        best_epoch = 0.0
        best_model = None

        t0 = time.time()
        it = 0

        queue = [(0, 1, self.init_point)]

        while queue:

            # pop the best configuration from queue
            score_p, epoch_p, self.params = queue.pop()

            print "============ iteration %d (%.1f s): %s" % (
                it, time.time() - t0, self.params)
            print "baseline score %.3f, epoch %.1f, remaining queue %d (score > %.3f)"  % (
                score_p * 100, epoch_p, len(queue), (best_accuracy - self.score_tol) * 100)

            # extend in all directions
            todo = [(pname, pm)
                    for pname in self.params
                    for pm in -1, 1]

            if it == 0:
                # add the baseline, which has not been evaluated so far
                todo = [(None, 0)] + todo

            # filter out configurations that have been visited already
            todo = [(pname, pm) for (pname, pm) in todo if
                    params_to_tuple(self.params_step(pname, pm)) not in self.cache]

            # perform all experiments
            for (pname, pm) in todo:
                (model,accuracy,epoch) = self.do_exp((pname,pm))

                params_i = self.params_step(pname, pm)

                # no score for this point (may be invalid)
                if accuracy == None: continue

                print "  %s, accuracy = %.3f, epoch = %.1f]" % (params_i,accuracy,epoch)

                if accuracy >= best_accuracy:
                    # we found a better score!
                    print "  keep"
                    if accuracy > best_accuracy:
                        best_op = []
                        best_accuracy = accuracy
                        best_epoch = epoch
                        best_model = model

                        fname = 'best_ovr_model.pkl'
                        print 'saving best OVR model to %s' % fname
                        bobo.util.save(best_model,fname)

                    best_op.append(params_i)

                # add this new point to queue
                queue.append((accuracy, epoch, params_i))

                sys.stdout.flush()

            # strip too low scores from queue 
            queue = [(accuracy, epoch, k) for accuracy, epoch, k in queue if accuracy > best_accuracy - self.score_tol]

            # sorted by increasing scores (best one is last)
            queue.sort()

            it += 1
            self.score_tol *= self.score_tol_factor


        print "best params found: score %.3f, epoch %.1f" % ((best_accuracy * 100),best_epoch)
        for params in best_op: 
            print params

        return (best_op,best_model)


if __name__ == '__main__':

    if True:
        topk = 1
        xclass = np.array([(0,0),(-1,0),(0,1),(0,-1),(1,0)],dtype=np.float32)
        nclasses = xclass.shape[0]

        nsamples=10000
        cov = 0.16*np.eye(2,dtype=np.float32)
        Xtrain = []
        Ltrain = []
        for c in xrange(0,nclasses):
            Xtrain.append(np.random.multivariate_normal(xclass[c,:],cov,nsamples))
            Ltrain.append(c+np.zeros((nsamples,),dtype=np.int32))

        Xtrain = np.concatenate(Xtrain,axis=0)
        Ltrain = np.concatenate(Ltrain,axis=0)

    else:
        topk = 5
        fvs = bobo.util.load('training_fvs.pkl')
        (_,categories,fvs) = zip(*fvs)
        label_dict = dict()
        for category in categories:
            if category not in label_dict:
                label_dict[category] = len(label_dict)

        Xtrain = np.concatenate([np.reshape(fv,(1,len(fv))) for fv in fvs],axis=0)
        Ltrain = np.zeros((len(categories),),dtype=np.int32)
        for i in xrange(0,len(Ltrain)):
            Ltrain[i] = label_dict[categories[i]]

    n, d = Xtrain.shape
    nclass = len(np.unique(Ltrain))

    print "train size %d vectors in %dD, %d classes " % (n, d, nclass)

    co = CrossvalOptimization(Xtrain = Xtrain,
                              Ltrain = Ltrain,
                              topk = topk,
                              n_folds = 10,
                              verbose = 1)
    (_,best_model) = co.optimize()

    fname = 'best_ovr_model.pkl'
    print 'saving best OVR model to %s' % fname
    bobo.util.save(best_model,fname)
