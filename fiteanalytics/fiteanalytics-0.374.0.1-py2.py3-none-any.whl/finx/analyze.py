#! python
# -*- coding: utf-8 -*-
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
from __future__ import print_function
from __future__ import unicode_literals
import plotly.graph_objs as go
from plotly import tools
from plotly.offline import init_notebook_mode, iplot
import pandas as pd
import numpy as np
from sklearn import linear_model
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
import inspect
import random

import fiteanalytics.finx.prepare as prepare

# Below functions come from time_series.py
# Below functions come from time_series.py
def test_stationarity(timeseries, window=2):
    try:
        rolmean = timeseries.rolling(window=window).mean()
        rolstd = timeseries.rolling(window=window).std()
        init_notebook_mode(connected=True)
        r = lambda: random.randint(0, 255)
        random_line_color = lambda: '#{}02X{}02X{}02X'.format(r(), r(), r())
        data_trace = go.Scatter(
            x=timeseries.index,
            y=timeseries[timeseries.columns[0]],
            name = 'data',
            mode='line',
            marker=dict(size=12,line=dict(color=random_line_color())))
        mean_trace = go.Scatter(
            x=rolmean.index,
            y=rolmean[rolmean.columns[0]],
            mode='line',
            name = 'rolling mean',
            marker=dict(size=8, line=dict(color=random_line_color())))
        std_trace = go.Scatter(
            x=rolstd.index,
            y=rolstd[rolstd.columns[0]],
            yaxis='y3',
            name = 'rolling std. dev.',
            mode='line',
            marker=dict(size=8, line=dict(color=random_line_color())))
        fig = tools.make_subplots(rows=2, cols=1)
        fig.append_trace(data_trace, 1, 1)
        fig.append_trace(mean_trace, 1, 1)
        fig.append_trace(std_trace, 2, 1)
        fig['layout'].update(title='Rolling Mean and Standard Deviation')
        iplot(fig, show_link=False, config=dict(displaylogo=False,modeBarButtonsToRemove=['sendDataToCloud']))
        dftest = adfuller(timeseries[timeseries.columns[0]], autolag='AIC')
        results = {}
        results['Test Statistic'] = dftest[0]
        results['p-value'] = dftest[1]
        results['Lags Used'] = dftest[2]
        results['Number of Observations Used'] = dftest[3]
        for key, value in dftest[4].items():
            results['Critical value: '+key] = value
        results['icbest'] = dftest[5]
        dfoutput = pd.DataFrame(results, index=['Dickey Fuller Test Results']).T
        return dfoutput
    except:
        return 'time series could not be tested'

def decompose_series(series, frequency=1):
    try:
        decomposition = seasonal_decompose(series, freq=frequency)
        trend = decomposition.trend
        seasonal = decomposition.seasonal
        residual = decomposition.resid
        init_notebook_mode(connected=True)
        r = lambda: random.randint(0, 255)
        random_line_color = lambda: '#{}02X{}02X{}02X'.format(r(), r(), r())
        data_trace = go.Scatter(
            x=series.index,
            y=series[series.columns[0]],
            name = 'original',
            mode='line',
            marker=dict(size=12,line=dict(color=random_line_color())))
        trend_trace = go.Scatter(
            x=trend.index,
            y=trend[trend.columns[0]],
            yaxis='y2',
            name = 'trend',
            mode='line',
            marker=dict(size=12,line=dict(color=random_line_color())))
        seasonal_trace = go.Scatter(
            x=seasonal.index,
            y=seasonal[seasonal.columns[0]],
            yaxis='y3',
            mode='line',
            name = 'seasonal',
            marker=dict(size=8, line=dict(color=random_line_color())))
        residual_trace = go.Scatter(
            x=residual.index,
            y=residual[residual.columns[0]],
            yaxis='y4',
            name = 'residual',
            mode='line',
            marker=dict(size=8, line=dict(color=random_line_color())))
        fig = tools.make_subplots(rows=4, cols=1)
        fig.append_trace(data_trace, 1, 1)
        fig.append_trace(trend_trace, 2, 1)
        fig.append_trace(seasonal_trace, 3, 1)
        fig.append_trace(residual_trace, 4, 1)
        fig['layout'].update(title='Series Decomposition')
        iplot(fig, show_link=False, config=dict(displaylogo=False,modeBarButtonsToRemove=['sendDataToCloud']))
        df = prepare.magic_wrangler([trend, seasonal, residual])
        df.columns = ['trend', 'seasonal', 'residual']
        return df
    except:
        return 'invalid series'

