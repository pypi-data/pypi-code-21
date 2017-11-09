import numpy as np
import matplotlib.pyplot as plt
import SDEint

def calcStability(p,solverList,fontsize = 30):
    print("Calculating stability regions for solvers in solverList.")
    '''Displays stab-func of scalar test equation for solvers in solverList.'''
    performAction(p,'stability',solverList)
    levels1 = [0,0.5,1,1.5]
    levels2 = [0.9,1,1.1]
    L = len(solverList)
    if L == 0:
        print("No solvers chosen.")
        return

    plots, labels, colors = [], [],('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')
    rows = np.ceil(L/2)
    s = p.stabDict[solverList[0]]
    R = Rborder(s.X,s.Y)
    for i in range(len(solverList)):
        plt.subplot(rows,2,i+1)
        s = p.stabDict[solverList[i]]
        cs = plt.contour(s.X,s.Y,s.R,levels=levels1,colors=('blue','r',
            'green', 'black'),linewidths=[1,1,5,1])
        cs2 = plt.contourf(s.X,s.Y,R,levels=levels2)
        lam, mu2 = p.f(1,0), p.g[0](1,0)**2
        length = np.linalg.norm([lam,mu2])
        lam, mu2 = lam/length, mu2/length
        onetofour = np.array([1,2,3,4])
        lams = np.dot(lam,onetofour)
        mu2s = np.dot(mu2,onetofour)
        plt.scatter(lams, mu2s, marker='o', s=20,c='yellow')
        plt.clabel(cs,inline=1,fontsize=20)
        plt.xlabel('lambda h',fontsize=20)
        plt.ylabel('mu^2 h',fontsize=20)
        plt.title(solverList[i],fontsize=20)
        plt.axis([-4,4, 0, 8])
    plt.tight_layout()
    plt.show()

def calcStrongCon(p,solverList,printNum=False,fontsize = 30):
    print("Estimating strong OOC for solvers in solverList.")
    '''Estimates strong order of convergence for solvers in solverList.'''
    if p.totSimNum < 1000:
        print("WARNING: p.totSimnum<1000. This is less than recommended ",
            "amount of sample paths for estimation of strong OOC.")
    plt.show()
    performAction(p,'strongCon',solverList,printNum=printNum,fontsize=fontsize)

def calcWeakCon(p,solverList,printNum=False,M=50000,fontsize = 30):
    print("Estimating weak OOC for solvers in solverList.")
    '''Estimates weak order of convergence for solvers in solverList.

    Only works for d=1 right now.'''
    if p.d > 1:
        print("calcWeakCon only implemented for d = 1 for now.")
    plt.show()
    performAction(p,'weakCon',solverList,printNum=printNum,M=M,
        fontsize = fontsize)

def performAction(p, action, solverList,printNum=False, M = 50000,
    fontsize = 30):
    np.set_printoptions(precision=6)
    for solvString in solverList:
        aSolvers = SDEint.availableSolvers(p)
        if solvString in aSolvers:
            if action == 'strongCon':
                p.strongConDict[solvString] = strongCon(p,solvString,
                    printNum=printNum,fontsize = fontsize)
            elif action == 'weakCon':
                p.weakConDict[solvString] = weakCon(p,solvString,
                    printNum=printNum, M=M,fontsize = fontsize)
            elif action == 'stability':
                p.stabDict[solvString] = stability(p,solvString)
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
    """Container class for calculating strong OOC for 1 solver."""
    def __init__(self,p,solvString,printNum=False,fontsize = 30):
        if p.n % 16 != 0:
            print("len(t) needs to be divisible by 16 for convergence "
                ,"analysis.")
            return
        if solvString in SDEint.availableSolvers(solverType='osIto'):
            solver = SDEint.osIto(p,solvString,printNum=printNum)
        elif solvString in SDEint.availableSolvers(solverType='osStrat'):
            solver = SDEint.osStrat(p,solvString,printNum=printNum)
        elif solvString in SDEint.availableSolvers(solverType='comSolver'):
            solver = SDEint.comSolver(p,solvString,printNum)

        #Calculates absolute error at last element for 1,2,4,8,16 dt.
        M = p.totSimNum
        dt = p.h
        N  = p.n
        if p.trueSol != None:
            Xtrue = p.trueX
        else:
            Xtrue = SDEint.manualSolver(p,p.tFine,p.dWFine)
        self.Xerr = np.zeros((M,5)) # preallocate array
        task = ('Computing strong convergence for solver '+solvString)
        for sim in range(M): # sample over discrete Brownian paths
            dW = p.dW[:,:,sim]
            W = p.W[:,:,sim]
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
                    Xtemp = Xtemp2
                tmp = Xtrue[-1,:,sim]
                err = np.linalg.norm(Xtemp - tmp)
                self.Xerr[sim,n] = err
            update_progress(sim/M)
        print(" ",end='')
        #Does least squares to calculate convergence coefficent.
        DtVals = dt*2**np.array(range(0,5))
        ones = np.ones(len(DtVals))
        A = np.vstack([ones,np.log(DtVals)]).T
        XerrMean = np.mean(self.Xerr,axis=0)
        y = np.log(XerrMean)
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
        plt.xlabel('stepsize dt',fontsize=20)
        plt.ylabel('Mean square norm of error',fontsize=20)
        plt.title('Loglog of strong convergence for solver '+ solvString,
            fontsize=20) 
        plt.legend(loc='upper left',fontsize = fontsize)
        print("fontsize = ",fontsize)

