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
from datetime import timedelta
import pandas as pd
import numpy as np
import re
import inspect
from datetime import timedelta, datetime
from sklearn.preprocessing import Imputer, normalize
import fiteanalytics.finx.utilities as utilities

#From Data in Demo
def filter(df, columns='ALL', filter_criterion=None, threshold=0):
    threshold_valid_options_pattern = re.compile(r'[0-9]+')
    matched_threshold = re.match(threshold_valid_options_pattern, str(threshold))
    if not matched_threshold:
        return 'threshold input invalid syntax, please retry using an integer ( filter(dataframe, columns, filter_criterion, threshold) )'
    criterion_pattern = re.compile('(df)([\<\>]{1}|[\<\>]{1}[\=]{1}|[\=]{2})[\-]{0,1}[0-9]+')
    matched_criterion = re.match(criterion_pattern, filter_criterion)
    if not matched_criterion:
        return 'invalid criterion, retry with the correct format (example: "df>2000")'
    try:
        if columns != 'ALL':
            try:
                df = df[columns]
            except:
                return 'invalid columns: ' + str(columns) + ' please choose from: ' + str(df.columns.values)
        return df[eval(filter_criterion)].dropna(thresh=threshold)
    except:
        return 'missing dataframe or dataframe not in correct format'

def reorder(df, columns, ascending):
    try:
        return df.sort_values(by=columns, ascending=ascending)
    except:
        return "invalid parameter, check parameters and retry"

def select(df, columns):
    try:
        return df[columns]
    except:
        return 'list of columns not valid: ' + str(columns) + ' valid columns: ' + str(df.columns.values)

def rename(df, list_old_names, list_new_names):
    return df.rename(columns=dict(zip(list_old_names, list_new_names)))

def add_column(df, series_df):
    try:
        return pd.concat([df, series_df], axis=1)
    except:
        return 'one or both of the input dataframes are not valid'

def describe(df):
    return df.describe()

# Below is from dataframe_utils.py
def merge_dataframes_on_date_axis(list_of_dataframes):
    dataframe = pd.concat(list_of_dataframes,axis=1)
    return dataframe

def drop_values(df):
    return df.dropna()

def split(df, train_fraction, random=False):
    if random is True:
        df = df.sample(frac=1)
    split_index = int(train_fraction*len(df.index))
    train = df[:split_index]
    test = df[split_index:]
    return train, test

def scale_values(df, min_val=-1, max_val=1):
    for column in df.columns:
        col_max = df[column].max()
        col_min = df[column].min()
        df[column] = ((max_val-min_val)*(df[column]-col_min)/(col_max-col_min)) + min_val
    return df

def log_series(series):
    return np.log(series)

def moving_average(series, delta=2):
    return series.rolling(delta).mean()

def exponential_moving_average(series, halflife=1, min_periods=0, adjust=True, ignore_na=True):
    return series.ewm(halflife=halflife,min_periods=min_periods,adjust=adjust,ignore_na=ignore_na).mean()

def log_difference(series, offset=1):
    return np.log(series).shift(offset) - np.log(series)

def normalize_values(df, columns):
    try:
        for column in columns:
            df[column] = (df[column] - df[column].mean())/df[column].std()
        return df
    except:
        return "dataframe or column input incorrect, double check that you typed everything correctly"

def interpolate_values(df, columns, method='linear'):
    try:
        for column in columns:
            df[column] = df[column].interpolate(method=method)
        return df
    except:
        return "incorrect input, follow the format interpolate_values(dataframe, column_list, method)"

def impute_values(df, columns, method='mean'):
    try:
        imp = Imputer(missing_values=np.nan, strategy=method)
        for column in columns:
            df[column] = imp.fit_transform(df[column].values.reshape(-1,1))
        return df
    except:
        return "incorrect input, follow the format impute_values(dataframe, column_list, method)"

def fit_values(df, columns, polynomial=1):
    try:
        try:
            df_original = df
            df = df.dropna()
        except:
            return 'Missing Dataframe input, make sure the format is correct ( fit_values(dataframe, columns, polynomial) )'
        difference = len(df_original.index) - len(df.index)
        try:
            for column in columns:
                params = np.polyfit(np.arange(len(df[column].index)), df[column], polynomial)
                for i in range(difference - 1, -1, -1):
                    if np.isnan(df_original[column][i]):
                        value = params[polynomial]
                        for j in range(polynomial):
                            value -= params[j] * (difference - i)
                        df_original[column][i] = value
            return df_original
        except:
            return 'invalid columns input'
    except:
        return 'values in dataframe are not fit-able'

