import random
import itertools as it
import cvxopt
from cvxopt import matrix, solvers
from fractions import Fraction
from copy import deepcopy
from collections import defaultdict
import numpy as np;
from numpy import unique
import pandas as pd;
from numpy import vstack
import re
from IPython.display import display
from IPython.display import display, Math, Latex
from WeightedMarkov.MarkovBase import *;

# Do not use this class -> it is here only for academic demostration purpose
# For all purpose you should use WeightedMVHOMarkov - that is generic for higher order multi variate
#
class WeightedMarkov(MarkovBase):
    """An higher order multi variate Markov Chain"""
    def __init__(self, X= None, nStates=None, order=1):
        assert order > 0, "order cannot be negative"
        super(WeightedMarkov, self).__init__(X=X, nStates=nStates, order=order)

    def fit(self, X=None):
        return self.Compute(X)
        
    def Compute(self, X):
        fS={}
        pS={}
        xHats=[]
        numClasses = self.nStates
        self.numClasses = numClasses

        if ( X is None):
            X = self.X;
            numClasses = self.nStates
            self.numClasses = numClasses
            order = self.order
        
        for x in X:
            xHats.append(self.computeXHat(x) )

        for i in range(self.order):
            a1 = X[0]
            a2 = a1[i+1:]
            F=self.Freq(a1, a2)
            fS[i] = F[0]
            pS[i] = F[1]
        
        self.fS = fS; self.pS = pS; self.xHats = xHats;
        
        return fS, pS, xHats;

    def computeXHat(self, s):
        xHat=np.zeros(self.nStates)
        t=pd.Series(s).value_counts() 
        for i,j in t.items():    
            xHat[i] =j
        ret = xHat/xHat.sum()

        ret = np.array([ret]).T

        return ret;
    #Display thr matrix
    def Matdisplay(self, *M, names=None, useFractions=False, display=False):
        s = ""
        if (names is None):
            names = ["" for i in range(len(M)) ]
        for i, m in enumerate(M):
            if str(type(np.array(m).flat[0])).find('str') < 0:
                useFrac = useFractions
            else:
                useFrac = False

            s+= self.M(m, name=names[i], useFrac=useFrac, call_display=False, showdim=False);

        if (display):
            display(Math(s))
        return (s)
    
    def Mdisplay(self,fS, pS, xHats):
        g = ["\hat{{F}}^{{{}}}".format(_) for _ in sorted(fS.keys())]
        v = [_[1] for _ in sorted(fS.items())]
        s = self.Matdisplay(*v, names=g)

        g = ["\hat{{P}}^{{{}}}".format(_) for _ in sorted(pS.keys())]
        v = [_[1] for _ in sorted(pS.items())]
        s += self.Matdisplay(*v, names=g, useFractions=True)

        g = ["\hat{{x}}_{}".format(i+1) for i in range(len(xHats))]
        s+= self.Matdisplay(*xHats, names=g, useFractions=True)
        
        display(Math(s))
        return (s)

    def Dump(self):
        self.Mdisplay(self.fS, self.pS, self.xHats)
        
        
    def DisplayCAb(self):
        t=''
        for i in range(self.order):
            t += '\lambda_{}+'.format(i)
        t = t[0:-1] + " <= +1"
        t += "\n-"+ t.replace('+', '-')
        for _ in range(self.order):
            t += '\n\lambda_{} >= 0'.format(_)

        for _ in range(self.nStates):
            t += '\n-'
        for _ in range(self.nStates):
            t += '\n+'
        t += '\nw >= 0'    

        dd = np.array([_ for _ in t.split('\n')])
        for tt in t.split('\n'):
            pass
            #print (tt, end='')
            #display(Math(tt))

        dd =np.matrix([dd]).T

        cAb = [np.matrix(self.c),np.matrix(self.A),np.matrix([self.b]).T, dd]
        s = self.Matdisplay(*cAb, names="c A b description".split(), useFractions=True)
        display(Math(s))
    
    def PrepareMatrices(self):
        s=len(self.X)
        n= self.nStates
        ls = list(it.product(range(s), repeat=2))
        numParams = self.order

        numRows = (2*s + numParams + 2*s*n)
        # numRows= 
        # 1. 2*s for sum of lambdas equal to 1 - we need two (1) for >= 1 (2) <= 1 plus
        # 2. lambda)_jk >=0, therefore  -1 * lamda)_jk <= 0 -> 2 for each lambda
        # 3. 2 for each s * numClasses (n) , the set of   lambdas

        #-1. ---- Prepare A
        A=[]
        b=[]

        for i in range(s):
            b += [1,-1]

            c2=[1 for _ in range(numParams+1)]
            c2[-1]= 0;  

            A += c2;
            A += [_ * -1 for _ in c2];

        A = np.array(A).reshape(int(len(A)/(numParams+1)),numParams+1, order='C')

        #-2. ---- Prepare A -> lambda's must be non negative
        for i in range(numParams):
            b += [0]

            c2=[0 for _ in range(numParams+1)]
            c2[i]= -1;  
            A = vstack((A, c2))

        #-3. ---- Prepare A
        i=0

        x= self.xHats[i].flatten().tolist()
        x1 = [-1 * _ for _ in x]
        b += x1
        b += x

        j=np.zeros((n*(numParams+1)))
        j=j.reshape(n,numParams+1)
        j[:,-1]=1
        for k in range(numParams):        
            pd1 = self.pS.get(k)
            xh1 = self.xHats[0]
            bb1 = pd1 * xh1
            j[:,k] = bb1.flatten()

        A = vstack((A, j*-1))
        j[:,-1]=-1
        A = vstack((A, j))

        # =>> Compute C

        c= [0. for _ in range(numParams+1)]
        c[-1] = 1

        A = vstack((A, [_*-1 for _ in c]))
        b.append(0)

        self.c = c;
        self.A = A;
        self.b = b;
        return c,A,b;

    def PrepareMatricesNN(self): #Do not include non negative contraints
        s=len(self.X)
        n= self.nStates
        ls = list(it.product(range(s), repeat=2))
        numParams = self.order

        numRows = (2*s + numParams + 2*s*n)
        # numRows= 
        A=[0 for _ in range(numParams + 1)]
        b=[0]

        #-3. ---- Prepare A
        for i in range(s):
            b += [1,-1]

            c2=[1 for _ in range(numParams+1)]
            c2[-1]= 0;  

            A += c2;
            A += [_ * -1 for _ in c2];

        A = np.array(A).reshape(int(len(A)/(numParams+1)),numParams+1, order='C')

        i=0
        x= self.xHats[i].flatten().tolist()
        x1 = [-1 * _ for _ in x]
        b += x1
        b += x

        j=np.zeros((n*(numParams+1)))
        j=j.reshape(n,numParams+1)
        j[:,-1]=1
        for k in range(numParams):        
            pd1 = self.pS.get(k)
            xh1 = self.xHats[0]
            bb1 = pd1 * xh1
            j[:,k] = bb1.flatten()

        A = vstack((A, j*-1))
        j[:,-1]=-1
        A = vstack((A, j))

        # =>> Compute C

        c= [0. for _ in range(numParams+1)]
        c[-1] = 1

        A = vstack((A, [_*-1 for _ in c]))
        b.append(0)

        self.c = c;
        self.A = A;
        self.b = b;
        return c,A,b;
    
    def Solve(self, showProgress=True, solver=None):
        self.c1=matrix(self.c)
        self.A1=matrix(self.A)
        self.b1=matrix(self.b)
        
        solvers.options['show_progress'] = showProgress
        
        self.sol=solvers.lp(self.c1, self.A1, self.b1,)
        self.p = self.sol['x']

        return self.sol;
    
    def Predict(self, CtIn, randomized=False):
        sol = np.matrix ([0. for i in self.xHats[0]]).T
        Ct = deepcopy(CtIn)
        if ( type(Ct[0]) == list):
            for i in range(len(Ct)):
                Ct[i] = np.matrix(Ct[i]).T
            
        for i in range(self.order):
            Qx =  self.pS[i] * Ct[i]
            Qx1=  Qx * self.p[i]
            sol += Qx1
        self.sol = sol
        
        mm=[i for i in range(self.nStates) if self.sol[i] == max(self.sol)]  # Get all the candidates
        if ( randomized):
            predicted = mm[random.randint(0,len(mm)-1)]
        predicted = mm[0]

        return sol, predicted;