def linear_regression_viz(df, train_fraction, split_random=False):
    r = lambda: random.randint(0, 255)
    random_line_color = lambda: '#{}02X{}02X{}02X'.format(r(), r(), r())
    if len(df.columns) == 1:
        df = pd.DataFrame([pd.to_numeric(df.index), df.values]).T.set_index(df.index)
    regr = linear_model.LinearRegression()
    if split_random is False:
        train, test = prepare.split(df, train_fraction, random=False)
    else:
        train, test = prepare.split(df, train_fraction, random=True)
    regr.fit(train[train.columns[:-1]], train[train.columns[-1:]])
    print('Coefficients: \n', regr.coef_)
    print("Mean squared error: %.2f" % np.mean((regr.predict(train[train.columns[:-1]]) - train[train.columns[-1:]]) ** 2))
    print('R^2: %.2f' % regr.score(test[test.columns[:-1]], test[test.columns[-1:]]))
    dimensions = len(df.columns[:-1])
    init_notebook_mode(connected=True)
    trace_data = []
    if dimensions == 1 :
        trace = go.Scatter(
            x=df[df.columns[0]].values,
            y=df[df.columns[1]].values,
            mode='markers',
            marker=dict(
                size=6,
                line=dict(color=random_line_color())))
        trace_data.append(trace)
        x2 = list(np.arange(df[df.columns[0]].min(), df[df.columns[0]].max(), (df[df.columns[0]].min()+df[df.columns[0]].max())/1000 if (df[df.columns[0]].min()+df[df.columns[0]].max())/200 != 0 else (-df[df.columns[0]].min()+df[df.columns[0]].max())/200))
        df2 = pd.DataFrame({df.columns[0]:x2})
        trace2 = go.Scatter(
            x=x2,
            y=list(i[0] for i in regr.predict(df2)),
            mode='lines',
            marker=dict(size=12, line=dict(color=random_line_color())))
        trace_data.append(trace2)
        layout = dict(title="Linear Regression",
                      xaxis=dict(title=df.columns[0]),
                      yaxis=dict(title=df.columns[-1]))
    if dimensions == 2:
        trace = go.Scatter3d(
            x=df[df.columns[0]].values,
            y=df[df.columns[1]].values,
            z=df[df.columns[2]].values,
            mode='markers',
            marker=dict(
                size=6,
                line=dict(color=random_line_color())))
        trace_data.append(trace)
        x2 = list(np.arange(df[df.columns[0]].min(), df[df.columns[0]].max(), (df[df.columns[0]].min()+df[df.columns[0]].max())/1000 if (df[df.columns[0]].min()+df[df.columns[0]].max())/200 != 0 else (-df[df.columns[0]].min()+df[df.columns[0]].max())/200))
        y2 = list(np.arange(df[df.columns[0]].min(), df[df.columns[0]].max(), (df[df.columns[0]].min()+df[df.columns[0]].max())/1000 if (df[df.columns[0]].min()+df[df.columns[0]].max())/200 != 0 else (-df[df.columns[0]].min()+df[df.columns[0]].max())/200))
        df2 = pd.DataFrame({df.columns[0]: x2, df.columns[1]: y2})
        trace2 = go.Scatter3d(
            x=x2,
            y=y2,
            z=list(i[0] for i in regr.predict(df2)),
            mode='lines',
            marker=dict(
                size=12,
                line=dict(color=random_line_color())))
        trace_data.append(trace2)
        layout = dict(title="Linear Regression",
                      xaxis=dict(title=df.columns[0]),
                      yaxis=dict(title=df.columns[1]))
    try:
        fig = dict(data=trace_data, layout=layout)
        iplot(fig,
              show_link=False,
              config=dict(displaylogo=False, modeBarButtonsToRemove=['sendDataToCloud']))
    except:
        return 'dataframe has too many columns this function can only plot up to 3 columns'
    return None

def linear_regression_raw(df=None, train_fraction=None, split_random=False):
    if df is None:
        return 'DataFrame input should not be None'
    if train_fraction is None:
        return 'train_fraction should be a decimal, not None'
    if len(df.columns) == 1:
        df = pd.DataFrame([pd.to_numeric(df.index), df.values]).T.set_index(df.index)
    regr = linear_model.LinearRegression()
    if split_random is False:
        train, test = prepare.split(df, train_fraction, random=False)
    else:
        train, test = prepare.split(df, train_fraction, random=True)
    regr.fit(train[train.columns[:-1]], train[train.columns[-1:]])
    coefficient = regr.coef_
    # print('Coefficients: \n', regr.coef_)
    mean_squared = np.mean((regr.predict(train[train.columns[:-1]]) - train[train.columns[-1:]]) ** 2)
    # print("Mean squared error: %.2f" % np.mean((regr.predict(train[train.columns[:-1]]) - train[train.columns[-1:]]) ** 2))
    score = regr.score(test[test.columns[:-1]], test[test.columns[-1:]])
    # print('R^2: %.2f' % regr.score(test[test.columns[:-1]], test[test.columns[-1:]]))
    predict = regr.predict(test[test.columns[:-1]])
    data = {'coefficient' : coefficient, 'mean_squared' : mean_squared, 'score' : score, 'predict' : [predict] }
    return data

VALID_FUNCTION_CALLS = ['test_stationarity',
                        'decompose_series',
                        'linear_regression_viz',
                        'linear_regression_raw']

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