def align_index_on_base(df, base_series=-1):
    try:
        df = df.loc[df[base_series].dropna().index]
    except:
        df = df.loc[df[df.columns[-1]].dropna().index]
    return df

# def magic_wrangler(list_of_dataframes):
#     try:
#         try:
#             df = merge_dataframes_on_date_axis(list_of_dataframes)
#         except:
#             return 'invalid list_of_dataframes'
#         latest_date = utilities.make_utc_from_string('0001-01-01 00:00:00')
#         latest_column = None
#         for column in df.columns:
#             first_index = utilities.make_utc_from_string(str(df[column].dropna().index[0]))
#             if first_index > latest_date:
#                 latest_date = first_index
#                 latest_column = column
#         temp_df = df[[latest_column]]
#         df = df.drop(latest_column, axis=1)
#         return align_index_on_base(pd.concat([df, temp_df], axis=1))
#     except:
#         return 'dataframes have values other than: index = string(in datetime format), and column = float make sure your dataframe is set up correctly in a time series format'

def magic_wrangler(list_of_dataframes):
    try:
        result = None
        for df in list_of_dataframes:
            if result is None:
                result = df.index
            else:
                result.append(df.index)
        index = result[~result.duplicated()]
        dataframe = pd.DataFrame(None,index=index)
        for df in list_of_dataframes:
            dataframe = dataframe.merge(df,how='outer',left_index=True, right_index=True, )
        return dataframe
    except:
        return 'dataframes have values other than: index = string(in datetime format), and column = float make sure your dataframe is set up correctly in a time series format'

def scale_cadence(df, cadence, start_date, end_date):
    if re.search('d',cadence,re.I):
        scaled_df = pd.DataFrame(df,index=pd.DatetimeIndex(freq='D',start=start_date,end=end_date))
    elif re.search('m',cadence,re.I):
        scaled_df = pd.DataFrame(df,index=pd.DatetimeIndex(freq='MS',start=start_date,end=end_date))
    elif re.search('y',cadence,re.I) or re.search('annual',cadence,re.I):
        scaled_df = pd.DataFrame(df,index=pd.DatetimeIndex(freq='A',start=start_date,end=end_date))
    else:
        scaled_df = 'Not a valid cadence, try daily, monthly, or annually'
    return scaled_df

# Into dataframe construction
def shift_time(single_feature_timeseries, new_feature_name, shift_factor):
    if not re.match(r'[\-\+]{1}[0-9]+',shift_factor):
        return dict(shift_factor_invalid='shift factor must be in the format +<integer_value> or -<integer_value>')
    if re.search(r'\+',shift_factor):
        shift_factor = shift_factor[1:]
        shift_factor_value = int(shift_factor)
        single_feature_timeseries = scale_cadence(single_feature_timeseries,
                                                          'Day',
                                                          single_feature_timeseries.index[0],
                                                          single_feature_timeseries.index[(len(single_feature_timeseries)-1)] + timedelta(days=1))
        rescaled_ts = single_feature_timeseries.shift(-shift_factor_value, 'D')
        rescaled_ts = rescaled_ts[shift_factor_value:]
        rescaled_ts = rescaled_ts.rename(columns={rescaled_ts.columns.values[0]: new_feature_name})
        return rescaled_ts
    else:
        shift_factor = shift_factor[1:]
        shift_factor_value = int(shift_factor)
        single_feature_timeseries = scale_cadence(single_feature_timeseries,
                                                          'Day',
                                                          single_feature_timeseries.index[0],
                                                          single_feature_timeseries.index[(len(single_feature_timeseries)-1)])
        rescaled_ts = single_feature_timeseries.set_index(single_feature_timeseries.index.shift(shift_factor_value,'D'))
        rescaled_ts = rescaled_ts.rename(columns={rescaled_ts.columns.values[0]: new_feature_name})
        return rescaled_ts

#TODO:help functions
VALID_FUNCTION_CALLS = ['filter',
                        'reorder',
                        'select',
                        'rename',
                        'add_column',
                        'describe',
                        'merge_dataframes_on_date_axis',
                        'drop_values',
                        'split',
                        'scale_values',
                        'log_series',
                        'moving_average',
                        'exponential_moving_average',
                        'log_difference',
                        'normalize_values',
                        'interpolate_values',
                        'impute_values',
                        'fit_values',
                        'align_index_on_base',
                        'magic_wrangler',
                        'scale_cadence']

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


