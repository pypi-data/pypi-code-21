# *****************************************************
# * FinX is a set of tools for Financial Data Science *
# * Copyright (C) 2017  Fite Analytics LLC            *
# *****************************************************
#
# This file is part of FinX.
#
#     FinX is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     FinX is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with FinX.  If not, see <http://www.gnu.org/licenses/>.
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import init_notebook_mode, iplot
import pandas as pd
import numpy as np
import scipy.stats
import inspect
import random
import math

def GarmanKlass(prices, window):
    log_hl = (prices['high_price']/prices['low_price']).apply(np.log)
    log_co = (prices['close_price']/prices['open_price']).apply(np.log)
    rs = 0.5 * log_hl ** 2 - (2 * math.log(2) - 1) * log_co ** 2
    def f(v):
        return math.sqrt(252 * v.mean())
    result = rs.rolling(window=window, center=False).apply(func=f)
    result[:window - 1] = np.nan
    return result

def HodgesTompkins(prices, window=30):
    log_return = (prices['close_price']/prices['close_price'].shift(1)).apply(np.log)
    vol = log_return.rolling(window=window, center=False).std() * math.sqrt(252)
    adj_factor = math.sqrt((1.0 / (1.0 - (window / (log_return.count() - (window - 1.0))) + (window ** 2 - 1.0) / (
    3.0 * (log_return.count() - (window - 1.0)) ** 2))))
    result = vol * adj_factor
    result[:window - 1] = np.nan
    return result

def Kurtosis(prices, window=30):
    log_return = (prices['close_price'] / prices['close_price'].shift(1)).apply(np.log)
    result = log_return.rolling(window=window, center=False).kurt()
    result[:window - 1] = np.nan
    return result

def Parkinson(prices, window=30):
    rs = (1 / (4 * math.log(2))) * ((prices['high_price'] / prices['low_price']).apply(np.log)) ** 2
    def f(v):
        return math.sqrt(252 * v.mean())
    result = rs.rolling(window=window, center=False).apply(func=f)
    result[:window - 1] = np.nan
    return result

def Raw(prices, window=30):
    log_return = (prices['close_price'] / prices['close_price'].shift(1)).apply(np.log)
    result = log_return.rolling(window=window, center=False).std() * math.sqrt(252)
    result[:window - 1] = np.nan
    return result

def RodgersSatchell(prices, window=30):
    log_ho = (prices['high_price'] / prices['open_price']).apply(np.log)
    log_lo = (prices['low_price'] / prices['open_price']).apply(np.log)
    log_co = (prices['close_price'] / prices['open_price']).apply(np.log)
    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    def f(v):
        return math.sqrt(252 * v.mean())
    result = rs.rolling(window=window, center=False).apply(func=f)
    result[:window - 1] = np.nan
    return result

def Skew(prices, window=30):
    log_return = (prices['close_price'] / prices['close_price'].shift(1)).apply(np.log)
    result = log_return.rolling(window=window, center=False).skew()
    result[:window - 1] = np.nan
    return result

def YangZhang(prices, window=30):
    log_ho = (prices['high_price'] / prices['open_price']).apply(np.log)
    log_lo = (prices['low_price'] / prices['open_price']).apply(np.log)
    log_co = (prices['close_price'] / prices['open_price']).apply(np.log)
    log_oc = (prices['open_price'] / prices['close_price'].shift(1)).apply(np.log)
    log_oc_sq = log_oc ** 2
    log_cc = (prices['close_price'] / prices['close_price'].shift(1)).apply(np.log)
    log_cc_sq = log_cc ** 2
    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    close_vol = log_cc_sq.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    open_vol = log_oc_sq.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    window_rs = rs.rolling(window=window, center=False).sum() * (1.0 / (window - 1.0))
    result = (open_vol + 0.164333 * close_vol + 0.835667 * window_rs).apply(np.sqrt) * math.sqrt(252)
    result[:window - 1] = np.nan
    return result

