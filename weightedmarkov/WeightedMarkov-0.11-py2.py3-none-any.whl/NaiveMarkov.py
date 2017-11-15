import random
import itertools as it
import cvxopt
from cvxopt import matrix, solvers
from fractions import Fraction
from copy import deepcopy
from collections import defaultdict
from numpy import unique

'''These classes are only meant to work with integer strings '''
class NaiveMarkov:
    """An nth-Order Markov Chain class with some lexical processing elements."""
    def __init__(self, delim, order, n=10000):
        """Initialized with a delimiting character (usually a space) and the order of the Markov chain."""
        self.states = {}
        self.delim = delim
        self.max = n
        if order > 0:
            self.order = order
        else:
            raise Exception('Markov Chain order cannot be negative or zero.')

    # Must provide classes encoded by 0, 1, 2 etc
    def Freq(s1, s2 = None, numClasses=None):
        if len(s1) <= 0:
            return None;

        if (s2 is None):
            s2 = s1[1:]

        numClasses = numClasses if numClasses else max(max(s1), max(s2))+1
        F=np.zeros((numClasses, numClasses))
        for z in zip(s2,s1):
            F[(z)] += 1

        F=np.matrix(F)
        P=F.copy();
        P = P/P.sum(axis=0)
        return F, P
    
    def GetTokens(self, sample):
        if (type(sample) == str ):
            tokens = sample.split(self.delim)
        else:
            tokens = sample;
            
        return tokens;

    def fit(self, sample):
        prev = tuple(['' for i in range(self.order)])
        tokens = self.GetTokens(sample)
        self.tokens = tokens;
        
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
        #print("{}:{}:{} ".format(Xt, ri, len(self.states[Xt])-1), end='')
        t = self.states[Xt][ri]
        Xt1 = t; #t[len(t)-1]
        
        return Xt1;
    
    def Predict(self, Xt=None, n=None):
        ret= [] if Xt is None else [Xt[-1]]
        #print ("HHH=>", ret)
        for i in range(self.max):
            c = self.NextState(Xt);
            ret.append(c[-1])
        #print ("HHH=>", ret)
            
        return ret

    def PredictO(self, orig, n=None):
        ret= [orig[j] for j in range(self.order)]
        start = tuple(ret)
        for i in range(len(orig)-self.order):
            start = tuple([orig[j+i] for j in range(self.order)])
            #print(start, end='', sep= ';')
            c = self.NextState(start);
            ret.append(c[-1])
        return ret;


    def Score(a, b, printOut=True, msg=None):
        n=0;
        t=0;
        z = zip(a,b)
        correctClass=defaultdict(int)
        totalClass=defaultdict(int)

        for c in z:
            totalClass[c[0]] += 1;

            if(c[0] == c[1]):
                correctClass[c[0]] += 1;
                t+= 1
            n += 1

        if (printOut):
            print("=======================Metrics : ", msg)
            print("orig=>{}\npred=>{}".format(a[0:80], b[0:80]))
            print("Total %d, correct %d, acc: %3.2f"%(n,t,t/n))
            for i,c in totalClass.items():
                acc = correctClass[i]/c
                print("class: {} total: {}, correct: {}, accuracy: {}".format(i, c, correctClass[i], acc))

        return n, t, totalClass
