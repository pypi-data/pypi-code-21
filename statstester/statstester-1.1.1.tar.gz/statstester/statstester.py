#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import numpy as np
import math
import pandas as pd
from scipy import stats


def standard_deviation_by_least_squared_method(x, y):
    return math.sqrt((syy(y) - calc_slope(x,y)*sxy(x, y))/(len(x)-2))


def calc_slope(x, y):
    slope = sxy(x, y) / sxx(x)
    return slope


def calc_intercept(x, y):
    intercept = (sum(y) - calc_slope(x, y) * sum(x)) / len(x)
    return intercept


def sigma_calc_slope(x, y):
    return standard_deviation_by_least_squared_method(x, y) / math.sqrt(sxx(x, y))


def sigma_calc_intercept(x, y):
    return standard_deviation_by_least_squared_method(x, y) * math.sqrt(sum(x**2) / (len(n) * sxx(x)))


def coefficient_of_determination(x, y): 
    r = correlation_coefficient(x, y)
    return r**2


def correlation_coefficient(x, y):
    r = sxy(x, y)/ sxx(x) / syy(y)
    return r


def deviation_sum_of_products(x, y):
    if len(x) != len(y):
        try:
            raise Exception
        except:
            pass
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    _deviation_sum_of_products = sum((x - x_mean) * (y - y_mean))
    return _deviation_sum_of_products


def sum_of_squared_deviations(x):
    return deviation_sum_of_products(x, x)


def sxy(x, y):
    return deviation_sum_of_products(x, y)
    

def syy(y):
    return sum_of_squared_deviations(y)


def sxx(x):
    return sum_of_squared_deviations(x)

def tdistribution(nsample, alpha):
    # The code which are written below will be deleted.
    ''' 
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../input/data/tdistribution.csv'))
    if alpha == 0.1:
        key_alpha = '0.1'
    elif alpha == 0.05:
        key_alpha = '0.05'
    elif alpha == 0.025:
        key_alpha = '0.025'
    else:
        return 'Alpha is Error!!!'
    return df[key_alpha][nsample]
    '''
    return stats.t.isf(alpha/2.0, nsample)
    

def two_line_t_test(data0, data1, alpha = 0.05):
    """  Checking the relation between two data using t-test/
    x0, y0: data 0
    x1, y1: data 1
    """
    x0, y0 = data0
    x1, y1 = data1
    n0 = len(x0)
    n1 = len(x1)

    s0 = standard_deviation_by_least_squared_method(x0, y0)
    s1 = standard_deviation_by_least_squared_method(x1, y1)
    s_ = math.sqrt(((n0 - 2) * (s0**2)+(n1 - 2) * (s1**2)) / (n0 + n1 - 4))

    # Test for Slope
    b0 = calc_slope(x0, y0)
    b1 = calc_slope(x1, y1)
    sb0b1 = s_ * math.sqrt(1 / sxx(x0) + 1 / sxx(x1))
    t_slope = (b0 - b1) / sb0b1
    tval = tdistribution(n0 + n1 - 4, alpha)
    if abs(t_slope) > tval:
        print('[ Slope ] | t value:{} | > t_inv value:{} means that it is significant by {}.'.format(t_slope, tval, alpha))
    else:
        print('[ Slope ] | t value:{} | < t_inv value:{} means that it is NOT significant by {}.'.format(t_slope, tval, alpha))


    # Test for Intercept
    a0 = calc_intercept(x0, y0)
    a1 = calc_intercept(x1, y1)
    sa0sa1 = s_ * math.sqrt(sum(x0 ** 2) / (n0 * sxx(x0)) + sum(x1 ** 2) / (n1 * sxx(x1)))
    t_intercept = (a0 - a1) / sa0sa1
    tval = tdistribution(n0 + n1 - 4, alpha)
    if abs(t_intercept) > tval:
        print('[ Intercept ] | t value:{} | > t_inv value:{} means that it is significant by {}.'.format(t_intercept, tval, alpha))
    else:
        print('[ Intercept ] | t value:{} | < t_inv value:{} means that it is NOT significant by {}.'.format(t_intercept, tval, alpha))


def t_test(x, y, equal_var = True):
    """ the Alias of scipy.stats.ttest_ind().
    If there is no option, this function calculate the t value assuming the equal variances.
    return t value and p value.
    """
    return stats.ttest_ind(x, y, equal_var = equal_var)

def f_test(x, y):
    """ the Alias of scipy.stats.f.cdf().
    """
    f = np.var(x)/np.var(y)
    return stats.f.cdf(f, len(x)-1, len(y)-1)
    

