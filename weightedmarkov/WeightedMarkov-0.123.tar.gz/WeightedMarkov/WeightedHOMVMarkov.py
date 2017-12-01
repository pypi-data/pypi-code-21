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
import numbers
from WeightedMarkov.MarkovBase import *;

# All series must have same number of states
#

class WeightedHOMVMarkov(MarkovBase):
    """An higher order multi variate Markov Chain"""
    def __init__(self, X= None, nStates=None, order=1):
        assert order > 0, "order cannot be negative"
        super(WeightedHOMVMarkov, self).__init__(X=X, nStates=nStates, order=order)
        
        s = len(X)
        self.c = [0 for _ in range(s)];
        self.A = [0 for _ in range(s)];
        self.b = [0 for _ in range(s)];
        self.p = [0 for _ in range(s)];
        self.sol = [0 for _ in range(s)];

    def fit(self, X=None):
        fS={}
        pS={}
        xHats=[]

        if ( X is None):
            X = self.X;
        
        for x in X:
            xHats.append(self.computeXHat(x) )

        for i,j in it.product(range(len(X)), repeat=2):
            for o in range(self.order):
                a1 = X[j]
                a2 = X[i][o+1:]
                    
                idx =(i+1, j+1, o+1)
                F= self.Freq(a1, a2)
                
                fS[(idx)] = F[0]
                pS[(idx)] = F[1]
                
                
        self.fS = fS; self.pS = pS; self. xHats = xHats;
        
        return fS, pS, xHats;
    

    def computeXHat(self, s):
        xHat=np.zeros(self.nStates)
        t=pd.Series(s).value_counts() 
        for i,j in t.items():    
            xHat[i] =j
        ret = xHat/xHat.sum()

        ret = np.array([ret]).T

        return ret;

    #Display the matrix
    def Matdisplay(self,*Ms, names=None, useFractions=False, display=False):
        s = ""
        if (names is None):
            names = ["" for i in range(len(Ms)) ]
        for i, m in enumerate(Ms):
            if str(type(np.array(m).flat[0])).find('str') < 0:
                useFrac = useFractions
            else:
                useFrac = False
            
            s+= self.M(m=m, name=names[i], useFrac=useFrac, call_display=False, showdim=False);

        if (display):
            display(Math(s))
        return (s)

    def MdisplayPS(self,useFractions=True):
        s=""
        g = ["\hat{{P_{}}}^{{{}}}".format(k[2], (k[0],k[1])) for k in sorted(self.pS.keys())]
        v = [_[1] for _ in sorted(self.pS.items())]
        s += self.Matdisplay(*v, names=g, useFractions=useFractions) + "\\\\"
        return (s)

    def MdisplayXHat(self,useFractions=True):
        s=""
        g = ["\hat{{x}}_{}".format(i+1) for i in range(len(self.xHats))]
        s+= self.Matdisplay(*self.xHats, names=g, useFractions=useFractions)
        
        return (s)

    def Mdisplay(self,fS, pS, xHats, useFractions=True):
        g = ["\hat{{F_{}}}^{{{}}}".format(k[2], (k[0],k[1])) for k in sorted(fS.keys())]
        v = [_[1] for _ in sorted(fS.items())]
        s = self.Matdisplay(*v, names=g, useFractions=useFractions) + "\\\\"
        

        g = ["\hat{{P_{}}}^{{{}}}".format(k[2], (k[0],k[1])) for k in sorted(pS.keys())]
        v = [_[1] for _ in sorted(pS.items())]
        s += self.Matdisplay(*v, names=g, useFractions=useFractions) + "\\\\"

        g = ["\hat{{x}}_{}".format(i+1) for i in range(len(xHats))]
        s+= self.Matdisplay(*xHats, names=g, useFractions=useFractions)

        display(Math(s))
        return (s)

    def Dump(self):
        s = self.Mdisplay(self.fS, self.pS, self.xHats)
        return s;
    
        
    def DisplayCAb(self, j = 0):
        s=len(self.X)
        n= self.nStates
        ls = list(it.product(range(s), repeat=2))
        numParams = s* self.order

        t=''
        for i in range(numParams):
            t += '\lambda_{}+'.format(i)
        t = t[0:-1] + " <= +1"
        t += "\n-"+ t.replace('+', '-')
        for _ in range(numParams):
            t += '\n\lambda_{} >= 0'.format(_)

        cons = len(self.A[j]) - (numParams+self.order+1)
        
        for _ in range( cons ):
            t += '\n->' 
            
        t += '\nw >= 0'    

        dd = np.array([_ for _ in t.split('\n')])
        for tt in t.split('\n'):
            pass
            #print (tt, end='')
            #display(Math(tt))

        dd =np.matrix([dd]).T

        cAb = [np.matrix(self.c[j]),np.matrix(self.A[j]),np.matrix([self.b[j]]).T, dd]
        s = self.Matdisplay(*cAb, names="c A b description".split(), useFractions=True)
        display(Math(s))
    
    def PrepareMatrices(self):
        for i in range(len(self.X)):
            self.PrepareMatrices1(i)
            
        return self.c[0], self.A[0], self.b[0];
    
    def PrepareMatrices1(self, j=0):
        s=len(self.X)
        n= self.nStates
        ls = list(it.product(range(s), repeat=2))
        numParams = s* self.order

        # =>> Compute C because it is easy
        c= [0. for _ in range(numParams+1)]
        c[-1] = 1

        A=[]
        b=[]
        #-1. ---- Sum of \lambdas = 1

        for i in range(s):
            b += [1,-1]

            c2=[1 for _ in range(numParams+1)]
            c2[-1]= 0;  

            A += c2;
            A += [_ * -1 for _ in c2];
            break;

        A = np.array(A).reshape(int(len(A)/(numParams+1)),numParams+1, order='C')

        #-2. ---- Prepare -> lambda's must be non negative
        for i in range(numParams):
            b += [0]

            c2=[0 for _ in range(numParams+1)]
            c2[i]= -1;  
            A = vstack((A, c2))

        #-3. ---- Prepare -> X^j's are constrained
    
        x= self.xHats[j].flatten().tolist()
        x1 = [-1 * _ for _ in x]
        b += x1
        b += x

        cm=np.zeros((n*(numParams+1)))
        cm=cm.reshape(n,numParams+1)
        cm[:,-1]=1
        for k in range(s):        
            for h in range(self.order):        
                pd1 = self.pS.get((j+1,k+1,h+1) )
                xh1 = self.xHats[k]
                bb1 = pd1 * xh1
                
                colIndex = k*self.order+h
                cm[:, colIndex] = bb1.flatten()

        A = vstack((A, cm*-1))

        cm[:,-1]=-1
        A = vstack((A, cm))
        A = vstack((A, [_*-1 for _ in c]))
        b.append(0)


        # =======> REMOVE the DUPLICATE ROWS
        aa = deepcopy(A)
        aa1 = deepcopy(aa[0:numParams])
        bb1 = deepcopy(b[0:numParams])

        for i in range(numParams, len(aa) -1 ):
            for ii,kk in enumerate(aa[i][:-1]):
                aa[i][ii] = round( aa[i][ii] , 12)

            ne= False;
            for ii,kk in enumerate(aa[i][:-1]):
                if ( aa[i][0] != aa[i][ii] ):
                    ne = True;
            if (not ne): continue;

            aa1 = np.append(aa1, [aa[i]])
            bb1.append(b[i])

        bb1.append(b[-1])
        aa1 = np.append(aa1, [aa[-1]])
        aa1 = aa1.reshape( int(len(aa1)/A.shape[1]), A.shape[1])
        
        self.c[j] = c;
        self.A[j] = aa1;
        self.b[j] = bb1;
        return self.c[j], self.A[j], self.b[j];
    
    def Solve(self, showProgress=True, solver=None):
        for i in range(len(self.c)):
            c1=matrix(np.matrix(self.c[i]).astype(np.double) ).T
            A1=matrix(np.matrix(self.A[i]).astype(np.double) )
            b1=matrix(np.matrix(self.b[i]).astype(np.double) ).T

            solvers.options['show_progress'] = showProgress
            
            sol = solvers.lp(c1, A1, b1)
            
            ##=> Set 0 if the value is too low and 1 if if it is close to 1
            ##=> We do this for efficient computation of predictions.
            for ii, f in enumerate(sol['x']):
                if ( f < 0.00001):
                    sol['x'][ii] = 0
                    continue;
                if ( abs(1-f) <0.00001):
                    sol['x'][ii] = 1
                    
            self.sol[i] = sol
            self.p[i]   = sol['x']
            
        return self.sol;
    
    def DumpSolution(self):
        ps=list(it.product(range(self.order), repeat=2))
        slt=r'''
        \begin{equation}
        \begin{aligned}
        '''; #begin{flalign*}'
        for i,s in enumerate(self.sol):
            slt+= "x^{{({})}}_{{r+1}} &= ".format(i+1)
            for ii, f in enumerate(np.array([_ for _ in self.sol[i]['x'].T][:-1]) ):
                if ( f < 0.00001):
                    continue;
                pi = ii % self.order
                pp = (i+1, ps[ii][0]+1)
                #  print("{} : {:.4f}".format(pp, f), end=' ' )
                if ( abs(1-f) <0.00001):
                    f=''
                else:
                    f = str(round(f, 4))
                    
                if( pi == 0):  ri = ''
                else: ri = "-"+str(pi)
                
                
                slt += "{} P_{}^{{{}}} X_{{r{}}}^{{({})}} +" .format(f, pi+1, pp, ri, pp[1])
            slt = slt[:-1];
            slt += r"\\"
        #    print()
        slt+=r'''
        \end{aligned}
        \end{equation}
        '''; #\\end{bmatrix}'

        m='''
        x^{(j)}_{r+1} = \sum_{k=1}^{s}\sum_{h=1}^{n} \lambda^{(h)}_{jk} P^{(jk)}_h x^{(k)}_{r-h+1}, 
        j = 1,2,...s, n = order
        '''
        display(Math(m))
        display(Math(slt))
        
        return slt;

    def makeX(self, c):
        if not ( isinstance( c , numbers.Number) ):
            return c;
        x = [0 for _ in range(self.nStates)]
        x[c]=1
        return np.matrix(x).T;
    
    def Predict(self, Xr, randomized=False):
        ps=list(it.product(range(self.order), repeat=2))
        Xr_1= [None for _ in range(len(self.X))]
        Pr_1= [-1 for _ in range(len(self.X))]

        order = self.order
        for i,s in enumerate(self.sol):
            if (Xr[i] is None):
                continue;
            PXr = None
            
            for ii, lmbda in enumerate(np.array([_ for _ in s['x'].T][:-1]) ):
                if ( lmbda == 0 ):
                    continue;
                pi = ii % order
                xi = ps[ii][0]
                idx=( i+1, xi+1, pi+1)
                #print(f, idx, "X",i)

                if (Xr[xi] is None):
                    PXr = None
                    break;

                if (PXr is None):
                    PXr = lmbda * self.pS[idx] * self.makeX(Xr[xi][pi])
                else:
                    PXr += lmbda * self.pS[idx] * self.makeX(Xr[xi][pi])

            Xr_1[i] = PXr
            Pr_1[i] = -1 if PXr is None else np.argmax(PXr)

        return Xr_1, Pr_1;

    def SelfEval(self, scoreFirstOnly=False, msg=None):
        Xr=[None for _ in range(len(self.X))]
        X = self.X
        order = self.order
        
        for i in range(min([len(c) for c in X]) - order):
            for ii in range(len(Xr)):
                Xr[ii] = list(reversed(X[ii][i:i+order] ))

            Xr_1,pr_1 = self.Predict(Xr)

            if (i==0):
                for j, jj in enumerate(Xr_1):
                    print(j, np.array(jj.flat), pr_1[j], X[j][i+order+1])
                P=pr_1
            else:
                P=np.vstack((P,pr_1))

            #break;

        for i in range(len(X)):
            self.Score(X[i][order:], P[:,i], msg=msg)
            if(scoreFirstOnly):
                break;
            
        return P
    