"""Maths functions"""


__version__ = '2017.11.1'


def update_mean(n: int, mean: float, value: float) -> float:
    new_mean = mean + (value - mean) / (n + 1)
    return new_mean


def update_pvariance(n: int, mean: float, var: float, value: float) -> float:
    Q = var * n
    new_mean = update_mean(n, mean, value)
    Q = Q + (value - mean) * (value - new_mean)
    return Q / (n + 1)


def update_variance(n: int, mean: float, var: float, value: float) -> float:
    Q = var * (n - 1)
    new_mean = update_mean(n, mean, value)
    Q = Q + (value - mean) * (value - new_mean)
    return Q / n
