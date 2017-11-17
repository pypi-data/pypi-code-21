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
import io
import json
import numpy as np
import pandas as pd
import quandl
import requests
import re
import inspect

# from fiteanalytics.finx.admin.config import Config
import fiteanalytics.finx.utilities as utilities
FORMAT = '%Y-%m-%d %H:%M:%S'


# Functions below are originally from package fite.py
def stock(finx_key, ticker=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print (kwargs, ' does not match any known arguments and will be ignored')
    if not isinstance(ticker, str):
        return 'invalid ticker: [' + str(ticker) + '] is not a valid ticker'
    # config = Config()
    url = 'http://finx.io/rest/stock/'
    # deprecated
    # url += 'stock/' + ticker
    # if config.settings['identity']['finx_key'] == 'Not Authorized':
    #     return 'finx has not been installed yet for help installing refer to http://finx.io/finx/documentation'
    payload = dict(finx_key=finx_key, ticker=ticker)
    response = requests.get(url, params=payload)
    json_response = json.loads(response.text)
    try:
        df = pd.DataFrame(json_response)
    except:
        return 'invalid ticker: [' + str(ticker) + '] is not a valid ticker'
    return df

def stock_quote(finx_key, ticker=None, as_of_date=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print (kwargs, ' does not match any known arguments and will be ignored')
    if not isinstance(ticker, str):
        return 'invalid ticker: [' + str(ticker) + '] is not a valid ticker'
    url = 'http://finx.io/rest/stock/quote/'
    payload = dict(finx_key=finx_key, ticker=ticker, as_of_date=as_of_date)
    response = requests.get(url, params=payload)
    json_response = json.loads(response.text)
    try:
        df = pd.DataFrame(json_response)
    except:
        return 'invalid ticker: [' + str(ticker) + '] is not a valid ticker'
    return df

# Deprecated
# def stock_summary(finx_key, ticker=None, as_of_date=None, *args, **kwargs):
#     if args:
#         print(args, ' does not match any known arguments and will be ignored')
#     if kwargs:
#         print (kwargs, ' does not match any known arguments and will be ignored')
#     if not isinstance(ticker, str):
#         return 'invalid ticker: [' + str(ticker) + '] is not a valid ticker'
#     # config = Config()
#     url = 'http://finx.io/rest/stock/summary/'
#     payload = dict(ticker=ticker,
#                    as_of_date=as_of_date,
#                    finx_key=finx_key)
#     response = requests.get(url, params=payload)
#     if not response.ok:
#         return response.text
#     json_response = json.loads(response.text)
#     df = pd.DataFrame(json_response, index=[stocksnap['snapdate'] for stocksnap in json_response])
#     if df.empty:
#         return 'no data: ticker is valid, however, there is no data currently available'
#     return list(df.columns)

# def stock_features(ticker=None,as_of_date=None, *args, **kwargs):
#     if args:
#         print(args, ' does not match any known arguments and will be ignored')
#     if kwargs:
#         print (kwargs, ' does not match any known arguments and will be ignored')
#     if not isinstance(ticker, str):
#         return 'invalid ticker: [' + str(ticker) + '] is not a valid ticker'
#     config = Config()
#     equity_data_uri = config.settings['endpoints']['content']['fite']
#     equity_data_uri += 'equity/reference/'
#     payload = dict(ticker=ticker,
#                    as_of_date=as_of_date,
#                    finx_key=config.settings['identity']['finx_key'])
#     response = requests.get(equity_data_uri, params=payload)
#     if not response.ok:
#         return response.text
#     json_response = json.loads(response.text)
#     df = pd.DataFrame(json_response, index=[stocksnap['snapdate'] for stocksnap in json_response])
#     if df.empty:
#         return 'no data: ticker is valid, however, there is no data currently available'
#     return list(df.columns)


def stock_live(finx_key, ticker=None, *args, **kwargs):
    try:
        if args:
            print(args, ' does not match any known arguments and will be ignored')
        if kwargs:
            print (kwargs, ' does not match any known arguments and will be ignored')
        if ticker is None :
            return 'bad ticker: ticker [' +str(ticker)+'] not found'
        # config = Config()
        # if config.settings['endpoints']['content']['fite'] == 'Not Authorized':
        #     return 'endpoint inaccessible: finx_api key has not been authorized yet. Installation tutorial can be found here http://finx.io/finx/documentation '
        url = 'http://finx.io/rest/stock/live/'
        # url += 'stock/live/'
        payload = dict(ticker=ticker,
                       finx_key=finx_key)
        response = requests.get(url, params=payload)
        if response.status_code == 400:
            return response.text
        elif response.status_code == 401:
            return response.text
        json_response = json.loads(response.text)
        try:
            df = pd.DataFrame(json_response, index=[str(json_response['snapdate']).split('T')[0]])
        except:
            return 'no data, but ticker and item are valid: data not available'
        df = df.sort_index()
        return df
    except:
        return 'endpoint inaccessible: stock observation service is currently unavailable'


def stock_observations(finx_key, feature='ALL', ticker=None, start_date=None, end_date=None, *args, **kwargs):
    try:
        if args:
            print(args, ' does not match any known arguments and will be ignored')
        if kwargs:
            print (kwargs, ' does not match any known arguments and will be ignored')
        if ticker is None :
            return 'bad ticker: ticker [' +str(ticker)+'] not found'
        # if not isinstance(start_date, str):
        #     return 'start_date must not be in string format, [' + str(start_date) + '] is not a correct string input'
        # if not isinstance(end_date,str):
        #     return 'end_date must not be in string format, [' + str(end_date) + '] is not a correct string input'
        # config = Config()
        # if config.settings['endpoints']['content']['fite'] == 'Not Authorized':
        #     return 'endpoint inaccessible: finx_api key has not been authorized yet. Installation tutorial can be found here http://finx.io/finx/documentation '
        url = 'http://finx.io/rest/stock/observations/'
        # url += 'stock/observations/'
        payload = dict(
            feature=feature,
           ticker=ticker,
           start_date=start_date,
           end_date=end_date,
           finx_key=finx_key)
        response = requests.get(url, params=payload)
        if response.status_code == 400:
            return response.text
        elif response.status_code == 401:
            return response.text
        json_response = json.loads(response.text)
        try:
            if feature not in ['ALL','volume','open_price','close_price','high_price','low_price']:
                return 'bad feature: feature ['+feature+'] not valid'
            df = pd.DataFrame(json_response,index=[stock_snap['snapdate'].split('T')[0] for stock_snap in json_response])[['volume','open_price','close_price','high_price','low_price']]
            if feature != 'ALL':
                df = df[[feature]]
        except:
            return 'no data, but ticker and feature are valid: data not available'
        df = df.sort_index()
        return df
    except:
        return 'endpoint inaccessible: stock observation service is currently unavailable'

# Deprecated Until Further Notice
# def stock_risk_measures(finx_key, ticker=None, start_date=None, end_date=None, *args, **kwargs):
#     if args:
#         print(args, ' does not match any known arguments and will be ignored')
#     if kwargs:
#         print(kwargs, ' does not match any known arguments and will be ignored')
#     if not isinstance(ticker, str):
#         return 'ticker must be a string, ' + str(ticker) + ' is not the correct format'
#     if not isinstance(start_date, str):
#         return 'start_date must be a string in "YYYY-MM-DD" format, ' + str(start_date) + ' is not the correct format'
#     # config = Config()
#     url = 'http://finx.io/rest/equity/risk/'
#     # url += 'equity/risk/'
#     payload = dict(ticker=ticker,
#                    start_date=start_date,
#                    end_date=end_date,
#                    finx_key=finx_key)
#     response = requests.get(url, params=payload)
#     if not response.ok:
#         return response.text
#     try:
#         json_response = json.loads(response.text)
#         df = pd.DataFrame(json_response).set_index('snap_uuid')
#         df.__delitem__('archive')
#         df.__delitem__('datestamp')
#         df.__delitem__('recorder_uuid')
#     except:
#         return 'no data: ticker is valid, however, there is currently no data for the requested parameters'
#     return df


def stock_max_pain_observations(finx_key, ticker=None, expiry_date=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print (kwargs, ' does not match any known arguments and will be ignored')
    # if expiry_date is None:
    #     return 'expiry_Date ['+str(expiry_date)+'] is not in the correct format YYYY-MM-DD'
    # config = Config()
    url = 'http://finx.io/rest/stock/observations/maxpain/'
    # url += 'equity/maxpain/'
    payload = dict(ticker=str(ticker),
                   expiry_date=str(expiry_date),
                   finx_key=finx_key)
    response = requests.get(url, params=payload)
    if not response.ok:
        return response.text
    json_response = json.loads(response.text)
    df = pd.DataFrame(json_response, index=[str(max_pain['calc_date']).split('T')[0] for max_pain in json_response])
    if df.empty:
        return 'no data: ticker is valid, however, there is currently no data matching the ticker'
    df = df.sort_index()
    return df

def stock_option_summary(finx_key, ticker=None, as_of_date=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print(kwargs, ' does not match any known arguments and will be ignored')
    # config = Config()
    url = 'http://finx.io/rest/stock_option/summary'
    # url += 'stockoption/summary/'
    payload = dict(ticker=str(ticker),
                   as_of_date=as_of_date,
                   finx_key=finx_key)
    response = requests.get(url, params=payload)
    if not response.ok:
        return response.text
    json_response = json.loads(response.text)
    df = pd.DataFrame(json_response, index=[0])
    cols = ['ticker',
            'as_of_date',
            'count_options',
            'count_calls',
            'count_puts',
            'count_itm_calls',
            'count_otm_calls',
            'count_itm_puts',
            'count_otm_puts',
            'count_option_securities_with_open_interest',
            'sum_open_interest',
            'sum_open_interest_calls',
            'sum_open_interest_puts',
            'sum_open_interest_itm_calls',
            'sum_open_interest_itm_puts',
            'sum_open_interest_otm_calls',
            'sum_open_interest_otm_puts',
            'option_with_highest_implied_volatility',
            'option_with_most_open_interest']
    df = df[cols]
    cols_to_make_numeric = ['count_options',
                            'count_calls',
                            'count_puts',
                            'count_itm_calls',
                            'count_otm_calls',
                            'count_itm_puts',
                            'count_otm_puts',
                            'count_option_securities_with_open_interest',
                            'sum_open_interest',
                            'sum_open_interest_calls',
                            'sum_open_interest_puts',
                            'sum_open_interest_itm_calls',
                            'sum_open_interest_itm_puts',
                            'sum_open_interest_otm_calls',
                            'sum_open_interest_otm_puts']
    for col in cols_to_make_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    if df.empty:
        return 'no data: ticker is valid, however, there is currently no data matching the request'
    return df

def stock_option(finx_key, ticker=None, expiry_date=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print(kwargs, ' does not match any known arguments and will be ignored')
    # config = Config()
    url = 'http://finx.io/rest/stock_options/'
    payload = dict(
        ticker=ticker,
        expiry_date=expiry_date,
        finx_key=finx_key)
    response = requests.get(url, params=payload)
    if not response.ok:
        return response.text
    try:
        json_response = json.loads(response.text)
        df = pd.DataFrame(json_response).set_index('stock_option_security_uuid')
    except:
        return 'no data: ticker is valid, however, there is currently no data matching the request'
    return df

def stock_option_quote(finx_key, ticker=None, expiry_date=None, option_side=None, strike_price=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print(kwargs, ' does not match any known arguments and will be ignored')
    url = 'http://finx.io/rest/stock_option/quote/'
    payload = dict(ticker=ticker,
                   expiry_date=expiry_date,
                   option_side=option_side,
                   strike_price=strike_price,
                   finx_key=finx_key)
    response = requests.get(url, params=payload)
    if not response.ok:
        return response.text
    try:
        json_response = json.loads(response.text)
        df = pd.DataFrame(json_response, index=[json_response['expiry_date']])
    except:
        return 'no data: ticker is valid, however, there is currently no data matching the request'
    return df

def stock_option_observations(finx_key, feature='ALL',ticker=None, strike_price = None, expiry_date=None, option_side=None, *args, **kwargs):
    # config = Config()
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print (kwargs, ' does not match any known arguments and will be ignored')
    # if not isinstance(ticker, str):
    #     return 'ticker must be a string ' + str(ticker) + ' is not a correct string input'
    if not isinstance(feature, str):
        return 'feature must be a string ' + str(feature) + ' is not a correct string/list input'
    # if not isinstance(expiry_date_start, str):
    #     return 'expiry_date_start must not be in string format, ' + str(expiry_date_start) + ' is not a correct string input'
    # if not isinstance(expiry_date_end,str):
    #     return 'expiry_date_end must not be in string format, ' + str(expiry_date_end) + ' is not a correct string input'
    url = 'http://finx.io/rest/stock_option/observations'
    payload = dict(feature=feature,
                   ticker=str(ticker),
                   strike_price=strike_price,
                   expiry_date=str(expiry_date),
                   option_side=option_side,
                   finx_key=finx_key)
    response = requests.get(url, params=payload)
    if not response.ok:
        return response.text
    json_response = json.loads(response.text)
    df = pd.DataFrame(json_response, index=[option['snapdate'] for option in json_response])
    if feature != 'ALL':
        try:
            df = df[[feature]]
        except:
            return 'feature ' +feature+ ' is not a valid feature'
    if df.empty:
        return 'ticker and feature are valid, however, there is no data available for this set of parameters'
    return df.sort_index()

# Deprecated Until Further Notice
# def stock_option_risk_measures(ticker, strike_price=None, option_side=None, expiry_date_start=None, expiry_date_end=None, *args, **kwargs):
#     config = Config()
#     if args:
#         print(args, ' does not match any known arguments and will be ignored')
#     if kwargs:
#         print (kwargs, ' does not match any known arguments and will be ignored')
#     if not isinstance(ticker, str):
#         return 'ticker must be a string ' + str(ticker) + ' is not a correct string input'
#     if strike_price is not None and not isinstance(strike_price, float) and not isinstance(strike_price, int):
#         return 'strike_price must be a decimal ' + str(strike_price) + ' is not a correct decimal input'
#     valid_option_sides = ['call','put']
#     if option_side is not None and option_side not in valid_option_sides:
#         return 'option_side ' + option_side + ' is not a valid option side, please choose from: ' + str(valid_option_sides)
#     url = 'http://finx.io/rest/'
#     url += 'option/risk/'
#     payload = dict(ticker=str(ticker),
#                    strike_price=strike_price,
#                    option_side=option_side,
#                    expiry_date_start=expiry_date_start,
#                    expiry_date_end=expiry_date_end,
#                    finx_key=config.settings['identity']['finx_key'])
#     response = requests.get(url, params=payload)
#     if not response.ok:
#         return response.text
#     json_response = json.loads(response.text)
#     try:
#         df = pd.DataFrame(json_response, index=[option['snapdate'] for option in json_response])[['theta','delta','vega','rho']]
#     except:
#         return 'no data: ticker ['+ ticker + '], option_side ['+str(option_side)+'] does not have any data points for strike price [' + str(strike_price)+'] between the dates ' + str(expiry_date_start)+ ', and '+str(expiry_date_end)
#     df = df.sort_index()
#     return df

def financials_features(finx_key, ticker=None, cadence=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print (kwargs, ' does not match any known arguments and will not be ignored')
    # c = Config()
    url_financials = 'http://finx.io/rest/financial/features/'
    payload = dict(finx_key=finx_key,ticker=str(ticker), cadence=cadence)
    response_financials = requests.get(url_financials, params=payload)
    if not response_financials.ok:
        return response_financials.text
    json_dict = json.loads(response_financials.text)
    df = pd.DataFrame(json_dict, index=[0])
    return df

def financials_observations(finx_key, ticker=None, features=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print(kwargs, ' does not match any known arguments and will be ignored')
    if not isinstance(ticker, str):
        return 'invalid ticker: [' + str(ticker) + '] is not a valid ticker'
    if not isinstance(features,list):
        return 'invalid feature, ' + str(features) + ' is not a valid feature'
    url = 'https://finx.io/rest/endpoint/q/?finx_key=' + finx_key
    finx_validation_response = requests.get(url).json()
    # if not utilities.check_ticker(ticker):
    #     return ticker + ' is not a valid ticker'
    joined_df = pd.DataFrame()
    for feature in features:
        quandl_code = 'SF1/' + ticker + '_' + feature
        try:
            if joined_df.empty:
                joined_df = quandl.get(quandl_code, **finx_validation_response)
                joined_df = joined_df.rename(columns={'Value': ticker + '_' + feature})
            else:
                df = quandl.get(quandl_code, **finx_validation_response)
                df = df.rename(columns={'Value': ticker + '_' + feature})
                joined_df = joined_df.join(df, how='left')
        except quandl.errors.quandl_error.NotFoundError:
            if feature is not None:
                print('\n' + feature + ' is not a valid feature in ticker '+ticker+'.\nOmitting invalid feature.\n')
    if joined_df.empty:
        print('Data Frame is empty, the ticker must not have been a valid ticker or\nthe feature list must not have had any valid features. Double check for typos')
    return joined_df

# Below are all the functions originally in fred.py

def fred_features():
    return "Find a series id on Fred's website: https://research.stlouisfed.org/"

def fred_observations(finx_key, series_id=None, start_date=None, end_date=None, *args, **kwargs):
    if args:
        print(args, ' does not match any known arguments and will be ignored')
    if kwargs:
        print(kwargs, ' does not match any known arguments and will be ignored')
    if series_id is None:
        return 'series_id must be a string not None'
    # config = Config()
    url='https://finx.io/rest/endpoint/f/?finx_key=' + finx_key
    finx_validation_response = requests.get(url).json()
    offset = 0
    request_uri = "https://api.stlouisfed.org/fred/series/observations"
    pattern = re.compile(r'[0-9]{4}\-[0-9]{2}\-[0-9]{2}')
    if (start_date is not None) and (not re.match(pattern,str(start_date))):
        return 'start_date ['+str(start_date)+'] must be a string in YYYY-MM-DD format'
    if (end_date is not None) and (not re.match(pattern,str(end_date))):
        return 'end_date ['+str(end_date)+'] must be a string in YYY-MM-DD format'
    payload = dict(series_id=series_id,
                   observations_start=start_date,
                   observations_end=end_date,
                   **finx_validation_response,
                   file_type='json')
    try:
        raw_response = requests.get(request_uri,params=payload)
        json_response = json.loads(raw_response.text)
        count = json_response['count']
        limit = json_response['limit']
    except:
        return 'series_id [' +str(series_id)+ '] is not a valid series id'
    observations = []
    while offset < count:
        payload = dict(series_id= series_id,
                       observations_start= start_date,
                       observations_end=end_date,
                       offset=str(offset),
                       **finx_validation_response,
                       file_type='json')
        raw_response = requests.get(request_uri,params=payload)
        json_response = json.loads(raw_response.text)
        observations += list(json_response['observations'])
        offset += limit
    return fred_observation_dataframe(observations, series_id)

def fred_observation_dataframe(observations, series_id):
    df = pd.DataFrame(observations, index=[x['date'] for x in observations])[['value']]
    df['value'] = list(map(float, list(df.replace('.', '0')['value'])))
    df = df.set_index(pd.to_datetime(df.index, format=FORMAT)).replace(0.0, np.nan).dropna()
    df.columns = [series_id]
    return df

VALID_FUNCTION_CALLS = ['stock_summary',
                        'stock_features',
                        'stock_observations',
                        'stock_risk_measures',
                        'stock_max_pain_observations',
                        'stock_option_summary',
                        'stock_option_list',
                        'stock_option_observations',
                        'stock_option_risk_measures',
                        'financials_features',
                        'financials_observations',
                        'fred_observations']

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