def compute_d1_and_d2(s,x,t,r,v,q):
    d1 = (np.log(s/x)+t*(r-q+(v**2)/2))/(v*math.sqrt(t))
    d2 = d1 - v*math.sqrt(t)
    return d1, d2

def delta(option_side,t,q,d1):
    if option_side is 'call':
        return np.exp(-q*t)*scipy.stats.norm.cdf(d1)
    else:
        return np.exp(-q*t)*(scipy.stats.norm.cdf(d1)-1)

def gamma(s,t,v,q,d1):
    return (np.exp(-q*t)*np.exp(-d1**2/2))/(s*v*math.sqrt(2*t*math.pi))

def theta(option_side,s,q,t,v,r,x,d1,d2,calendar_days):
    theta_part_1 = -(s*v*np.exp(-q*t)*np.exp(-d1**2/2)*(1/math.sqrt(2*math.pi))/(2*math.sqrt(t)))
    if option_side is 'call':
        theta_part_2 = -(r*x*np.exp(-r*t)*scipy.stats.norm.cdf(d2))
        theta_part_3 = q*s*np.exp(-q*t)*scipy.stats.norm.cdf(d1)
    else:
        theta_part_2 = (r*x*np.exp(-r*t)*scipy.stats.norm.cdf(-d2))
        theta_part_3 = -q*s*np.exp(-q*t)*scipy.stats.norm.cdf(-d1)
    if calendar_days is True:
        total_theta = (theta_part_1+theta_part_2+theta_part_3)/365
    else:
        total_theta = (theta_part_1+theta_part_2+theta_part_3)/252
    return total_theta

def rho(option_side,x,t,r,d2):
    if option_side is 'call':
        return (x*t*np.exp(-r*t)*scipy.stats.norm.cdf(d2))/100
    else:
        return (x*t*np.exp(-r*t)*scipy.stats.norm.cdf(-d2))/100

def vega(s,q,t,d1):
    return (s*np.exp(-q*t)*math.sqrt(t)*np.exp(-d1**2/2)*(1/math.sqrt(2*math.pi)))/100

def volga(s,q,t,v,d1,d2):
    return vega(s,q,t,d1)*(d1*d2)/(s*v)

def vanna(q,t,v,d1,d2):
    return -np.exp(-q*t)*(d2/v)*np.exp(-d1**2/2)/(math.sqrt(2*math.pi))

def greeks(option_side,stock_price,strike_price,days_to_expiry,risk_free_rate,sigma,dividend_yield=0,calendar_days=True):
    greek_dict = {}
    if calendar_days is True:
        days_to_expiry = days_to_expiry/365
    else:
        days_to_expiry = days_to_expiry/252
    d1, d2 = compute_d1_and_d2(stock_price, strike_price, days_to_expiry, risk_free_rate, sigma, dividend_yield)
    greek_dict['delta'] = delta(option_side, days_to_expiry, dividend_yield, d1)
    greek_dict['gamma'] = gamma(stock_price, days_to_expiry, sigma, dividend_yield, d1)
    greek_dict['theta'] = theta(option_side, stock_price, dividend_yield, days_to_expiry, sigma, risk_free_rate, strike_price, d1, d2, calendar_days)
    greek_dict['rho'] = rho(option_side, strike_price, days_to_expiry, risk_free_rate, d2)
    greek_dict['vega'] = vega(stock_price, dividend_yield, days_to_expiry, d1)
    greek_dict['volga'] = volga(stock_price, dividend_yield, days_to_expiry, sigma, d1, d2)
    greek_dict['vanna'] = vanna(dividend_yield, days_to_expiry, sigma, d1, d2)
    return pd.DataFrame(greek_dict, index=['Greek Calculations'])

