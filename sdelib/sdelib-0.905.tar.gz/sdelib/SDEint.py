import numpy as np

def availableSolvers(problem=None,solverType=None,d=1,m=1):
    '''Method for returning list of available solvers.

    If problem given, it available solvers based on problem.equationType and
    problem.m and problem.d. If problem not given, uses solverType string to
    return available solvers.'''
    if problem is None and solverType is None:
        raise ValueError('Either problem or solverType needs to be an argument')
    wholeItoList = ["itoEM", "itoThetaDM","itoBackwardsEulerDM",
    "itoTheta1M","itoBackwardsEuler1M"
    "itoPlaten","itoMilstein11","itoMilsteinD1"]
    ito11List = ["itoEM", "itoTheta1M","itoBackwardsEuler1M",
    "itoPlaten","itoMilstein11"]
    itoD1List = ["itoEM", "itoThetaDM","itoBackwardsEulerDM",
    "itoPlaten","itoMilsteinD1"]
    itoDMList = ["itoEM", "itoThetaDM","itoBackwardsEulerDM"]

    wholeStratList, wholeComList = [],[]
    if problem is not None:
        if problem.calcType == 'Ito':
            if problem.m == 1 and problem.d == 1:
                if problem.g1 != None:
                    if problem.equationType == 'Autonomous and multiplicative':
                        return ito11List
                    else:
                        return ['itoEM','itoPlaten','itoMilstein11']
                else:
                    if problem.equationType == 'Autonomous and multiplicative':
                        return ito11List[0:-1]
                    else:
                        return ['itoEM','itoPlaten',]
            elif problem.m == 1 and problem.d> 1:
                if problem.g1 != None:
                    if problem.equationType == 'Autonomous and multiplicative':
                        return itoD1List
                    else:
                        return ['itoEM','itoPlaten','itoMilsteinD1']
                else:
                    if problem.equationType == 'Autonomous and multiplicative':
                        return itoD1List[0:-1]
                    else:
                        return ['itoEM','itoPlaten']
            elif problem.m > 1:
                if problem.equationType == 'Autonomous and multiplicative':
                    return itoDMList
                else:
                    return ['itoEM']
            else:
                raise NotImplementedError("Something horrible has happened.")
        elif problem.calcType == 'Stratonovich':
            return stratTup
    else:
        if solverType == 'osIto':
            if d == 1 and m == 1:
                return ito11List
            elif m == 1:
                return itoD1List
            elif d > 1 and m > 1:
                return itoDMList
            else:
                raise NotImplementedError("Something horrible has happened")
        elif solverType == 'osStrat':
            return wholeStratList
        elif solverType == 'comSolver':
            return wholeComList

def getSolver(problem,solverString):
    solvers = availableSolvers(problem=problem)
    if not solverString in solvers:
        raise ValueError("Something horrible has happened")
    if problem.calcType == 'Ito':
        return osIto(problem,solverString = solverString)
    elif problem.calcType == 'Stratonovich':
        return osStrat(problem,solverString = solverString) 

class solution:
    """Used for SDEprob solution dictionary,."""
    def __init__(self, problem, X, solverString):
        self.X, self.solverString, self.p = X, solverString, problem
        problem.addSolution(self)

class SDEsolver:
    """Master class for SDEsolver classes. Used only as parent."""

