import numpy as np


def sgn(x):
    return 1 if x > 0 else 0


def sign(x):
    return 1 if x > 0 else (-1 if x < 0 else x)


def dsign(x):
    return 1


def dsgn(x):
    return 1


def logistic(x, alpha):
    return 1/(1 + np.exp(-alpha * x))


def dlogistic(x, alpha):
    return alpha * logistic(x, alpha) * (1 - logistic(x, alpha))


def rbf_gauss(r, sigma):
    return np.exp(-r**2 / (2 * (sigma[0][0])**2))


def x(x, alpha=1):
    return x*alpha


def drbf_gauss(r, sigma=0.1):
    return np.exp(-r**2 / (2 * sigma**2)) * (-r)


def rbf_green(x, SIGMA):
    return np.exp(- x.dot(SIGMA).dot(np.transpose(x)))


def drbf_green(x, SIGMA):
    return - 2 * np.sqrt(x.dot(SIGMA).dot(np.transpose(x))) *\
            np.exp(- x.dot(SIGMA).dot(np.transpose(x)))


ACTIVATION = {
    'sgn': sgn,
    'sign': sign,
    'logistic': logistic,
    'rbf_gauss': rbf_gauss,
    'rbf_green': rbf_green,
    'x': x
}
FIRST_DERIVATIVES = {
    'sgn': dsgn,
    'sign': dsign,
    'logistic': dlogistic,
    'rbf_gauss': drbf_gauss,
    'rbf_green': drbf_green
}

