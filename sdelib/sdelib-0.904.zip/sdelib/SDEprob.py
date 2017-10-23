import numpy as np
import numbers
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets
import scipy.io
import logging
import SDEint

class Error(Exception):
    pass

class SDEValueError(Error):
    """General error used when something goes wrong in a method.

    Used when incompatibilities are discovered between f, g, X0 and dW for 
    dimensions."""
    pass

class SDEprob:
    """Represents an SDE from class variables f, g, X0, t, W and dW.

    Class constitutes a description of a Stochastic Differential Equation of the
    form dX = f(X,t)dt + g(X,t)dW where X is the value of the stochastic
    process at t = t[n-1], W is the Wiener process, it's increment dW =dW[n]-
    dW[n-1],and t is the time. Basically a container for the problem described
    by the functions f and g that gets sent to the constructor. Solving this
    problem is done elsewhere."""
    def __init__(
            self, spec=None,f=None, g=None, X0=None, t=None, totSimNum=1,
            m=None,nFine = None, dWFine = None, expSol = None,
            trueSol=None, g1=None, name='Unspecified',
            printTrue = False, seed = None,GUI = False, equationType = 'Ito'):
        """Initializes object either through script or GUI.

        Adds initial conditions specified by spec or X0, t, totSimNum, d and
        m. Adds functions specified by spec or functions f and g. Calls
        check_args to check if dimensions between initial conditions and
        the functions specifying the problem match.
        Input arguments:
        Spec = SDEspec object, an object containing f function and g list of gk
        functions, and dimensions d and m consistent with output of functions.
        f = Drift function
        g = Diffusion function
        X0 = X(0), needs length consistent with outputs of f and g.
        t = Array representing time, assumed of form np.linspace(0,T,n+1)
        m = Number of Wiener processes.
        n = Number of time jumps, meaning len(t)-1.
        totSimNum = Number of sample paths. It is assumed you create the noise
        while you create the SDEprob object, not while you solve an SDEprob. 
        W = Matrix of Wiener process at time t and sample path sim. Has numpy
        shape (n+1, m, totSimNum). W(0) = 0 is included as start point
        dW = Matrix of Wiener increments of numpy shape (n+1, m, totSimNum).
        Has same shape as W for simple error checks, though first point dW[0]=
        np.zeros(d) is never used for anything."""

        self.SDEtype = "SDEprob"#Identifier for opening objects from file.
        self.equationType = equationType#Ito or Stratonovich.
        self.completed = False#For plotting solution.
        self.GUI = GUI#Whether messages show up in windows or terminal.
        self.name = name

        #For overwriting f,g,trueSol,expsol,g1 from spec if spec exists.
        if spec != None:
            print("1")
            #print("spec is not None")
            self.spec = spec
            f, g, GUI, name = spec.f, spec.g, spec.GUI, spec.name
            if hasattr(spec,'trueSol'):
                if spec.trueSol != None:
                    trueSol = spec.trueSol
            if hasattr(spec,'expSol'):
                if spec.expSol != None:
                    expSol = spec.expSol
            if hasattr(spec,'g1'):
                if spec.g1 != None:
                    g1 = spec.g1
                name = spec.name

        # # Does various tests of input and 
        d, m, f, g, X0, t, totSimNum = _check_args(f, g, X0, t, totSimNum,GUI)
        self.n = int(len(t)-1)#Number of time intervals.
        self.h = t[1]-t[0]#Step size h.
        #X in R^d, m Wiener processes, totSimNum sample paths (for averaging)
        self.d, self.m, self.totSimNum = d, m, totSimNum
        self.f, self.g, self.g1 = f, g, g1#Problem functions
        self.trueSol, self.expSol = trueSol, expSol#True solution and expected
        #value of solution.
        self.X0, self.t = X0, t#Initial conditions
        self.solDict = {}#Solution dictionary
        #Dictionaries
        self.strongConDict, self.weakConDict, self.stabDict = {}, {}, {}
        self.solved, self.numOfSol = False, 0#Neither used much currently
        self.printTrue = printTrue#For printing. Used for bug testing.

        #Create higher res t for true solution.
        if nFine != None:
            #Creates nFine as provided if nFine is a multiple of n.
            self.nFine = nFine
            self.factor = nFine/self.n
            if not self.factor.is_integer():
                if self.GUI:
                    openMessageBox("nFine has to be divisible by n.")
                else:
                    raise ValueError("nFine has to be divisible by n.")
            else:
                self.factor = int(self.factor)
        else:
            #Creates nFine as the lowest power of 2 times n above 4096.
            if self.n < 4096:
                # print("4")
                self.factor = np.ceil(4096/self.n)
                tmp = 1
                while tmp < self.factor:
                    tmp = tmp*2
                self.factor = tmp
                self.nFine = self.factor*self.n
            else:#nFine equal to n if n is large.
                self.nFine = self.n
                self.factor = 1
            self.tFine = np.linspace(0,t[-1],self.nFine)
        self.tFine = np.linspace(0,t[-1],self.nFine+1)
        self.hFine = self.tFine[1]-self.tFine[0]
    

        np.random.seed(seed)#Sets seed, default-value None means random.
        try:
            matFine = np.random.standard_normal(size=(self.nFine, self.m,
                self.totSimNum))
        except MemoryError:#If matFine is too large
            numOfElements = self.nFine*self.m*self.totSimNum
            floatSize = np.finfo(float)
            estSize = numOfElements*floatSize/(1024*1024)
            string = ("Wiener matrix too big, MemoryError thrown. Wiener "
                +"matrix of size (" +str(nFine)+str(self.m)
                + str(self.totSimNum) + " won't be created. Estimated byte "
                + "size = Number of elements x size of 1 float ~= "
                + str(numOfElements) +"x" + str(floatSize) + "= "+str(estSize)
                + "MB.")
            if self.GUI:
                openMessageBox(string)
            else:
                print(string)
            return None

        W0 = np.zeros((1,self.m,self.totSimNum))#Includes W(0) = 0 in W matrix.
        matFine = np.concatenate((W0,matFine),axis=0) 
        self.dWFine = np.dot(np.sqrt(self.hFine),matFine)
        #Allows including an external noise process, used for making sure I got
        #the same results as Higham matlab scripts while searching for bugs.
        if dWFine != None:
            # variableDict = scipy.io.loadmat('C:\Drive\SDE\Higham\emstrong.mat')
            # dWFine = variableDict['dWMat']
            dWFine = np.array(dWFine)
            shape = dWFine.shape
            newShape = (len(self.tFine),self.m,self.totSimNum)
            print("dWFine.shape: ",shape)
            if len(dWFine) != len(self.tFine):
                print("len(dWFine),len(tFine)",len(dWFine),len(self.tFine))
                self.tFine = np.linspace(0,t[-1],len(dWFine))
            if shape != newShape:
                #Insert specific code here, typically a singleton dim needs to
                #be added.
                print("Shape mismatch, oldshape, newshape: ",shape,newShape)
                dWFine = np.expand_dims(dWFine,axis=1)
            self.nFine = len(dWFine)-1
            self.dWFine = dWFine
            self.tFine = np.linspace(0,t[-1],self.nFine+1)
            self.hFine = self.tFine[1]-self.tFine[0]
            self.factor = self.nFine/self.n
            if self.factor.is_integer():
                self.factor = int(self.factor)
            else:
                string = ("(self.nFine/self.n).is_integer = False. nFine = " +
                    str(self.nFine) + ", n = " + str(self.n) + ".")
                print("factor: ",self.factor)
                message(string,GUI,error=Tr)

        self.WFine = np.cumsum(self.dWFine, axis=0)#Create WFine from dWFine.
        self.W = self.WFine[::self.factor]#Create W from WFine.
        self.dW = self.W[1:self.n+1]-self.W[:self.n]
        self.dW = np.concatenate((W0,self.dW),axis=0)

        #Error check for whether cumsum of dWFine and dW match.
        if self.factor != 1:
            lastDiffers = np.abs(np.sum(self.dW[:,:,0])-np.sum(self.dWFine[:,:,0]))
            if lastDiffers > 1e-12:#For finding cause if dW != dWFine 
                print("W[-1]=!WFine[-1]: ")
                print("WFine[0:factor]: ",self.WFine[0:self.factor,:,0])
                print("W[0:factor]: ",self.W[0:self.factor,:,0])
                print("tFine[0:factor]: ",self.tFine[0:self.factor])
                print("t[0:factor]: ",self.t[0:self.factor])
                print("WFine[-1],W[-1]:",self.WFine[-1,:,0],self.W[-1,:,0])

        #For adding trueSol without SDEspec
        if trueSol == "Autonomous and multiplicative":
            if self.d == 1:
                def trueSol(p):
                    a1 = p.f(np.array(1),0)
                    a2 = 0
                    for k in range(p.m):
                        a2 += p.g[k](np.array(1),0)**2
                    a3 = a1-0.5*a2
                    a = np.multiply(a3,p.tFine[1:])
                    b = np.zeros(p.WFine[:,0].shape)
                    for k in range(p.m):
                        b += np.squeeze(p.g[k](1,0))*p.WFine[:,k]
                    #Needs singleton dimension for consistency with sdelib.
                    c = np.zeros((len(p.tFine),p.d,p.totSimNum))
                    for sim in range(p.totSimNum):
                        d = np.squeeze(a)+np.squeeze(b[1:,sim])
                        e = np.exp(d)*p.X0
                        e = np.insert(e,0,p.X0,axis=0)
                        c[:,0,sim] = e
                    if p.printTrue:
                        print("Printing true solution:")
                        for sim in range(p.totSimNum):
                            print("Sample path nr ",sim)
                            print(np.squeeze(c[:,0,sim]))
                    return c
            else:
                def trueSol(p):
                    F = getF(p.f,p.d)#For dX = (FX+f(X,t))dt, calculate F-matrix
                    G = []
                    for k in range(p.m):
                        Gk = getF(p.g[k],p.d)
                        G.append(Gk)
                    A = F - 0.5*sum([Gk*Gk for Gk in G])
                    trueX = np.zeros((len(p.tFine),p.d,p.totSimNum))
                    for sim in range(p.totSimNum):
                        trueX[0,:,sim] = p.X0
                        for i in range(1,p.nFine):
                            B = np.zeros(F.shape)
                            for k in range(p.m):
                                B += G[k]*p.WFine[i,k,sim]
                            trueX[i,:,sim] = linalg.expm(A*p.tFine[i]+B)@p.X0
                        update_progress(sim/p.totSimNum)
                    if p.printTrue:
                        print("Printing true solution.")
                        for sim in range(p.totSimNum):
                            print("Sample path nr ",sim)
                            for d in range(p.d):
                                print("Dimension nr ",d)
                                print(trueX[:,d,sim])
                    return trueX
            print(" ")#For line shift after update progress.
        if trueSol != None:
            print("Calculating true solution from Mao's formula.")
            self.trueX = trueSol(self)
        else:#If trueSol ==None, assumes trueSol is itoEM with nFine.
            print("Using ItoEM with ",str(self.nFine)," steps as trueSol since"
                + " trueSol == None.")
            [t,X] = osIto(self,solverString='itoEM').manualSolve(tFine,dWFine)
            self.trueX = X
        self.trueMean = self.trueX.mean(axis=2)#Mean along sample paths.

    def reduceTime(self,t,factor):
        """Returns time vector with 1/factor as many time steps."""
        if type(factor) != int:
            if not factor.is_integer():
                raise ValueError(str(factor)+" is not an integer.")
        newLen = (len(t)-1)/factor
        if not newLen.is_integer():
            raise ValueError(("(len(t)-1)/factor is not a whole number, but "
                +str(newLen)+"."))
        return np.linspace(t[0],t[-1],newLen)

    def reducedW(self,dW,factor):
        """Returns dW with 1/factor as many time steps."""
        if type(factor) != int:
            if not factor.is_integer():
                raise ValueError(str(factor)+" is not an integer.")
        newLen = (len(dW)-1)/factor
        if not newLen.is_integer():
            raise ValueError(("(len(dW)-1)/factor is not a whole number, but "
                +str(newLen)+"."))
        return dW[::factor]
    
    def addSolution(self, solution, methString):
        """Adds solution to solution dictionary."""
        self.solDict[methString] = solution
        self.solved = True
        self.numOfSol = self.numOfSol + 1

    def plotSolutions(
        self, methodList=None, subplot=False,simNum = None, plotMean = False,
        plotSamp = True, plotTrue = True, plotTrueMean = False
    ):
        """Plots solututions specified by input or else assumes

        Most of the code performs checks on what to print. plotSamp specifies
        whether a sample path is printed, plotTrue indicates whether a true
        solution is printed. plotTruemean indicates whether a mean of true
        solutions is printed."""
        if self.totSimNum == 1:#Mean calculations unnecessary for 1 sample path
            plotMean = False#Drops plotting mean for single sample path.
            if simNum == None:
                simNum = 0#Sets first sample path if no simNum included.
        else:#Creates dictionary of means of solution.
            meanDict ={}
            if plotMean:
                if methodList == None:
                    for key, value in self.solDict.items():
                        meanDict[key] = np.mean(value.X,axis=2)
                else:
                    for key in methodList:
                        meanDict[key] = np.mean(solDict[key].X,axis=2)
        if plotTrueMean:
            trueMean = np.mean(self.trueX,axis=1)
        if plotSamp == True and simNum == None:
            simNum = 0

        #Plots solutions in methodList, else plots all solutions in solDict.
        if methodList == None:
            keys = self.solDict.keys()
        else:
            keys = methodList

        #Plots seperate figure for each dimension.
        for i in range(self.d):
            plt.figure(i)
            if plotSamp:#Plot sample path.
                for key in self.solDict.keys():
                    if key in keys:
                        value = self.solDict[key]
                        string = (key + ", sim = " + str(simNum)
                            +", dim = " + str(i)+", len(t) = " +
                            str(len(self.t)) + ".")
                        X = np.squeeze(value.X[:,i,simNum])#For when shape=(1,)
                        plt.plot(self.t,X,label=string)
            if plotTrue:#Plots true solution of sample path simNum
                string = ("True solution, sim = "+ str(simNum)
                    +", dim = " + str(i)+", len(tFine) = " +
                            str(len(self.tFine)) + ".")
                X = np.squeeze(self.trueX[:,i,simNum])#For when shape=(1,)
                plt.plot(self.tFine, X,label=string)
            if plotTrueMean:#Plots mean of true solution
                string = ("Mean of true solution, dim = " + str(i) + 
                    ", len(tFine) = " + str(len(self.tFine)) + ".")
                X = np.squeeze(self.trueMean[:,i])#For when shape=(1,)
                plt.plot(self.tFine, X,label=string)
            if plotMean:#Plot means in meanDict.
                for key, value in meanDict.items():
                    string = ("Mean of " + key +" along dimension nr. " 
                    + str(i) + ", len(t) = " + str(len(self.t)) + ".")
                    X = np.squeeze(value[:,i])#For when shape=(1,)
                    plt.plot(self.t,X,label=string)
            plt.xlabel('t')
            plt.ylabel('X(t)')
            plt.title('Plot of problem named '+self.name)
            plt.legend(loc='upper left')
        plt.show()


