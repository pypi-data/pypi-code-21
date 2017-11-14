import numpy as np
import pylab as pl

from jacobi.jacobi import Yakobi


def runYakobiWithRandomArgs():
    k = np.random.randint(5, 15)
    gamma = np.random.random_integers(1, 20, 15)
    betta = np.random.random_integers(1, 20, 15)
    resultN = Yakobi().processN(gamma, betta, k)
    print(f'Step: {k}')
    print(f'Gamma: {gamma}')
    print(f'Betta: {betta}')
    print(f'Res N: {resultN}')
    plotStepsN(range(0, k), resultN)

def plotStepsN(steps, n):
    pl.plot(steps, n, color ='red')
    pl.xlabel('Steps')
    pl.ylabel('N')
    pl.savefig('jacobiPlot.png')
    pl.show()

runYakobiWithRandomArgs()
