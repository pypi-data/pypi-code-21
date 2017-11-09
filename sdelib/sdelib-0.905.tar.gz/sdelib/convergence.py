import numpy as np
import SDEproblem, SDEint, SDEanalysis
n = 512#Needs to be divisible by 16 to work
t = np.linspace(0,1,n+1)
X0 = np.array([1])
a, b = 2, 0.1
def f(X, t):
    return a*X
def gk(X, t):
    return b*X
def gkk(X,t):
	return b
g = [gk]
g1 = [[gkk]]
prob = SDEproblem.SDEprob(f=f,g=g,g1=g1,X0=X0,totSimNum=1000,t=t,
	name="GBM",trueSol="Autonomous and multiplicative",
	checkTest=True)#Creates problem object.
solvers = SDEint.availableSolvers(problem=prob)#Returns solvers in osIto
#SDEanalysis.calcStrongCon(prob,solvers)#Strong OOC estimation for prob,solvers
#SDEanalysis.calcWeakCon(prob,solvers,M=50000)#Weak OOC est for prob,solvers
SDEanalysis.calcStability(prob,solvers[:-1])#Stability function contour for
#scalar test equation.