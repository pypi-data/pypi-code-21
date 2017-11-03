# -*- coding:utf-8 -*-
# writen by ChuanyuXue

import numpy

def _F(x, X):
    return len(X[X <= x]) / len(X)

def _Fr(x, y, X, Y):
    return len(X[(X <= x) & (Y == y)]) / len(Y[Y == y])

def _Pr(y, Y):
    return len(Y[Y == y]) / len(Y)

def mvtest(X, Y):
    X = numpy.array(X)
    Y = numpy.array(Y)
    if(len(X) == len(Y)):
        length = len(X)
        RVec = numpy.unique(Y)
        result = 0

        for y in RVec:
            for x in X:
                result += _Pr(y, Y) * numpy.square(_Fr(x, y, X, Y) - _F(x, X))
        return result / length
    else:
        raise Exception("Two vectors must be equal to the same dimention vector.")
