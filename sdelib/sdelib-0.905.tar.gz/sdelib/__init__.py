import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
from .SDEint import osIto, availableSolvers
from .SDEproblem import SDEprob
from .SDEanalysis import calcStrongCon, calcWeakCon
from .SDEspecification import SDEspec
from .GUI import calcSolver, chooseSolvers, FullExampSpec, mainWin, newF
from .GUI import newG, newFunc, newReal, newSpec
#import gui