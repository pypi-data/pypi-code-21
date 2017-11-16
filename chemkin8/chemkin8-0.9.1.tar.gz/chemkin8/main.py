import numpy as np
from chemkin import *
from parser import *


# Input variables
x1 = [2., 1., .5, 1., 1., 1.]
x2 = [2., 1., .5, 1., 1., 1., .5, 1.]
T = 1500


fname1 = 'test_cases/rxns.xml'
fname2 = 'test_cases/rxnset_long.xml'
fname3 = 'test_cases/rxns_reversible.xml'

c = chemkin(fname1)
print(c.reaction_rates(x1, T))

c = chemkin(fname2)
print(c.reaction_rates(x2, T))

c = chemkin(fname3)
print(c.reaction_rates(x2, T))

