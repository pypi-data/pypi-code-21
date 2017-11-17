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
import datetime as dt
import pytz
import inspect
import re
import requests
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup

from fiteanalytics.finx.admin.config import Config

# def register_key(finx_key):
#     config = Config()
#     config.save_identity(finx_key)
#     return None

def install_finx(finx_key, test=False):
    config = Config()
    config.install_finx(finx_key, test)
    return None

def now():
    return dt.datetime.now(pytz.UTC)

def make_eod_today():
    return make_eod_utc_from_string(str(now()).split(' ')[0])

def make_utc_from_naive(naive_date):
    return pytz.utc.localize(naive_date)

def make_naive_from_utc(aware_date):
    return aware_date.replace(tzinfo=None)

def make_utc_from_string(string_date):
    string_date = string_date.split(' ')
    date_fields = list(map(int, string_date[0].split('-')))
    time_fields = list(map(int, string_date[1].split(':')))
    return dt.datetime(date_fields[0],date_fields[1],date_fields[2],time_fields[0],time_fields[1],time_fields[2], tzinfo=pytz.UTC)

def make_utc_from_YYYYMMDDhhmmss(string_pattern):
    naive_date = dt.datetime.strptime(string_pattern, '%Y%m%d%H%M%S')
    utc_date = make_utc_from_naive(naive_date)
    return utc_date

def make_utc_from_YYYY_dash_MM_dash_DD(string_date):
    naive_date = dt.datetime.strptime(string_date, '%Y-%m-%d')
    utc_date = make_utc_from_naive(naive_date)
    return utc_date

def make_YYYYMMDDhhmmss_from_dateutils_now():
    date_part, time_part = str(now())[:19].split(' ')
    date_part = ''.join(date_part.split('-'))
    time_part = ''.join(time_part.split(':'))
    formatted_string = date_part+time_part
    return formatted_string

def make_YYYYdashMMdashDD_from_dateutils_now():
    date_part, time_part = str(now())[:19].split(' ')
    date_part = date_part.split('-')
    formatted_string = date_part[0] + '-' + date_part[1] + '-' + date_part[2]
    return formatted_string

def make_naive_string_from_utc_string(string_date):
    string_date = string_date.split('T')
    date_part = string_date[0]
    time_part = string_date[1].split('+')[0]
    naive_string = date_part+' '+time_part
    return naive_string

def make_bod_utc_from_string(string_date):
    date_fields = list(map(int, string_date.split('-')))
    return dt.datetime(date_fields[0],date_fields[1],date_fields[2],0,0,0,tzinfo=pytz.UTC)

def make_eod_utc_from_string(string_date):
    date_fields = list(map(int, string_date.split('-')))
    return dt.datetime(date_fields[0],date_fields[1],date_fields[2],23,59,59,tzinfo=pytz.UTC)

#made special case for Fred Util
def make_utc_fred_last_updated(string_date):
    clean_string = string_date[:-3]
    utc_date = make_utc_from_string(clean_string)
    return utc_date

# if string_date_1 > string_date_2 then returns True
def compare_dates(string_date_1=None, string_date_2=None):
    result = False
    if string_date_1 is None:
        return result
    if string_date_2 is None:
        string_date_2 = make_YYYYdashMMdashDD_from_dateutils_now()
    if dt.datetime.strptime(string_date_1, '%Y-%m-%d') > dt.datetime.strptime(string_date_2, '%Y-%m-%d'):
        result = True
    return result