class weakCon:
    """Container class for calculating weak OOC for 1 solver."""
    def __init__(self, p, solvString, printNum=False, M = 50000,fontsize = 30):
        if p.n % 16 != 0:
            print("len(t) needs to be divisible by 16 for convergence "
                ,"analysis.")
            return
        if solvString in SDEint.availableSolvers(solverType='osIto'):
            solver = SDEint.osIto(p,solvString,printNum=printNum)
        elif solvString in SDEint.availableSolvers(solverType='osStrat'):
            solver = SDEint.osStrat(p,solvString,printNum=printNum)
        elif solvString in SDEint.availableSolvers(solverType='comSolver'):
            solver = SDEint.comSolver(p,solvString,printNum)

        from scipy.stats import norm
        #Calculates absolute error at last element for 1,2,4,8,16 dt.
        res, d = 5, p.d
        dt = p.h
        Xem = np.zeros((5,1))# preallocate arrays
        Xerr = np.zeros((res,p.d))
        EndExp = p.expX[-1]
        DtVals = []
        for i in range(res):#take various Euler timesteps
            DtVals.append(dt*(2**(i)))
            L = int(p.t[-1]/DtVals[i])# L Euler steps of size DtVals[i]
            Xtemp = np.ones((d,M))#Currently only supports d=1
            t = 0
            for j in range(L):
                Winc = np.sqrt(DtVals[i])*norm.ppf(np.random.rand(p.m,M))
                Xtemp = solver.solver(p,Xtemp,t,DtVals[i],Winc)
                t = t + DtVals[i]
                update_progress((j/L+i)/res)
            Xem[i] = np.mean(Xtemp,axis=1)
            Xerr[i] = np.linalg.norm(Xem[i] - EndExp)
        print(" ",end='')
        Xerr = Xerr/res
        #Does least squares to calculate convergence coefficent.
        ones = np.ones(len(DtVals))
        A = np.vstack([ones,np.log(DtVals)]).T
        y = np.log(Xerr)
        self.OOC, self.res, rank, s = np.linalg.lstsq(A,y)
        np.set_printoptions(precision=6)
        string = ("\n" + solvString +
            " has an estimated weak order of convergence of "+str(self.OOC[1])
        + " with a residual of {0:.6f}".format(
                self.res[0]))
        print(string)
        
        plt.figure()
        plt.loglog(DtVals,(DtVals**self.OOC[1]),label='Least squares line')
        plt.loglog(DtVals,Xerr,label='Error at end point',
            marker = 'x')
        plt.xlabel('stepsize dt',fontsize=20)
        plt.ylabel('Mean square norm of error',fontsize=20)
        plt.title('Loglog of weak convergence for solver '+ solvString,
            fontsize=20) 
        plt.legend(loc='upper left', fontsize = fontsize)

class stability:
    '''Container class for calculating stability function for 1 solver.'''
    def __init__(self,p,solverString,theta=0.5):
        if not p.checkTest:
            print("Stability plot only implemented for scalar test equation.")
            return
        self.theta = theta
        lowX, hiX = -4,4
        lowY, hiY = 0, 8
        nX, nY = 900,900
        Xvals = np.linspace(lowX,hiX,nX)
        Yvals = np.linspace(lowY,hiY,nY)
        self.X, self.Y = np.meshgrid(Xvals,Yvals)

        solvers = ["itoEM", "itoTheta","itoBackwardsEuler","itoPlaten",
        "itoMilstein11"]
        self.R = np.zeros(self.X.shape)
        if solverString == 'itoEM':
            self.R = RItoEM(self.X,self.Y)
        elif solverString == "itoTheta":
            self.R = RItoTheta(self.X,self.Y,theta=theta)
        elif solverString == 'itoBackwardsEuler':
            self.R = RItoTheta(self.X,self.Y,theta=1)
        elif solverString == 'itoPlaten' or solverString == 'itoMilstein11':
            self.R = RItoStrong1(self.X,self.Y)
        else:
            print("Something has gone horribly wrong in stability.__init__")
            return

def Rborder(X,Y):
    '''Calculates stability area for scalar test equation.'''
    R = np.zeros(X.shape)
    for i in range(len(X)):#Should be possible to do as a list comprehension.
        for j in range(len(Y)):
            if (2*X[i,j]+Y[i,j]) < 0:
                R[i,j] = 1
    return R

def RItoEM(X,Y):
    '''Calculates stability function for ItoEM for scalar test equation.'''
    return np.abs(1+X)**2+np.abs(Y)

def RItoTheta(X,Y,theta=0.5):
    '''Calculates stability function for ItoTheta for scalar test equation.'''
    return (np.abs(1+(1-theta)*X)**2+np.abs(Y))/((np.abs(1-theta*X))**2)

def RItoStrong1(X,Y):
    '''Calculates stability function for Milstein for scalar test equation.'''
    return np.abs(1+X)**2+np.abs(Y)+0.5*np.abs(Y**2)

def update_progress(progress,task='Progress of task'):
    '''Edits 1 line in terminal to display progress. Progress is in [0,1]'''
    print("\rProgress of task: [{0:50s}] {1:.1f}%".format('#' *
        int(progress * 50),progress*100), end="", flush=True)