def _check_args(f, g, X0, t, totSimNum,GUI):
    """Sanity checks on f, g, X0 and totSimNum.

    Does various tests of input, including testing whether dimensions
    match, matches input type of X0 with f and g, whether time input
    has uniform spacing, whether totSimNum is integer. Returns number of equations
    d, number of Wiener processes m, number of time jumps n along with all the
    inputs."""

    #sdelib requires uniform t.
    if not np.isclose(min(np.diff(t)), max(np.diff(t))):
        string = "t must be uniformly spaced."
        message(string,GUI,error=True)

    #Set dimension d of SDE, len doesn't work if X0 is number.
    try:
        d = len(X0)
    except TypeError:
        d = 1
        X0 = np.array(X0).reshape((d,))
    
    #Checks if output of f has correct shape.
    if f(X0, t[0]).shape != X0.shape:
        string = (
            "f(X0,t[0]).shape = "+ str(f(X0, t[0]).shape) + 
            ",while X0.shape = " + str(X0.shape) + ". The values are "
            + "f(X0,t[0]) = " + str(f(X0,t[0])) + ", while X0 = " + str(X0)
            + ".")
        message(string,GUI,error=True)

    #Checks that g is a list of m callable functions, throws error if not.
    if type(g) == list:#
        g = tuple(g)
        m = len(g)
        for k in range(0, m):
            if not callable(g[k]):
                message(string,GUI,error=True)
                return
            Gtestk = g[k](X0, t[0])
            if Gtestk.shape != X0.shape:#Checks if output has correct shape.
                string = ("g[k](X0, t[0]).shape = "+ str(np.shape(Gtestk))
                    +", while X0.shape = "+str(X0.shape)+". g[k](X0, t[0]) = "
                    +str(Gtestk)+", while X0 = " + str(X0)+".")
                message(string,GUI,error=True)
                return
    else:
        string = (
            "g needs to be a list. Each element in the list is a function.")
        message(string,GUI,error=True)
        return

    #Checks that totSimNum is integer
    if not np.isclose(totSimNum,int(totSimNum)):
        string = ("totSimNum isn't an integer, totSimNum = %d with type =  %s"
            % (totSimNum, type(totSimNum)))
        message(string,GUI,error=True)
        return
    else:
        totSimNum = int(totSimNum)
    return d, m, f, g, X0, t, totSimNum
 
def getF(f,d):
    """Used for getting a constant matrix A out of function.

    For example if f(X,t) = AX + a(t) and X in R^3, f is called with f(e_k,0)
    where e_k is one of the 3 basis vectors for R^3 for all k to recreate F.
    This assumes a(0) = 0."""
    F = np.zeros((d,d))
    X = np.identity(d)
    for i in range(d):
        F[:,i] = f(X[:,i],0)
    return F

def message(message,GUI,error=False):
    """Prints message in manner dictated by GUI and error."""
    if GUI:
        openMessageBox(message)
    elif error:
        raise SDEValueError(message)
    else:
        print(message)

def openMessageBox(message,title="Message"):
    """Prints message in message box"""
    box = QtWidgets.QMessageBox()
    box.setIcon(QtWidgets.QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.exec_()