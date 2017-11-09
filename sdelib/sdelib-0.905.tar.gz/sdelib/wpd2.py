import numpy as np
import matplotlib.pyplot as plt
import SDEproblem
import SDEint
from timeit import default_timer as timer

N = [2**i for i in range(2,6)]
print("N: ",N)
X0 = np.array([1,0])
a,b = np.array([[-5,5],[5,-5]]), np.array([[0.01,0],[0,0.01]])
def f(X, t):
    return a@X
def gk(X, t):
    return b@X

g = [gk]
t = np.linspace(0,1,N[-1]+1)
prob = SDEproblem.SDEprob(f=f,g=g,X0=X0,t=t,name="GBM2d",nFine = N[-1],
trueSol="Autonomous and multiplicative",totSimNum=500)#Creates problem object.
solvers = SDEint.availableSolvers(problem=prob)
endPoint = prob.trueX[-1]
errorDict = {}
probSolv = SDEint.osIto(prob)#Creates one-step Ito solver object for prob.
for solver in solvers:
    error = np.zeros((len(N)))
    compTime = np.zeros((len(N)))
    factor = 1
    for i in range(len(N)):
        W0 = np.zeros((1,prob.m,prob.totSimNum))
        new_t = prob.reduceTime(t,factor)
        new_W = prob.reducedW(prob.W,factor)
        new_dW = new_W[1:len(new_W)]-new_W[:len(new_W)-1]
        new_dW = np.concatenate((W0,new_dW),axis=0)
        probSolv.setSolver(solver)
        start = timer()
        [new_t,X] = probSolv.manualSolve(prob,new_t,new_dW)
        end = timer()
        compTime[i] = end-start
        factor = factor*2
        error[i] = np.mean((endPoint-X[-1])**2)
    errorDict[solver] = (compTime,error,len(new_t))
    plt.loglog(compTime,error,"o-",basex=2,basey=2,label=solver)
    plt.xlabel('Computation time (s)',fontsize=20)
    plt.ylabel('End point mean square error',fontsize=20)
    titleString = ("WPD, dX(t)="+str(a)+"Xdt+"+str(b)
        +"XdW(t), len(t) from "+str(N[0])+" to "+str(N[-1])+".")
    plt.title(titleString,fontsize=20)
plt.legend(loc='best',fontsize=30)
plt.show()