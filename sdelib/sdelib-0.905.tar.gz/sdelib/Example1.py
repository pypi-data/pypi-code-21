import numpy as np
import SDEproblem
import SDEint
t = np.linspace(0,1,64)
X0 = np.array([1])
def f(X, t):
    return 1*X
def gk(X, t):
    return 1*X
g = [gk]
prob = SDEproblem.SDEprob(f=f,g=g,X0=X0,t=t,name="GBM1d",
trueSol="Autonomous and multiplicative",totSimNum=1000)#Creates problem object.
solvers = ['itoEM','itoPlaten']
probSolv = SDEint.osIto(prob)#Creates one-step Ito solver object for prob.
for solver in solvers:
    probSolv.solve(solverString = solver)
prob.plotSolutions()