def volatility(series, method, window):
    if method is 'GarmanKlass':
        estimate = GarmanKlass(series, window)
    elif method is 'HodgesTompkins':
        estimate = HodgesTompkins(series, window)
    elif method is 'Kurtosis':
        estimate = Kurtosis(series, window)
    elif method is 'Parkinson':
        estimate = Parkinson(series, window)
    elif method is 'Raw':
        estimate = Raw(series, window)
    elif method is 'RogersSatchell':
        estimate = RodgersSatchell(series, window)
    elif method is 'Skew':
        estimate = Skew(series, window)
    elif method is 'YangZhang':
        estimate = YangZhang(series, window)
    else:
        return 'Invalid Method'
    return pd.DataFrame(estimate, columns=[method])

def volatility(series, method, window):
    if method is 'GarmanKlass':
        estimate = GarmanKlass(series, window)
    elif method is 'HodgesTompkins':
        estimate = HodgesTompkins(series, window)
    elif method is 'Kurtosis':
        estimate = Kurtosis(series, window)
    elif method is 'Parkinson':
        estimate = Parkinson(series, window)
    elif method is 'Raw':
        estimate = Raw(series, window)
    elif method is 'RogersSatchell':
        estimate = RodgersSatchell(series, window)
    elif method is 'Skew':
        estimate = Skew(series, window)
    elif method is 'YangZhang':
        estimate = YangZhang(series, window)
    else:
        return 'Invalid Method'
    return pd.DataFrame(estimate, columns=[method])

def volatility_cones(series, method, windows=[30, 60, 90, 120], quantiles=[0.25, 0.75]):
    """Plots volatility cones
    Parameters
    ----------
    windows : [int, int, ...]
        List of rolling windows for which to calculate the estimator cones
    quantiles : [lower, upper]
        List of lower and upper quantiles for which to plot the cones
    """

    if len(windows) < 2:
        raise ValueError('Two or more window periods required')
    if len(quantiles) != 2:
        raise ValueError('A two element list of quantiles is required, lower and upper')
    if quantiles[0] + quantiles[1] != 1.0:
        raise ValueError('The sum of the quantiles must equal 1.0')
    if quantiles[0] > quantiles[1]:
        raise ValueError(
            'The lower quantiles (first element) must be less than the upper quantile (second element)')
    _max = []
    _min = []
    top_q = []
    median = []
    bottom_q = []
    realized = []
    data = []
    for w in windows:
        try:
            estimate = volatility(series, method, w)
            if len(estimate.dropna()) > 0:
                _max.append(estimate.max()[0])
                top_q.append(estimate.quantile(quantiles[1])[0])
                median.append(estimate.median()[0])
                bottom_q.append(estimate.quantile(quantiles[0])[0])
                _min.append(estimate.min()[0])
                realized.append(list(estimate.values)[-1][0])
                data.append([estimate, w])
            else:
                print('Window of size '+str(w)+' is too large for series')
        except:
            print('Window of size '+str(w)+' does not work with series')
    if method is "Skew" or method is "Kurtosis":
        f = lambda x: "%i" % round(x, 0)
    else:
        f = lambda x: "%i%%" % round(x * 100, 0)
    init_notebook_mode(connected=True)
    r = lambda: random.randint(0, 255)
    random_line_color = lambda: '#{}02X{}02X{}02X'.format(r(), r(), r())
    new_windows = [data[i][1] for i in range(len(data))]
    max_trace = go.Scatter(
        x=new_windows,
        y=_max,
        name = 'max',
        mode='line',
        marker=dict(size=12,line=dict(color=random_line_color())))
    min_trace = go.Scatter(
        x=new_windows,
        y=_min,
        name = 'min',
        mode='line',
        marker=dict(size=12,line=dict(color=random_line_color())))
    top_q_trace = go.Scatter(
        x=new_windows,
        y=top_q,
        name = 'top_q',
        mode='line',
        marker=dict(size=12,line=dict(color=random_line_color())))
    median_trace = go.Scatter(
        x=new_windows,
        y=median,
        name = 'median',
        mode='line',
        marker=dict(size=12,line=dict(color=random_line_color())))
    bottom_q_trace = go.Scatter(
        x=new_windows,
        y=bottom_q,
        name = 'bottom_q',
        mode='line',
        marker=dict(size=12,line=dict(color=random_line_color())))
    fig = tools.make_subplots(rows=1, cols=2, shared_yaxes=True)
    fig.append_trace(max_trace, 1, 1)
    fig.append_trace(min_trace, 1, 1)
    fig.append_trace(top_q_trace, 1, 1)
    fig.append_trace(median_trace, 1, 1)
    fig.append_trace(bottom_q_trace, 1, 1)
    for i in range(len(data)):
        if len(data[i][0][method].dropna()) > 0:
            box_trace = go.Box(x=data[i][1],
                               y=data[i][0][method],
                               name='Window: '+str(data[i][1]))
            fig.append_trace(box_trace, 1, 2)
    realized_trace = go.Scatter(x=new_windows,
                                y=realized,
                                name='realized',
                                mode='line',
                                marker=dict(size=12,line=dict(color=random_line_color())))
    fig.append_trace(realized_trace, 1, 1)
    fig['layout'].update(title='Volatility Cones')
    fig['layout']['xaxis1'].update(title='Window', domain=[0,0.7])
    fig['layout']['xaxis2'].update(domain=[0.7,1])
    fig['layout']['yaxis1'].update(title='Volatility')
    iplot(fig, show_link=False, config=dict(displaylogo=False,modeBarButtonsToRemove=['sendDataToCloud']))
    return None