class osIto(SDEsolver):
    """ Solver class for one-step Ito methods.
    
    Class works by receiving a SDEprob (an SDE with a stored Wiener process 
    matrix) and solving it using a one-step Ito method. Constructor and
    setSolver selects the method to solve the problem. solver is used for
    computing one step using an index i for SDEprob.t. The methods themselves
    thus only have to be specified mathematically in one step, which
    simplifies the process of adding new methods, but makes this slightly
    slower than algorithms which only have to do 1 thing well.
    """    
    def __init__(self, p, solverString=None,printNum = False,theta=0.5):
        """Sets the solver based on solverString"""
        self.printNum = printNum
        self.SDEtype = "SDEint"
        self.solverString = None
        self.p = p#SDE object to be integrated.
        self.theta = theta#Used for Theta scheme
        self.solverTup = availableSolvers(problem=p)
        if solverString != None:
            self.setSolver(solverString)
        self.X = {}

    def returnSolvers():
        '''Returns solvers available in this solver-object. '''
        return availableSolvers(problem = self.p)

    def reduceTime(t,factor):
        '''Returns new t-array has length (len(t)-1)/factor.'''
        if not factor.is_integer():
            raise ValueError(str(factor)+" is not an integer.")
        newLen = (len(t)-1)/factor
        if not newLen.is_integer():
            raise ValueError(("(len(t)-1)/factor is not a whole number, but "
                +str(newLen)+"."))
        return np.linspace(t[0],t[-1],newLen)

    def setSolver(self, solverString):
        """Sets solver method with solverString."""
        if solverString in self.solverTup:
            print("Set solver: ",solverString)
            self.solverString = solverString
        else:
            s = solverString + " is not among the methods implemented in osIto."
            raise NotImplementedError(s)

    def solver(self,p,X,t,h,dW):
        """Performs one step on problem p with value X at time t with time step
        h and Wiener-increment dW."""
        return getattr(self, self.solverString)(p, X, t, h, dW)
        
    def oneStepper(self,simNum, reducedTime = None):
        """For solving SDE by using solver as a generator until the number
        of steps reaches n."""
        yield self.p.X0
        Xs = self.p.X0
        counter = 0
        if reducedTime is None:
            while counter < self.p.n:
                Xs = self.solver(self.p, Xs, self.p.t[counter],self.p.h,
                    self.p.dW[counter+1,:,simNum])
                counter += 1
                yield Xs
        else:
            new_n = len(reducedTime)-1
            while counter < new_n:
                Xs = self.solver(self.p, Xs, reducedTime[counter],self.p.h,
                    self.p.dW[counter+1,:,simNum])
                counter += 1
                yield Xs

    #For when method is called only with initial conditions specified.
    def solve(self, solverString=None,timeFactor = 1):
        """Central method of osIto, call this to solve SDEprob.

        After an osIto is created, this is the function you call to solve
        SDEprob. First ensures a valid solver is chosen, then oneStepper is
        called which solves SDEprob. Then a solution object is created with the
        answer, which adds itself to SDEprob's solution dictionary."""
        if solverString is not None:#Allows both setting and resetting solver.
            self.setSolver(solverString)
        elif self.solverString is None:#In case solver not set before or now.
            raise ValueError("solverString not included before osIto.solve().")

        if timeFactor == 1:
            #Embeds solution into solution ditorionary here.
            if self.solverString not in self.p.solDict:#Only solves once.
                t = self.p.t
                X = np.zeros((len(t),self.p.d,self.p.totSimNum))
                for simNum in range(0,self.p.totSimNum):
                    if self.p.totSimNum > 1:
                        update_progress(simNum/self.p.totSimNum)
                    X[:,:,simNum] = list(self.oneStepper(simNum))
                X = np.array(X)
                #Embeds solution into p.solDict here.
                solution(self.p, X, self.solverString)
                if self.p.totSimNum > 1:
                    print(" ",end='')
        else:#For solving a problem realization with different step sizes.
        #Does not get added to p.solDict
            t = self.p.reduceTime(self.p.t,timeFactor)
            X = np.zeros((len(reducedTime),self.p.d,self.p.totSimNum))
            for sim in range(0,self.p.totSimNum):
                if self.p.totSimNum > 1:
                        update_progress(sim/p.totSimNum)
                X[:,:,simNum] = list(self.oneStepper(simNum,
                    reducedTime = t))
            X = np.array(X)
        if self.p.totSimNum > 1:
                print(" ",end='')
        if self.printNum:
            print("X: ",np.squeeze(X))
        if hasattr(self.p,'trueX'):   
            if self.p.trueX is not None:
                string = ("End-point relative error (delta norm/ absolute norm) "
                    + "for sim = 0: " +str(np.linalg.norm(X[-1,:,0]
                        -self.p.trueX[-1,:,0])/np.linalg.norm(
                        self.p.trueX[-1,:,0])))
                print(string)
        return (t,np.squeeze(X))

    def manualSolve(self,p,t,dW):
        '''Solves p without p.t and p.dw, but with t and dW instead. '''
        try:
            if len(t) != len(dW):
                raise ValueError("t must have same length as dW")
                return
        except TypeError:
            print("len throws TypeError because t or dW has no len()")
        h = t[1]-t[0]#Assumes t is homogenously spaced.
        X = np.zeros((len(t),len(self.p.X0),p.totSimNum))
        for sim in range(p.totSimNum):
            # if p.totSimNum > 1:
            #     update_progress(sim/p.totSimNum)
            X[:,:,sim] = np.array(list(self.manualOneStepper(p.X0,t,h,
                dW[:,:,sim])))
        return (t,np.squeeze(X))

    def manualOneStepper(self,X0,t,h,dW):
        """For solving an SDE using custom t and dW instead of p.t and p.dW."""
        yield X0
        Xs = self.p.X0
        i = 0
        length = len(t)-1
        while i < length:
            Xs = self.solver(self.p, Xs, t[i],h,dW[i])
            i += 1
            yield Xs
        
    def itoEM(self, p, X, t, h, dW):
        """Euler-Maruyama method for Ito."""
        a = p.f(X, t)*h
        for k in range(p.m):
            a += p.g[k](X, t)*dW[k]
        return X + a
    
    def itoMilstein11(self, p, X, t, h, dW):
        """Milstein method for Ito, d=m=1."""  
        g = p.g[0](X, t)
        a = p.f(X, t)*h + g*dW[0] + g*p.g1[0][0](X, t)*(dW[0]*dW[0] - h)/2
        return X + a

    def itoMilsteinD1(self, p, X, t, h, dW):
        """Milstein method for Ito, d=2,3,...m=1.

        Requires that problem has g1 attribute which is a d x d list of where
        p.g1[i][j](X,t) represents the j'th partial derivative of p.g[i](X,t),
        or dg^i/dx^j."""    
        a = p.f(X, t)*h
        b = p.g[0](X, t)*dW
        c = X + a + b
        k = 0.5*(dW**2 - h)
        try:
            for i in range(p.d):
                for j in range(p.d):
                    c[i] += b[j]*p.g1[i][j](X,t)*k
        except AttributeError:
            print("Milstein method only works when the derivative of g is "
                ,"included in problem.")
            return None

    def itoBackwardsEulerDM(self, p, X, t, h, dW):
        """Same as semi-implicit Euler scheme with theta equal to 1.

        Requires p is dX = FXdt + G(X,t)XdW"""
        gInc = np.zeros(X.shape)
        for k in range(p.m):
            gInc += p.g[k](X, t)*dW[k]
        a = np.identity(p.d)-p.F*h
        # print("1,2: ",a,a.shape)
        # print("X, gInc, X.shape, gInc.shape: ",X,gInc,X.shape,gInc.shape)
        b = np.reshape(X +gInc,(p.d,1))
        Xn1 = np.reshape(np.linalg.solve(a,b),(p.d,))
        fInc = (self.theta*p.f(Xn1,t)*h + (1-self.theta)*p.f(X, t)*h)
        # print("X,fInc,gInc,X.shape,fInc.shape,gInc.shape: ",X,fInc,gInc,X.shape
            # ,fInc.shape,gInc.shape)
        return X + fInc + gInc

    def itoThetaDM(self, p, X, t, h, dW):
        """Theta scheme. Controlled by parameter self.theta.

        Requires p is dX = FXdt + G(X,t)XdW"""
        gInc = np.zeros(X.shape)
        for k in range(p.m):
            gInc += p.g[k](X, t)*dW[k]
        a = np.identity(p.d)-p.F*self.theta*h
        b = np.reshape(X + (1-self.theta)*p.f(X,t)*h+gInc,(p.d,1))
        Xn1 = np.reshape(np.linalg.solve(a,b),(p.d,))
        fInc = (self.theta*p.f(Xn1,t)*h + (1-self.theta)*p.f(X, t)*h)
        c = X + fInc + gInc
        return c

    def itoBackwardsEuler1M(self, p, X, t, h, dW):
        """Same as semi-implicit Euler scheme with theta equal to 1.

        Requires p is dX = FXdt + G(X,t)XdW"""
        gInc = np.zeros(X.shape)
        for k in range(p.m):
            gInc += p.g[k](X, t)*dW[k]
        Xn1 = (X+gInc)/(1-p.f(0,0)*self.theta*h)
        fInc = (self.theta*p.f(Xn1,t)*h + (1-self.theta)*p.f(X, t)*h)
        return X + fInc + gInc

    def itoTheta1M(self, p, X, t, h, dW):
        """Theta scheme. Controlled by parameter self.theta.

        Requires p is dX = FXdt + G(X,t)XdW"""
        gInc = np.zeros(X.shape)
        for k in range(p.m):
            gInc += p.g[k](X, t)*dW[k]
        Xn1 = ((X + (1-self.theta)*p.f(0,0)*h+gInc)/
            (1-p.f(0,0)*self.theta*h))
        fInc = (self.theta*p.f(Xn1,t)*h + (1-self.theta)*p.f(X, t)*h)
        return X + fInc + gInc

    def itoPlaten(self, p, X, t, h, dW):
        """Strong order 1 Runge-Kutta method for d=1,2,3,...,m=1."""
        g1 = p.g[0](X, t)
        g2 = p.g[0](X + g1 * np.sqrt(h), t)
        temp = (g2 - g1) * (h**(-0.5)) * (dW*dW - h) / 2
        return np.reshape(self.itoEM(p,X,t,h,dW) + temp,X.shape) 

class osStrat(SDEsolver):
    """Solver class for one-step Stratonovich."""
    def __init__(self, problem, solverString):
        pass


# Solver class for other methods. Contains complete methods since multi-step
# methods have summation procedures specific to the multi-step method, thus
# summation methods can't be modular and shared like oneStepper above is.
class comSolver(SDEsolver):
    pass

def update_progress(progress):
    print("\rProgress for integrating sample paths: [{0:50s}] {1:.1f}%".format('#' *
        int(progress * 50),progress*100), end="", flush=True)