#Change the format of a datetime-string (defaults set to YYYYMMDD in and None out)
def magic_date_converter(date_string, date_format_in='%Y%m%d', date_format_out=None):
    try:
        date_format_in = re.sub(r'YYYY', '%Y', date_format_in)
        date_format_in = re.sub(r'YY', '%y', date_format_in)
        date_format_in = re.sub(r'MM', '%m', date_format_in)
        date_format_in = re.sub(r'DD', '%d', date_format_in)
        date_format_in = re.sub(r'WEEKDAY', '%A', date_format_in)
        date_format_in = re.sub(r'weekday', '%a', date_format_in)
        date_format_in = re.sub(r'MONTH', '%B', date_format_in)
        date_format_in = re.sub(r'month', '%b', date_format_in)
        date_format_in = re.sub(r'Hour', '%H', date_format_in)
        date_format_in = re.sub(r'Min', '%M', date_format_in)
        date_format_in = re.sub(r'Sec', '%S', date_format_in)
        # after the date_format_in is completely changed to a datetime readable expression, transform the date_string to datetime object
        date_string = re.sub(r'st|nd|rd|th', '', date_string)
        base_data = dt.datetime.strptime(date_string, date_format_in)
        if date_format_out is not None:
            date_format_out = re.sub(r'YYYY', '%Y', date_format_out)
            date_format_out = re.sub(r'YY', '%y', date_format_out)
            date_format_out = re.sub(r'MM', '%m', date_format_out)
            date_format_out = re.sub(r'DD', '%d', date_format_out)
            date_format_out = re.sub(r'MONTH', '%B', date_format_out)
            date_format_out = re.sub(r'month', '%b', date_format_out)
            date_format_out = re.sub(r'Hour', '%H', date_format_out)
            date_format_out = re.sub(r'Min', '%M', date_format_out)
            date_format_out = re.sub(r'Sec', '%S', date_format_out)
            date_format_out = re.sub(r'WEEKDAY', '%A', date_format_out)
            date_format_out = re.sub(r'weekday', '%a', date_format_out)
            # after the date_format_out is completely changed to a datetime readable expression, transform the datetime object to a formatted string
            if re.search(r'%b|%B', date_format_out):
                if re.search(r'%d',date_format_out):
                    day = dt.datetime.strftime(base_data, '%d')
                    if (int(day) % 10) < 4 and (int(day) < 10 or int(day) > 20):
                        if int(day)%2 == 0:
                            suffix = 'nd'
                        elif int(day)%3 == 0:
                            suffix = 'rd'
                        else:
                            suffix = 'st'
                    else:
                        suffix = 'th'
                    date_format_out = re.sub(r'\%d', '%d'+suffix, date_format_out)
            formatted_data = dt.datetime.strftime(base_data, date_format_out)
        else:
            formatted_data = base_data
        return formatted_data
    except:
        return "Date Converter couldnt understand your command. Double check the input, the reader is case sensitive"

# Deprecated since I made the csv in s3 bucket
# def get_hollidays_list(market):
#     url = 'http://markets.on.nytimes.com/research/markets/holidays/holidays.asp'
#     holidays = list()
#     for i in range(-1, 10):
#         timeOffset = i
#         payload = dict(exchange=market,
#                        timeOFFset=timeOffset,
#                        display='market')
#         response_LSE = requests.get(url, params=payload)
#         soup = BeautifulSoup(response_LSE.text, 'html.parser')
#         for tr in soup.find_all('tr'):
#             td = tr.find('td')
#             if td is not None:
#                 holidays.append(magic_date_converter(td.text, 'MM/DD/YYYY', None))
#     return holidays

# def NYSE_trading_days():
#     holiday = get_hollidays_list('NYQ')
#     result = list()
#     dt = pd.DatetimeIndex(freq='B',start='2016-01-01',end='2027-12-31')
#     for item in dt:
#         if item not in holiday:
#             result.append(item)
#     return result
#
# def LSE_trading_days():
#     holiday = get_hollidays_list('LSE')
#     result = list()
#     dt = pd.DatetimeIndex(freq='B', start='2016-01-01', end='2027-12-31')
#     for item in dt:
#         if item not in holiday:
#             result.append(item)
#     return result
#
# def NASDAQ_trading_days():
#     holiday = get_hollidays_list('NSQ')
#     result = list()
#     dt = pd.DatetimeIndex(freq='B', start='2016-01-01', end='2027-12-31')
#     for item in dt:
#         if item not in holiday:
#             result.append(item)
#     return result

def trading_days(market):
    if re.search(r'NYSE',market,re.I):
        market = 'nyse'
    elif re.search(r'LSE',market,re.I):
        market = 'lse'
    elif re.search(r'NASDAQ',market,re.I):
        market = 'nasdaq'
    url = 'https://s3-us-west-1.amazonaws.com/fiteanalytics/' + market + '_holidays.csv'
    try:
        response = requests.get(url)
    except:
        return 'market invalid or spelled incorrectly'
    years = ['2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027']
    df = pd.read_csv(StringIO(response.text), index_col=0, parse_dates=years)
    result = list()
    dt = pd.DatetimeIndex(freq='B', start='2016-01-01', end='2027-12-31')
    holiday_list = list()
    for col in df:
        for row in df[col]:
            holiday_list.append(row)
    for item in dt:
        if item not in holiday_list:
            result.append(item)
    return result

VALID_FUNCTION_CALLS = ['install_finx',
                        'now',
                        'make_eod_today',
                        'make_utc_from_naive',
                        'make_naive_from_utc',
                        'make_utc_from_string',
                        'make_utc_from_YYYYMMDDhhmmss',
                        'make_utc_from_YYYY_dash_MM_dash_DD',
                        'make_YYYYMMDDhhmmss_from_dateutils_now',
                        'make_YYYYdashMMdashDD_from_dateutils_now',
                        'make_naive_string_from_utc_string',
                        'make_bod_utc_from_string',
                        'make_eod_utc_from_string',
                        'make_utc_fred_last_updated',
                        'compare_dates',
                        'magic_date_converter',
                        'trading_days']

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
