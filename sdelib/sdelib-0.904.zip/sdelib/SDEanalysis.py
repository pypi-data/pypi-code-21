import numpy as np
import matplotlib.pyplot as plt
import SDEint

def calcStrongCon(p,solverList,printNum=False):
    plt.show()
    performAction(p,'strongCon',solverList,printNum=printNum)

def calcWeakCon(p,solverList,printNum=False):
    plt.show()
    performAction(p,'weakCon',solverList,printNum=printNum)

def performAction(p, action, solverList,printNum=False):
    if p.trueSol == None:
        message = ("p.trueSol = None, therefore Euler-Maruyama with "
+"n = nFine will be used as the true solution to estimate convergence.")
    for solvString in solverList:
        aSolvers = SDEint.availableSolvers(p)
        if solvString in aSolvers:
            if action == 'strongCon':
                p.strongConDict[solvString] = strongCon(p,solvString,printNum=printNum)
            elif action == 'weakCon':
                p.weakConDict[solvString] = weakCon(p,solvString,printNum=printNum)
            elif action == 'stability':
                p.stabDict[solvString] = stability(p,solvString,printNum=printNum)
            else:
                raise NotImplementedError("Something went horribly wrong.")
        else:
            message = (solvString + " is not among the available solvers for "
+"problem named "+p.name +" of equation type "+p.equationType+". This problem "
+"can be solved by the following tuple of solvers: ")
            print(message)
            print(aSolvers)
    plt.show()

class strongCon:
    """Container class for calculating strong convergence for 1 solver for
    SDEprob."""
    def __init__(self,p,solvString,printNum=False):
        if p.n % 16 != 0:
            print("len(t) needs to be divisible by 16 for convergence "
                ,"analysis.")
        else:
            if solvString in SDEint.availableSolvers(solverType='osIto'):
                solver = SDEint.osIto(p,solvString,printNum=printNum)
            elif solvString in SDEint.availableSolvers(solverType='osStrat'):
                solver = SDEint.osStrat(p,solvString,printNum=printNum)
            elif solvString in SDEint.availableSolvers(solverType='comSolver'):
                solver = SDEint.comSolver(p,solvString,printNum)

            #Calculates absolute error at last element for 1,2,4,8,16 dt.
            M = p.totSimNum
            dt = p.hFine
            N  = p.nFine
            if p.trueSol != None:
                Xtrue = p.trueSol(p)
            else:
                Xtrue = SDEint.manualSolver(p,p.tFine,p.dWFine)
            self.Xerr = np.zeros((M,5)) # preallocate array
            task = ('Computing strong convergence for solver '+solvString)
            for sim in range(M): # sample over discrete Brownian paths
                dW = p.dWFine[:,:,sim]
                W = p.WFine[:,:,sim]
                conPoints = 5
                for n in range(0,conPoints):
                    R = 2**n
                    Dt = R*dt
                    L = N/R # L Euler steps of size Dt = R*dt
                    Xtemp = p.X0
                    t = p.t[0]
                    for j in range(1,int(L)+1):
                        t = t + Dt
                        Winc = dW[R*(j-1)+1:R*j+1].sum(axis=0)
                        Xtemp2 = solver.solver(p,Xtemp,t,Dt,Winc)
                        #print("Xtemp2, Xtemp, Winc, Dt j, R, R*j, R*(j+1): ",Xtemp2, Xtemp,Winc,Dt,j,R,R*(j-1)+1,R*j)
                        Xtemp = Xtemp2
                    tmp = Xtrue[-1,:,sim]
                    err = np.linalg.norm(Xtemp - tmp)
                    self.Xerr[sim,n] = err
                update_progress(sim/M)
                #print(sim, Xtemp,tmp)
            print(" ")
            #Does least squares to calculate convergence coefficent.
            DtVals = dt*2**np.array(range(0,5))
            ones = np.ones(len(DtVals))
            A = np.vstack([ones,np.log(DtVals)]).T
            print("A: ",A)
            XerrMean = np.mean(self.Xerr,axis=0)
            print("XerrMean: ",XerrMean)
            y = np.log(XerrMean)
            print("rhs: ",y)
            self.OOC, self.res, rank, s = np.linalg.lstsq(A,y)
            # print("self.OOC, self.res, rank, s: ",self.OOC, self.res, rank,s)
            message = ("\n" + solvString +
                " has an estimated strong order of convergence of "
                + str(self.OOC[1]) + " with a residual of " + str(self.res[0]))
            print(message)
            plt.figure()
            plt.loglog(DtVals,(DtVals**self.OOC[1]),label='Least squares line')
            plt.loglog(DtVals,XerrMean,label='Error at end point',
                marker = 'x')
            plt.xlabel('stepsize dt')
            plt.ylabel('Mean square norm of error')
            plt.title('Loglog of strong convergence for solver '+ solvString) 
            plt.legend(loc='upper left')
            plt.show()

