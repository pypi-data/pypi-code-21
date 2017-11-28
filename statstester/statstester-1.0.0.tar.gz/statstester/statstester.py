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
    """ xの偏差平方和を返す
    """
    return deviation_sum_of_products(x, x)


def sxy(x, y):
    """ xとyの偏差積和を返す
    """
    return deviation_sum_of_products(x, y)
    

def syy(y):
    """ リストyの偏差平方和を返す
    """
    return sum_of_squared_deviations(y)


def sxx(x):
    """ リストxの偏差平方和を示す。
    """
    return sum_of_squared_deviations(x)

def tdistribution(nsample, alpha):
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
    

def two_line_t_test(data0, data1, alpha = 0.05):
    """ 2つのデータのアイデに相関があるかどうかを調べる。
    x0, y0: 比較元データ列。
    x1, y1: 比較先データ列。

    [Notice]
    >>> from __future__ import print_function
    >>> import numpy as np
    >>> import statsmodels.api as sm
    >>> import matplotlib.pyplot as plt
    >>> from statsmodels.sandbox.regression.predstd import wls_prediction_std
    >>> np.random.seed(9876789)
    >>> nsample = 100
    >>> x = np.linspace(0, 10, 100)
    >>> X = np.column_stack((x, x**2)) 
    >>> beta = np.array([1, 0.1, 10])
    >>> e = np.random.normal(size=nsample)
    >>> X = sm.add_constant(X)
    >>> y = np.dot(X, beta) + e 
    >>> model = sm.OLS(y, X) # これ、x1, x2に対するyのfit。
    >>> results = model.fit()
    >>> print(results.summary())
    OLS Regression Results    
    略
    >>> print(dir(results))
    ['HC0_se', 'HC1_se', 'HC2_se', 'HC3_se', '_HCCM', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_cache', '_data_attr', '_get_robustcov_results', '_is_nested', '_wexog_singular_values', 'aic', 'bic', 'bse', 'centered_tss', 'compare_f_test', 'compare_lm_test', 'compare_lr_test', 'condition_number', 'conf_int', 'conf_int_el', 'cov_HC0', 'cov_HC1', 'cov_HC2', 'cov_HC3', 'cov_kwds', 'cov_params', 'cov_type', 'df_model', 'df_resid', 'diagn', 'eigenvals', 'el_test', 'ess', 'f_pvalue', 'f_test', 'fittedvalues', 'fvalue', 'get_influence', 'get_prediction', 'get_robustcov_results', 'initialize', 'k_constant', 'llf', 'load', 'model', 'mse_model', 'mse_resid', 'mse_total', 'nobs', 'normalized_cov_params', 'outlier_test', 'params', 'predict', 'pvalues', 'remove_data', 'resid', 'resid_pearson', 'rsquared', 'rsquared_adj', 'save', 'scale', 'ssr', 'summary', 'summary2', 't_test', 'tvalues', 'uncentered_tss', 'use_t', 'wald_test', 'wald_test_terms', 'wresid']    
    """

    
    x0, y0 = data0
    x1, y1 = data1
    n0 = len(x0)
    n1 = len(x1)

    s0 = standard_deviation_by_least_squared_method(x0, y0)
    s1 = standard_deviation_by_least_squared_method(x1, y1)
    s_ = math.sqrt(((n0 - 2) * (s0**2)+(n1 - 2) * (s1**2)) / (n0 + n1 - 4))

    # 傾きの差の検定
    b0 = calc_slope(x0, y0)
    b1 = calc_slope(x1, y1)
    sb0b1 = s_ * math.sqrt(1 / sxx(x0) + 1 / sxx(x1))
    t_slope = (b0 - b1) / sb0b1 # 自由度(n0 + n1 - 4)のt分布
    tval = tdistribution(n0 + n1 - 4, alpha)
    if abs(t_slope) > tval:
        print('t値:{}の絶対値 > t:{}より傾きの差は{}で有意。'.format(t_slope, tval, alpha))
    else:
        print('t値:{}の絶対値 < t:{}より傾きの差は{}で有意ではない。'.format(t_slope, tval, alpha))


    # 切片の差の検定
    a0 = calc_intercept(x0, y0)
    a1 = calc_intercept(x1, y1)
    sa0sa1 = s_ * math.sqrt(sum(x0 ** 2) / (n0 * sxx(x0)) + sum(x1 ** 2) / (n1 * sxx(x1)))
    t_intercept = (a0 - a1) / sa0sa1
    tval = tdistribution(n0 + n1 - 4, alpha)
    if abs(t_intercept) > tval:
        print('t値:{}の絶対値 > t:{}より切片の差は{}で有意。'.format(t_intercept, tval, alpha))
    else:
        print('t値:{}の絶対値 < t:{}より切片の差は{}で有意ではない。'.format(t_intercept, tval, alpha))


def t_test(x, y, equal_var = True):
    """ t検定を行う。
    指定がなければ、全ては等しい分散として扱う。
    t値とp値（確率）を返す。
    """
    return stats.ttest_ind(x, y, equal_var = equal_var)

def f_test(x, y):
    """ f検定を行う。
    """
    f = np.var(x)/np.var(y)
    return stats.f.cdf(f, len(x)-1, len(y)-1)
    

