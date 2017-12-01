import random
import itertools as it
import cvxopt
from cvxopt import matrix, solvers
from fractions import Fraction
from copy import deepcopy
from collections import defaultdict
from numpy import unique
from WeightedMarkov.MarkovBase import *;

class NaiveMarkov(MarkovBase):
    '''These classes are only meant to work with integer strings '''
    def __init__(self, X=[], nStates=0, order= 1, n=10000, delim=' '):
        super(NaiveMarkov, self).__init__(X=X, nStates=nStates, order=order)
        self.max = 10000
        self.delim = ' '
        self.states= {}
        
    def GetTokens(self, sample):
        if (type(sample) == str ):
            tokens = sample.split(self.delim)
        else:
            tokens = sample;
            
        return tokens;

    def fit(self, sample=None):
        prev = tuple(['' for i in range(self.order)])
        tokens = self.GetTokens(sample)
        self.tokens = tokens;
        self.X = [tokens]
        
        self.max = len(tokens)
        for t in tokens:
            if not prev in self.states:
                self.states[prev] = []
            curr = prev[1:] + (t,)
            self.states[prev].append(curr)
            prev = curr
            
    def NextState(self, Xt=None, n=None):
        if Xt is None or not Xt in self.states.keys():
            Xt = tuple(['' for i in range(self.order)])
        ri = random.randint(0, len(self.states[Xt])-1)
        t = self.states[Xt][ri]
        Xt1 = t; 
        return Xt1;
    
    def Predict(self, Xt=None, n=None):
        ret= [] if Xt is None else [Xt[-1]]
        for i in range(self.max):
            c = self.NextState(Xt);
            ret.append(c[-1])
            
        return ret

    def PredictFromList(self, orig, n=None):
        ret= [orig[j] for j in range(self.order)]
        start = tuple(ret)
        for i in range(len(orig)-self.order):
            start = tuple([orig[j+i] for j in range(self.order)])
            c = self.NextState(start);
            ret.append(c[-1])
        return ret;