class weakCon:
    """Container class for calculating strong convergence for 1 solver for
    SDEprob."""
    def __init__(self,p,solvString,printNum=False):
        if p.n % 16 != 0:
            print("len(t) needs to be divisible by 16 for convergence "
                ,"analysis.")
        else:
            if solvString in SDEint.availableSolvers(solverType='osIto'):
                solver = SDEint.osIto(p,solvString,printNum=printNum)
            elif solvString in SDEint.availableSolvers(solverType='osStrat'):
                solver = SDEint.osStrat(p,solvString,printNum=printNum)
            elif solvString in SDEint.availableSolvers(solverType='comSolver'):
                solver = SDEint.comSolver(p,solvString,printNum)

            from scipy.stats import norm
            #np.random.seed(100)

            #Calculates absolute error at last element for 1,2,4,8,16 dt.
            res = 5
            low2Fact = 5#[0,T] has 2^5 intervals at low end
            high2Fact = low2Fact + res#[0,T] has 2^(5+5) intervals at high end.
            M = 50000# number of paths sampled
            Xem = np.zeros((5,1))# preallocate arrays
            Xerr = np.zeros((res,p.d))
            #print("p.expSol: ",p.expSol)
            EndExp = p.expSol(p.X0,p.t)[-1]
            #print("EndExp: ",EndExp)
            DtVals = []
            for i in range(res):#take various Euler timesteps
                DtVals.append(p.t[-1]*2**(i-9))
                L = int(p.t[-1]/DtVals[i])# L Euler steps of size Dt
                #print("DtVals[i], i, L: ",DtVals[i], i, L)
                Xtemp = np.ones(d,M)
                t = 0
                for j in range(L):
                    Winc = np.sqrt(DtVals[i])*norm.ppf(np.random.rand(p.m,M))
                    Xtemp = solver.solver(p,Xtemp,t,DtVals[i],Winc)
                    t = t + DtVals[i]
                    #print("j, Winc, Xtemp: ",j,Winc,Xtemp)
                    update_progress((j/L+i)/res)
                #print("Xtemp.shape: ",Xtemp.shape)
                Xem[i] = np.mean(Xtemp,axis=0)
                Xerr[i] = np.linalg.norm(Xem[i] - EndExp)
                #print("Xem[i], Xerr[i]: ",Xem[i], Xerr[i])
            print(" ")
            Xerr = Xerr/res
            #Does least squares to calculate convergence coefficent.
            ones = np.ones(len(DtVals))
            A = np.vstack([ones,np.log(DtVals)]).T
            y = np.log(Xerr)
            self.OOC, self.res, rank, s = np.linalg.lstsq(A,y)
            # print("self.OOC, self.res, rank, s: ",self.OOC, self.res, rank,s)
            message = ("\n" + solvString +
                " has an estimated weak order of convergence of "
                + str(self.OOC[1]) + " with a residual of " + str(self.res[0]))
            print(message)
            plt.figure()
            plt.loglog(DtVals,(DtVals**self.OOC[1]),label='Least squares line')
            plt.loglog(DtVals,Xerr,label='Error at end point',
                marker = 'x')
            plt.xlabel('stepsize dt')
            plt.ylabel('Mean square norm of error')
            plt.title('Loglog of weak convergence for solver '+ solvString) 
            plt.legend(loc='upper left')

class stability:
    def __init__(self,p,solverString):
        pass

def update_progress(progress,task='Progress of task'):
    print("\rProgress of task: [{0:50s}] {1:.1f}%".format('#' *
        int(progress * 50),progress*100), end="", flush=True)