VALID_FUNCTION_CALLS = ['greeks',
                        'volatility',
                        'volatility_cones']

def get_function_call_params(function_call=False, valid_function_calls=False):
    function_call_to_params_map = dict()
    for function_call_key in VALID_FUNCTION_CALLS:
        fun = inspect.getfullargspec(eval(function_call_key))
        params_list = list()
        if fun.args:
            no_default = 'no inspected default'
            fun_defaults = list(fun.defaults)
            fun_defaults = [no_default] * (len(fun.args) - len(fun.defaults)) + fun_defaults
            for param, default in zip(fun.args, fun_defaults):
                if default is not no_default:
                    param = '{} (default={})'.format(param, default)
                params_list.append(param)
            if fun.varargs:
              params_list.append('*' + fun.varargs)
            if fun.varkw:
              params_list.append('**' + fun.varkw)
        if fun.kwonlydefaults:
          params_list.append('*' + fun.varargs)
          parsed_kwonly = ['{} (defaults={})'.format(key, value)
                           for key, value in fun.kwonlydefaults.items()]
          params_list.extend(parsed_kwonly)
        if not fun.args and not fun.kwonlydefaults and fun.varargs:
            params_list.append('*' + fun.varargs)
        function_call_to_params_map[function_call_key] = params_list
    if bool(valid_function_calls):
        return list(function_call_to_params_map.keys())
    if bool(function_call):
        return function_call_to_params_map[function_call]

def help(*function_calls):
    print('-------------------------------------')
    print('fiteanalytics.finx.analyze help')
    print('-------------------------------------')
    print('Functions in this package provide analysis of large data sets')
    print('-------------------------------------')
    valid_function_calls = get_function_call_params(valid_function_calls=True)
    if not function_calls:
        print("\033[1mValid function calls are\033[0m:\n\t\t\t• {}"
              .format("\n\t\t\t• ".join(valid_function_calls[:])))
        function_calls = valid_function_calls
    for function_call in function_calls:
        try:
            params = get_function_call_params(function_call)
            if isinstance(params, tuple) or isinstance(params, list):
                print("Parameters for \033[1m{}\033[0m:\n\t\t\t• {}"
                      .format(function_call, "\n\t\t\t• ".join(params[:])))
            else:
                print("Parameters for \033[1m{}\033[0m:\n\t\t\t• {}"
                      .format(function_call, params))
        except:
            print("\033[1mValid function calls are\033[0m:\n\t\t\t• {}"
                  .format("\n\t\t\t• ".join(valid_function_calls[:])))
            return "error: function {} does not exist".format(function_call)


