# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius                                                                     #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program provides currency and other utilities.                          #
#                                                                              #
# copyright (C) 2017 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

from __future__ import division
import ast
import datetime
import functools
import io
import json
import os
import pprint
import requests
import time
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

import currency_converter
import dataset
import datavision
import matplotlib.pyplot as plt
import numpy
import pandas as pd
import pyprel
import shijian

name    = "denarius"
version = "2017-11-29T1856Z"

def prices_Bitcoin_Ethereum(
    convert_to_floats = True
    ):

    prices = {}

    prices["BTC_EUR"] = requests.get("https://www.bitstamp.net/api/v2/ticker/btceur").json()
    prices["BTC_USD"] = requests.get("https://www.bitstamp.net/api/v2/ticker/btcusd").json()
    prices["ETH_EUR"] = requests.get("https://www.bitstamp.net/api/v2/ticker/etheur").json()
    prices["ETH_USD"] = requests.get("https://www.bitstamp.net/api/v2/ticker/ethusd").json()
    prices["ETH_BTC"] = requests.get("https://www.bitstamp.net/api/v2/ticker/ethbtc").json()

    if convert_to_floats:

        for pair in prices:
            for price in prices[pair]:
                prices[pair][price] = float(prices[pair][price])

    return prices

def last_prices_Bitcoin_Ethereum():

    prices = prices_Bitcoin_Ethereum()

    text =\
"""
BTC_EUR: {BTC_EUR_last}
BTC_USD: {BTC_USD_last}

ETH_EUR: {ETH_EUR_last}
ETH_USD: {ETH_USD_last}

ETH_BTC: {ETH_BTC_last}
""".format(
    BTC_EUR_last = prices["BTC_EUR"]["last"],
    BTC_USD_last = prices["BTC_USD"]["last"],
    ETH_EUR_last = prices["ETH_EUR"]["last"],
    ETH_USD_last = prices["ETH_USD"]["last"],
    ETH_BTC_last = prices["ETH_BTC"]["last"]
)

    return text

def value_Bitcoin(
    price    = "last",
    currency = "EUR"
    ):

    return ticker_Bitcoin(
        currency = currency
    )[price]

    if day:
        URL = URL_day
    if hour:
        URL = URL_hour

    # Access a Bitcoin ticker.
    file_URL                = urlopen(URL)
    data_string             = file_URL.read()
    # Convert the data from string to dictionary.
    data_dictionary_strings = ast.literal_eval(data_string)
    #
    #    example hour ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1000.6,
    #        'last':      999.31,
    #        'low':       996.67,
    #        'open':      990.0,
    #        'timestamp': 1487600377.0,
    #        'volume':    21.11748617,
    #        'vwap':      998.34
    #    }
    #
    #    example day ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1004.0,
    #        'last':      999.31,
    #        'low':       985.31,
    #        'open':      990.0,
    #        'timestamp': 1487600340.0,
    #        'volume':    324.21451971,
    #        'vwap':      996.27
    #    }
    #
    # Convert numbers from strings to floats.
    data_dictionary = dict()
    for key in data_dictionary_strings:
        data_dictionary[key] = float(data_dictionary_strings[key])
    if currency != "EUR":
        # Convert currency EUR to requested currency.
        data_dictionary_currency = dict()
        converter_currency = currency_converter.CurrencyConverter()
        for key in data_dictionary:
            if key == "timestamp":
                data_dictionary_currency[key] = data_dictionary[key]
            else:
                data_dictionary_currency[key] =\
                    converter_currency.convert(
                        data_dictionary_strings[key],
                        "EUR",
                        currency
                    )

        return data_dictionary_currency

    return data_dictionary

def fluctuation_value_Bitcoin(
    days                      = 5,
    factor_standard_deviation = 1.6,
    details                   = False
    ):

    data_Bitcoin = data_historical_Bitcoin(
        days        = days,
        return_list = True
    )
    value_current_Bitcoin = value_Bitcoin()
    values_Bitcoin = [float(element[1]) for element in data_Bitcoin]
    mean_Bitcoin               = numpy.array(values_Bitcoin).mean()
    standard_deviation_Bitcoin = numpy.array(values_Bitcoin).std()
    low_Bitcoin  =\
        mean_Bitcoin - factor_standard_deviation * standard_deviation_Bitcoin
    high_Bitcoin =\
        mean_Bitcoin + factor_standard_deviation * standard_deviation_Bitcoin

    if details:
        print("Bitcoin values from last {days} days:\n\n{values}\n".format(
            days   = days,
            values = ", ".join([str(element) for element in values_Bitcoin])
        ))
        print("high bound Bitcoin:    {value}".format(value = high_Bitcoin))
        print("Bitcoin current value: {value}".format(
            value = value_current_Bitcoin
        ))
        print("low bound Bitcoin:     {value}".format(value = low_Bitcoin))

    if low_Bitcoin <= value_current_Bitcoin <= high_Bitcoin:

        return False

    else:

        return True

def fluctuation_value_LocalBitcoins(
    days                            = 3,
    factor_standard_deviation       = 1.6,
    details                         = False,
    filename_database_LocalBitcoins = "database_LocalBitcoins.db",
    ):

    datetime_time_start = datetime.datetime.utcnow() - datetime.timedelta(days = days)

    # get last few days of LocalBitcoins values from database
    values_LocalBitcoins = []
    database_LocalBitcoins = access_database(filename = filename_database_LocalBitcoins)
    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            values_LocalBitcoins.append(ast.literal_eval(row["values_GBP"])[0])
    # reverse order so latest first
    values_LocalBitcoins = values_LocalBitcoins[::-1]

    # current value
    value_current_LocalBitcoins = values_Bitcoin_LocalBitcoin()[0]

    mean_Bitcoin               = numpy.array(values_LocalBitcoins).mean()
    standard_deviation_Bitcoin = numpy.array(values_LocalBitcoins).std()
    low_Bitcoin  =\
        mean_Bitcoin - factor_standard_deviation * standard_deviation_Bitcoin
    high_Bitcoin =\
        mean_Bitcoin + factor_standard_deviation * standard_deviation_Bitcoin
    
    if details:
        print("high bound LocalBitcoins:    {value}".format(value = high_Bitcoin))
        print("LocalBitcoins current value: {value}".format(
            value = value_current_LocalBitcoins
        ))
        print("low bound LocalBitcoins:     {value}".format(value = low_Bitcoin))
    
    if low_Bitcoin <= value_current_LocalBitcoins <= high_Bitcoin:

        return False

    else:

        return True

def value_prediction_linear_Bitcoin(
    days_past   = 5, # past days data from which prediction is made
    days_future = 2, # number of days from now at which to predict value
    currency    = "EUR"
    ):

    data_Bitcoin = data_historical_Bitcoin(
        currency    = currency,
        days        = days_past,
        return_list = True
    )

    values_Bitcoin = [float(element[1]) for element in data_Bitcoin]
    data = [[day, value] for day, value in zip(list(range(-days_past, 0)), values_Bitcoin)]

    model_values = shijian.model_linear(data = data)
    b0 = model_values[0]
    b1 = model_values[1]
    x = days_future
    y = b0 + b1 * x

    return y

def ticker_Bitcoin(
    URL_hour = "https://www.bitstamp.net/api/v2/ticker/btceur",
    URL_day  = "https://www.bitstamp.net/api/v2/ticker_hour/btceur",
    currency = "EUR",
    hour     = True,
    day      = False
    ):

    if day:
        URL = URL_day
    if hour:
        URL = URL_hour

    # Access a Bitcoin ticker.
    file_URL                = urlopen(URL)
    data_string             = file_URL.read()
    # Convert the data from string to dictionary.
    data_dictionary_strings = ast.literal_eval(data_string)
    #
    #    example hour ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1000.6,
    #        'last':      999.31,
    #        'low':       996.67,
    #        'open':      990.0,
    #        'timestamp': 1487600377.0,
    #        'volume':    21.11748617,
    #        'vwap':      998.34
    #    }
    #
    #    example day ticker:
    #    {
    #        'ask':       999.31,
    #        'bid':       998.01,
    #        'high':      1004.0,
    #        'last':      999.31,
    #        'low':       985.31,
    #        'open':      990.0,
    #        'timestamp': 1487600340.0,
    #        'volume':    324.21451971,
    #        'vwap':      996.27
    #    }
    #
    # Convert numbers from strings to floats.
    data_dictionary = dict()
    for key in data_dictionary_strings:
        data_dictionary[key] = float(data_dictionary_strings[key])
    if currency != "EUR":
        # Convert currency EUR to requested currency.
        data_dictionary_currency = dict()
        converter_currency = currency_converter.CurrencyConverter()
        for key in data_dictionary:
            if key == "timestamp":
                data_dictionary_currency[key] = data_dictionary[key]
            else:
                data_dictionary_currency[key] =\
                    converter_currency.convert(
                        data_dictionary_strings[key],
                        "EUR",
                        currency
                    )

        return data_dictionary_currency

    return data_dictionary

def data_historical_Bitcoin(
    URL               = "https://api.coindesk.com/v1/bpi/historical/close.json",
    currency          = "EUR",
    date_start        = None, # YYYY-MM-DD
    date_stop         = None, # YYYY-MM-DD
    days              = None, # last days (start/stop dates alternative)
    return_list       = False,
    return_UNIX_times = False,
    sort_reverse      = False
    ):

    if days:
        time_current = datetime.datetime.utcnow()
        date_stop    = time_current.strftime("%Y-%m-%d")
        date_start   = (time_current -\
                       datetime.timedelta(days = days)).strftime("%Y-%m-%d")
    # Construct the URL using the API (http://www.coindesk.com/api/).
    URL = URL + "?currency=" + currency
    if date_start is not None and date_stop is not None:
        URL = URL + "&start=" + date_start + "&end=" + date_stop
    # Access the online data.
    file_URL                = urlopen(URL)
    data_string             = file_URL.read()
    # Convert the data from string to dictionary.
    data_dictionary_strings = ast.literal_eval(data_string)

    if return_list or return_UNIX_times:
        data_dictionary_list = list()
        for key in data_dictionary_strings["bpi"]:
            if return_UNIX_times:
                date = int(
                    time.mktime(
                        datetime.datetime.strptime(
                            key,
                            "%Y-%m-%d"
                        ).timetuple()
                    )
                )
            else:
                date = key
            data_dictionary_list.append(
                [date, float(data_dictionary_strings["bpi"][key])]
            )
        # sort
        data_dictionary_list_tmp = sorted(
            data_dictionary_list,
            key = lambda data_dictionary_list: (
                      data_dictionary_list[0],
                      data_dictionary_list[1]
                  ),
            reverse = sort_reverse
        )
        data_dictionary_list = data_dictionary_list_tmp

        return data_dictionary_list

    else:

        return data_dictionary_strings

def table_Bitcoin(
    currency   = "EUR",
    date_start = None, # YYYY-MM-DD
    date_stop  = None, # YYYY-MM-DD
    UNIX_times = False
    ):

    # Get Bitcoin value data.
    data = data_historical_Bitcoin(
        currency          = currency,
        date_start        = None, # YYYY-MM-DD
        date_stop         = None, # YYYY-MM-DD
        return_UNIX_times = UNIX_times,
        return_list       = True
    )
    
    # Return a table of the Bitcoin value data.
    table_contents = [[
                         "time",
                         "Bitcoin value ({currency})".format(
                             currency = currency
                         )
                     ]]
    table_contents.extend(data)
    table = pyprel.Table(
                contents = table_contents
            )

    return table

def save_graph_Bitcoin(
    currency   = "EUR",
    filename   = None,
    directory  = ".",
    overwrite  = True,
    date_start = None, # YYYY-MM-DD
    date_stop  = None, # YYYY-MM-DD
    days       = None  # last days (start/stop dates alternative)
    ):

    if filename is None:
        filename = "Bitcoin_value_{currency}_versus_time.png".format(
            currency = currency
        )

    data = data_historical_Bitcoin(
        currency          = currency,
        date_start        = date_start, # YYYY-MM-DD
        date_stop         = date_stop,  # YYYY-MM-DD
        days              = days,
        return_UNIX_times = True
    )

    datavision.save_graph_matplotlib(
        values       = data,
        title_axis_x = "time",
        title_axis_y = "value ({currency})".format(
                           currency = currency
                       ),
        filename     = filename,
        directory    = directory,
        overwrite    = overwrite,
        line         = True,
        line_width   = 0.5,
        time_axis_x  = True
    )

def save_graph_LocalBitcoins(
    filename          = None,
    directory         = ".",
    overwrite         = True,
    filename_database = "database_LocalBitcoins.db"
    ):

    if filename is None:
        filename = "LocalBitcoins_Bitcoin_lowest_price_GBP_versus_time.png"

    database = access_database(filename = filename_database)

    data = []
    for row in database["LocalBitcoins"]:
        data.append([row["time_UNIX"], ast.literal_eval(row["values_GBP"])[0]])

    datavision.save_graph_matplotlib(
        values       = data,
        title_axis_x = "time",
        title_axis_y = "LBC low (GBP)",
        filename     = filename,
        directory    = directory,
        overwrite    = overwrite,
        line         = True,
        line_width   = 0.5,
        time_axis_x  = True,
        time_style   = "%Y-%m-%dT%H%MZ", # e.g. "%Y-%m-%d", "%Y-%m-%dT%H%MZ",
        font_size    = 8
    )

def save_graph_Bitcoin_LocalBitcoins(
    filename                        = "Bitcoin_LocalBitcoins_lowest_price_GBP.png",
    directory                       = ".",
    overwrite                       = True,
    filename_database_Bitcoin       = "database_Bitcoin_GBP.db",
    filename_database_LocalBitcoins = "database_LocalBitcoins.db",
    time_start                      = "2017-03-08T1436Z" # YYYY-MM-DDTHHMMZ
    ):

    """
    Save a graph of Bitcoin GBP values versus LocalBitcoins lowest GBP values.
    """

    x_Bitcoin       = []
    y_Bitcoin       = []
    x_LocalBitcoins = []
    y_LocalBitcoins = []

    database_Bitcoin       = access_database(filename = filename_database_Bitcoin)
    database_LocalBitcoins = access_database(filename = filename_database_LocalBitcoins)

    datetime_time_start = datetime.datetime.strptime(time_start, "%Y-%m-%dT%H%MZ")

    for row in database_Bitcoin["Bitcoin"]:
        row_time = datetime.datetime.fromtimestamp(row["time"]) + datetime.timedelta(hours = 24)
        if row_time >= datetime_time_start:
            x_Bitcoin.append(row_time)
            y_Bitcoin.append(row["value"])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins.append(row_time)
            y_LocalBitcoins.append(ast.literal_eval(row["values_GBP"])[0])

    datavision.save_multigraph_2D_matplotlib(
        variables_x      = [x_Bitcoin, x_LocalBitcoins],
        variables_y      = [y_Bitcoin, y_LocalBitcoins],
        variables_names  = ["Bitcoin", "LocalBitcoins"],
        title            = "Bitcoin values versus LocalBitcoins lowest price",
        title_axis_x     = "time",
        title_axis_y     = "Bitcoin value (GBP)",
        filename         = filename,
        directory        = directory,
        overwrite        = overwrite,
        LaTeX            = False,
        markers          = False,
        marker_size      = 0.8,
        line             = True,
        line_width       = 0.5,
        palette_name     = "palette1",
        time_axis_x      = True,
        time_style       = "%Y-%m-%d",
        font_size        = 10
    )

def save_graphs_Bitcoin_LocalBitcoins(
    filename                        = "Bitcoin_LocalBitcoins_prices_GBP.png",
    directory                       = ".",
    overwrite                       = True,
    filename_database_Bitcoin       = "database_Bitcoin_GBP.db",
    filename_database_LocalBitcoins = "database_LocalBitcoins.db",
    time_start                      = "2017-03-08T1436Z" # YYYY-MM-DDTHHMMZ
    ):

    """
    Save a graph of the LocalBitcoins 5 lowest GBP values and Bitcoin value.
    """

    x_Bitcoin         = []
    y_Bitcoin         = []

    x_LocalBitcoins_1 = []
    y_LocalBitcoins_1 = []

    x_LocalBitcoins_2 = []
    y_LocalBitcoins_2 = []

    x_LocalBitcoins_3 = []
    y_LocalBitcoins_3 = []

    x_LocalBitcoins_4 = []
    y_LocalBitcoins_4 = []

    x_LocalBitcoins_5 = []
    y_LocalBitcoins_5 = []

    database_Bitcoin       = access_database(filename = filename_database_Bitcoin)
    database_LocalBitcoins = access_database(filename = filename_database_LocalBitcoins)

    datetime_time_start = datetime.datetime.strptime(time_start, "%Y-%m-%dT%H%MZ")

    for row in database_Bitcoin["Bitcoin"]:
        row_time = datetime.datetime.fromtimestamp(row["time"]) + datetime.timedelta(hours = 24)
        if row_time >= datetime_time_start:
            x_Bitcoin.append(row_time)
            y_Bitcoin.append(row["value"])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_1.append(row_time)
            y_LocalBitcoins_1.append(ast.literal_eval(row["values_GBP"])[0])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_2.append(row_time)
            y_LocalBitcoins_2.append(ast.literal_eval(row["values_GBP"])[1])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_3.append(row_time)
            y_LocalBitcoins_3.append(ast.literal_eval(row["values_GBP"])[2])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_4.append(row_time)
            y_LocalBitcoins_4.append(ast.literal_eval(row["values_GBP"])[3])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_5.append(row_time)
            y_LocalBitcoins_5.append(ast.literal_eval(row["values_GBP"])[4])

    datavision.save_multigraph_2D_matplotlib(
        variables_x      = [
                           x_Bitcoin,
                           x_LocalBitcoins_1,
                           x_LocalBitcoins_2,
                           x_LocalBitcoins_3,
                           x_LocalBitcoins_4,
                           x_LocalBitcoins_5
                           ],
        variables_y      = [
                           y_Bitcoin,
                           y_LocalBitcoins_1,
                           y_LocalBitcoins_2,
                           y_LocalBitcoins_3,
                           y_LocalBitcoins_4,
                           y_LocalBitcoins_5
                           ],
        variables_names  = [
                           "Bitcoin",
                           "LocalBitcoins 1",
                           "LocalBitcoins 2",
                           "LocalBitcoins 3",
                           "LocalBitcoins 4",
                           "LocalBitcoins 5"
                           ],
        title            = "Bitcoin value versus LocalBitcoins lowest prices",
        title_axis_x     = "time",
        title_axis_y     = "Bitcoin value (GBP)",
        filename         = filename,
        directory        = directory,
        overwrite        = overwrite,
        LaTeX            = False,
        markers          = False,
        marker_size      = 0.8,
        line             = True,
        line_width       = 0.3,
        palette_name     = "palette1",
        time_axis_x      = True,
        time_style       = "%Y-%m-%d",
        font_size        = 10
    )

def save_graphs_Bitcoin_LocalBitcoins_Bollinger_bands(
    window                          = 20,
    directory                       = ".",
    overwrite                       = True,
    filename_database_Bitcoin       = "database_Bitcoin_GBP.db",
    filename_database_LocalBitcoins = "database_LocalBitcoins.db",
    time_start                      = "2017-03-08T1436Z", # YYYY-MM-DDTHHMMZ
    line_width                      = 0.4
    ):

    """
    Save a graphs of the LocalBitcoins 5 lowest GBP values and Bitcoin value.
    """

    filenames = [
        "Bitcoin_Bollinger_bands.png",
        "LocalBitcoins_1_Bollinger_bands.png",
        "LocalBitcoins_2_Bollinger_bands.png",
        "LocalBitcoins_3_Bollinger_bands.png",
        "LocalBitcoins_4_Bollinger_bands.png",
        "LocalBitcoins_5_Bollinger_bands.png",
    ]

    x_Bitcoin         = []
    y_Bitcoin         = []

    x_LocalBitcoins_1 = []
    y_LocalBitcoins_1 = []

    x_LocalBitcoins_2 = []
    y_LocalBitcoins_2 = []

    x_LocalBitcoins_3 = []
    y_LocalBitcoins_3 = []

    x_LocalBitcoins_4 = []
    y_LocalBitcoins_4 = []

    x_LocalBitcoins_5 = []
    y_LocalBitcoins_5 = []

    database_Bitcoin       = access_database(filename = filename_database_Bitcoin)
    database_LocalBitcoins = access_database(filename = filename_database_LocalBitcoins)

    datetime_time_start = datetime.datetime.strptime(time_start, "%Y-%m-%dT%H%MZ")

    for row in database_Bitcoin["Bitcoin"]:
        row_time = datetime.datetime.fromtimestamp(row["time"]) + datetime.timedelta(hours = 24)
        if row_time >= datetime_time_start:
            x_Bitcoin.append(row_time)
            y_Bitcoin.append(row["value"])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_1.append(row_time)
            y_LocalBitcoins_1.append(ast.literal_eval(row["values_GBP"])[0])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_2.append(row_time)
            y_LocalBitcoins_2.append(ast.literal_eval(row["values_GBP"])[1])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_3.append(row_time)
            y_LocalBitcoins_3.append(ast.literal_eval(row["values_GBP"])[2])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_4.append(row_time)
            y_LocalBitcoins_4.append(ast.literal_eval(row["values_GBP"])[3])

    for row in database_LocalBitcoins["LocalBitcoins"]:
        row_time = datetime.datetime.fromtimestamp(row["time_UNIX"])
        if row_time >= datetime_time_start:
            x_LocalBitcoins_5.append(row_time)
            y_LocalBitcoins_5.append(ast.literal_eval(row["values_GBP"])[4])

    datavision.save_plot_Bollinger_bands(
        x           = numpy.array(x_Bitcoin),
        y           = numpy.array(y_Bitcoin),
        window      = window,
        title       = "Bitcoin",
        time_axis_x = True,
        line_width  = line_width,
        filename    = filenames[0],
        directory   = directory
    )

    datavision.save_plot_Bollinger_bands(
        x           = numpy.array(x_LocalBitcoins_1),
        y           = numpy.array(y_LocalBitcoins_1),
        window      = window,
        title       = "LocalBitcoins 1",
        time_axis_x = True,
        line_width  = line_width,
        filename    = filenames[1],
        directory   = directory
    )

    datavision.save_plot_Bollinger_bands(
        x           = numpy.array(x_LocalBitcoins_2),
        y           = numpy.array(y_LocalBitcoins_2),
        window      = window,
        title       = "LocalBitcoins 2",
        time_axis_x = True,
        line_width  = line_width,
        filename    = filenames[2],
        directory   = directory
    )

    datavision.save_plot_Bollinger_bands(
        x           = numpy.array(x_LocalBitcoins_3),
        y           = numpy.array(y_LocalBitcoins_3),
        window      = window,
        title       = "LocalBitcoins 3",
        time_axis_x = True,
        line_width  = line_width,
        filename    = filenames[3],
        directory   = directory
    )

    datavision.save_plot_Bollinger_bands(
        x           = numpy.array(x_LocalBitcoins_4),
        y           = numpy.array(y_LocalBitcoins_4),
        window      = window,
        title       = "LocalBitcoins 4",
        time_axis_x = True,
        line_width  = line_width,
        filename    = filenames[4],
        directory   = directory
    )

    datavision.save_plot_Bollinger_bands(
        x           = numpy.array(x_LocalBitcoins_5),
        y           = numpy.array(y_LocalBitcoins_5),
        window      = window,
        title       = "LocalBitcoins 5",
        time_axis_x = True,
        line_width  = line_width,
        filename    = filenames[5],
        directory   = directory
    )

def save_graph_LocalBitcoins_days(
    filename          = "LocalBitcoins_Bitcoin_lowest_price_GBP_days.png",
    directory         = ".",
    overwrite         = True,
    filename_database = "database_LocalBitcoins.db"
    ):

    if filename is None:
        filename = "LocalBitcoins_Bitcoin_lowest_price_GBP_days.png"

    database = access_database(filename = filename_database)

    data_datetime         = []
    data_time_through_day = []
    data_value            = []
    for row in database["LocalBitcoins"]:
        time_row = datetime.datetime.fromtimestamp(row["time_UNIX"])
        time_through_day =\
            time_row -\
            datetime.datetime.combine(time_row.date(), datetime.time())
        data_datetime.append(time_row)
        data_time_through_day.append((time_through_day.seconds / 86400) * 24)
        data_value.append(ast.literal_eval(row["values_GBP"])[0])

    data                         = pd.DataFrame()
    data["value"]                = data_value
    data["time_through_day"]     = data_time_through_day
    data.index                   = data_datetime
    data.index.name              = "datetime"
    data["value_day_normalized"] = data["value"].div(data.resample("D")["value"].transform("sum"))

    # trim
    data_plot = []
    for data_time_through_day, data_value in zip(data["time_through_day"], data["value_day_normalized"]):
        if data_value < 0.025:
            data_plot.append([data_time_through_day, data_value])

    #data_plot = [[data_time_through_day, data_value] for data_time_through_day, data_value in zip(data["time_through_day"], data["value_day_normalized"])]

    datavision.save_graph_matplotlib(
        values       = data_plot,
        title_axis_x = "time (hours)",
        title_axis_y = "LBC low (GBP, normalised to unity)",
        filename     = filename,
        directory    = directory,
        overwrite    = overwrite,
        line         = False,
        line_width   = 0.5,
        #time_axis_x  = True,
        #time_style   = "%H%MZ", # e.g. "%Y-%m-%d", "%Y-%m-%dT%H%MZ",
        font_size    = 8,
        marker_size  = 2
    )

def save_graph_LocalBitcoins_weeks(
    filename          = "LocalBitcoins_Bitcoin_lowest_price_GBP_weeks.png",
    directory         = ".",
    overwrite         = True,
    filename_database = "database_LocalBitcoins.db",
    normalize         = True
    ):

    if filename is None:
        filename = "LocalBitcoins_Bitcoin_lowest_price_GBP_weeks.png"

    database = access_database(filename = filename_database)

    data = []
    for row in database["LocalBitcoins"]:
        data.append(
            [
                datetime.datetime.fromtimestamp(row["time_UNIX"]),
                ast.literal_eval(row["values_GBP"])[0]
            ]
        )

    df = pd.DataFrame(data, columns = ["time", "LBC1"])

    df["weekday"]          = df["time"].dt.weekday
    df["weekday_name"]     = df["time"].dt.weekday_name
    df["time_through_day"] = df["time"].map(lambda x: x - datetime.datetime.combine(x.date(), datetime.time()))

    def days_through_week(row):

        return row["weekday"] + row["time_through_day"] / (24 * numpy.timedelta64(1, "h"))

    df["days_through_week"] = df.apply(lambda row: days_through_week(row), axis = 1)

    #data_plot = df.as_matrix(columns = ["days_through_week", "LBC1"]).tolist()
    #
    #datavision.save_graph_matplotlib(
    #    values       = data_plot,
    #    title_axis_x = "days through week",
    #    title_axis_y = "LBC low (GBP)", #"LBC low (GBP, normalised to unity)",
    #    filename     = filename,
    #    directory    = directory,
    #    overwrite    = overwrite,
    #    line         = False,
    #    line_width   = 0.5,
    #    #time_axis_x  = True,
    #    #time_style   = "%H%MZ", # e.g. "%Y-%m-%d", "%Y-%m-%dT%H%MZ",
    #    font_size    = 8,
    #    marker_size  = 2
    #)

    datasets = []

    dataset = []
    previous_days_through_week = 0
    for days_through_week, LBC1 in zip(df["days_through_week"], df["LBC1"]):
        if abs(days_through_week - previous_days_through_week) < 5:
            dataset.append([days_through_week, LBC1])
        else:
            datasets.append(dataset)
            dataset = []
        previous_days_through_week = days_through_week

    plt.ioff()

    fig = plt.figure(figsize = (15, 8))

    for dataset in datasets:

        x = [datum[0] for datum in dataset]
        y = [datum[1] for datum in dataset]
        if normalize:
            y = datavision.normalize_to_range(y)

        plt.plot(
            x,
            y,
            linestyle = "-",
            linewidth = 1.3
        )

    #plt.axes().set_aspect(1 / plt.axes().get_data_ratio())

    plt.ylabel("LBC low (GBP)")
    plt.xticks(
        [
            0.5,
            1.5,
            2.5,
            3.5,
            4.5,
            5.5,
            6.5
        ],
        [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    plt.savefig(
        directory + "/" + filename,
        dpi = 700
    )
    plt.close()

def graph_TTY_Bitcoin(
    currency   = "EUR",
    date_start = None, # YYYY-MM-DD
    date_stop  = None, # YYYY-MM-DD
    days       = None  # last days (start/stop dates alternative)
    ):

    data = data_historical_Bitcoin(
        currency          = currency,
        date_start        = date_start, # YYYY-MM-DD
        date_stop         = date_stop,  # YYYY-MM-DD
        days              = days,
        return_UNIX_times = True
    )
    x = [element[0] for element in data]
    y = [element[1] for element in data]
    plot = datavision.TTYFigure()
    tmp = plot.plot(
        x,
        y,
        marker = "_o",
        plot_slope = False
    )

    return tmp

def create_database(
    filename = None
    ):

    os.system(
        "sqlite3 " + \
        filename + \
        " \"create table aTable(field1 int); drop table aTable;\""
    )

def access_database(
    filename = "database.db"
    ):

    database = dataset.connect("sqlite:///" + str(filename))

    return database

def save_database_Bitcoin(
    filename   = "database_Bitcoin.db",
    currency   = "EUR",
    date_start = "2010-07-17",
    date_stop  = None
    ):

    if date_stop is None:
        date_stop = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    data = data_historical_Bitcoin(
        currency          = currency,
        date_start        = date_start,
        date_stop         = date_stop,
        return_list       = True,
        return_UNIX_times = True
    )
    database = access_database(filename = filename)
    table    = database["Bitcoin"]
    progress = shijian.Progress()
    progress.engage_quick_calculation_mode()
    number_of_entries = len(data)
    for index, element in enumerate(data):
        table.insert(dict(
            time      = element[0],
            value     = element[1]
        ))
        print(progress.add_datum(fraction = index / number_of_entries))

def table_database(
    filename           = "database.db",
    name_table         = "Bitcoin",
    include_attributes = None,
    rows_limit         = None
    ):

    database = access_database(filename = filename)

    return pyprel.Table(
        contents = pyprel.table_dataset_database_table(
            table              = database[name_table],
            include_attributes = include_attributes,
            rows_limit         = rows_limit
        )
    )

def quote_Kraken(
    asset_1 = "XBT",
    asset_2 = "EUR",
    URL     = "https://api.kraken.com/0/public/Ticker?pair="
    ):

    """
    Access the Kraken API and return the value of a specified Kraken asset (by
    default XBT (BTC)) in terms of a specified Kraken asset (by default EUR) as
    a float.
    """

    try:

        results = requests.get(URL + asset_1 + asset_2).json()
        value   = results["result"]["X" + asset_1 + "Z" + asset_2]["c"][0]

        return float(value)

    except:

        print("error -- could not access Kraken API")

        return None

def quote_arbitrage_data_Kraken_LocalBitcoins_UK():

    """
    Get the last Kraken price in EUR. Convert this value to GBP using the
    current exchange rate. Get the current 5 lowest prices on LocalBitcoins UK
    in GBP. Divide the third lowest LocalBitcoins UK price by the last Kraken
    price in GBP. Return all of this data in a dictionary.
    """

    try:

        Kraken_last_price_EUR = quote_Kraken()
        Kraken_last_price_GBP = convert_currency(
                                    value      = Kraken_last_price_EUR,
                                    currency_1 = "EUR",
                                    currency_2 = "GBP"
                                )
        LBC                   = values_Bitcoin_LocalBitcoin()

        results = {
            "datetime":               datetime.datetime.utcnow(),
            "Kraken_last_price_EUR":  Kraken_last_price_EUR,
            "Kraken_last_price_GBP":  Kraken_last_price_GBP,
            "LBC_1_GBP":              LBC[0],
            "LBC_2_GBP":              LBC[1],
            "LBC_3_GBP":              LBC[2],
            "LBC_4_GBP":              LBC[3],
            "LBC_5_GBP":              LBC[4],
            "arbitrage_Kraken_LBC_1": LBC[0] / Kraken_last_price_GBP,
            "arbitrage_Kraken_LBC_2": LBC[1] / Kraken_last_price_GBP,
            "arbitrage_Kraken_LBC_3": LBC[2] / Kraken_last_price_GBP,
            "arbitrage_Kraken_LBC_4": LBC[3] / Kraken_last_price_GBP,
            "arbitrage_Kraken_LBC_5": LBC[4] / Kraken_last_price_GBP
        }

        return results

    except:

        print("error -- could not convert currency or access Kraken API")

        return None

def loop_save_arbitrage_data_Kraken_LocalBitcoins_UK(
    filename = "arbitrage_Kraken_LocalBitcoins_UK.csv",
    interval = 900,
    verbose  = True
    ):

    """
    Loop save arbitrage data for Kraken and LocalBitcoins UK to a CSV file.
    """

    pp = pprint.PrettyPrinter(indent = 4, width = 1)

    while True:

        results = quote_arbitrage_data_Kraken_LocalBitcoins_UK()

        if results:

            df = pd.DataFrame()
            df = df.append(results, ignore_index = True)
            df.index = df["datetime"]
            del df["datetime"]

            if not os.path.isfile(filename):

                header = True

            else:

                header = False

            with open(filename, "a") as file_arbitrage:
                df.to_csv(file_arbitrage, header = header)

            if verbose:

                print("")
                pp.pprint(results)

        print("\nnext recording in {interval} s".format(interval = interval))

        time.sleep(interval)

def values_Bitcoin_LocalBitcoin(
    URL = "https://localbitcoins.com/buy-bitcoins-online/"
          "GB/united-kingdom/national-bank-transfer/.json"
    ):

    file_URL    = urlopen(URL)
    data_string = file_URL.read()
    data_JSON   = json.loads(data_string)

    advertisements = data_JSON["data"]["ad_list"]
    advertisement_prices = []
    for advertisement in advertisements:
        advertisement_prices.append(float(advertisement["data"]["temp_price"]))
    advertisement_prices.sort()

    return advertisement_prices

def save_current_values_LocalBitcoins_to_database(
    filename   = "database_LocalBitcoins.db"
    ):

    # Data saved to the database is a UTC datetime timestamp, a UTC UNIX,
    # timestamp, the LocalBitcoins API string returned (JSON) and a list of the
    # current prices in GBP.

    timestamp      = datetime.datetime.utcnow()
    timestamp_UNIX = (timestamp -\
                     datetime.datetime.utcfromtimestamp(0)).total_seconds()

    # buying prices

    URL = "https://localbitcoins.com/buy-bitcoins-online/"\
          "GB/united-kingdom/national-bank-transfer/.json"

    file_URL    = urlopen(URL)
    data_string = file_URL.read()
    data_JSON   = json.loads(data_string)

    advertisements = data_JSON["data"]["ad_list"]
    advertisement_prices = []
    for advertisement in advertisements:
        advertisement_prices.append(float(advertisement["data"]["temp_price"]))
    advertisement_prices.sort()

    # selling prices

    URL = "https://localbitcoins.com/sell-bitcoins-online/"\
        "GB/united-kingdom/national-bank-transfer/.json"

    file_URL_sell    = urlopen(URL)
    data_string_sell = file_URL_sell.read()
    data_JSON_sell   = json.loads(data_string_sell)

    advertisements_sell = data_JSON_sell["data"]["ad_list"]
    advertisement_prices_sell = []
    for advertisement_sell in advertisements_sell:
        advertisement_prices_sell.append(float(advertisement_sell["data"]["temp_price"]))
    advertisement_prices_sell.sort()

    # save to database

    database = access_database(filename = filename)
    table    = database["LocalBitcoins"]

    table.insert(dict(
        time             = timestamp,
        time_UNIX        = timestamp_UNIX,
        JSON_GB_NBT      = str(data_string),
        JSON_GB_NBT_sell = str(data_string_sell),
        values_GBP       = str(advertisement_prices),
        values_GBP_sell  = str(advertisement_prices_sell)
    ))

def loop_save_current_values_LocalBitcoins_to_database(
    filename    = "database_LocalBitcoins.db",
    time_period = 1800, # seconds (30 minutes)
    verbose     = True
    ):

    while True:
        if verbose:
            print(
                "{time} save LocalBitcoins current data to database "\
                "{filename} (next save in {seconds} s)".format(
                    time     = datetime.datetime.utcnow(),
                    filename = filename,
                    seconds  = time_period
                )
            )
        save_current_values_LocalBitcoins_to_database(
            filename = filename
        )
        time.sleep(time_period)

def table_database_LocalBitcoins(
    filename           = "database_LocalBitcoins.db",
    name_table         = "LocalBitcoins",
    include_attributes = ["time", "time_UNIX", "values_GBP"],
    rows_limit         = None
    ):

    return table_database(
        filename           = filename,
        name_table         = name_table,
        include_attributes = include_attributes,
        rows_limit         = rows_limit
    )

def save_database_LocalBitcoins_to_DataFrame_PKL(
    filename_database = "database_LocalBitcoins.db",
    filename_PKL      = "LBC.pkl"
    ):

    """
    Save a subset of information of the LocalBitcoins database to a pickled
    DataFrame, specifically the 5 lowest GBP prices, with some additional
    variables, including weekday, weekday name, time through day and fraction
    through day.
    """

    datebase = dataset.connect("sqlite:///" + filename_database)

    data = []
    for row in database["LocalBitcoins"]:
        data.append(
            [
                datetime.datetime.fromtimestamp(row["time_UNIX"]),
                ast.literal_eval(row["values_GBP"])[0],
                ast.literal_eval(row["values_GBP"])[1],
                ast.literal_eval(row["values_GBP"])[2],
                ast.literal_eval(row["values_GBP"])[3],
                ast.literal_eval(row["values_GBP"])[4]
            ]
        )

    LBC = pd.DataFrame(
        data,
        columns = [
            "datetime",
            "LBC1",
            "LBC2",
            "LBC3",
            "LBC4",
            "LBC5"
        ]
    )

    LBC["weekday"]              = LBC["datetime"].dt.weekday
    LBC["weekday_name"]         = LBC["datetime"].dt.weekday_name
    LBC["time_through_day"]     = LBC["datetime"].map(lambda x: x - datetime.datetime.combine(x.date(), datetime.time()))
    LBC["fraction_through_day"] = LBC["time_through_day"].map(lambda x: x / datetime.timedelta(hours = 24))

    LBC.index = LBC["datetime"]
    del LBC["datetime"]
    LBC.index = pd.to_datetime(LBC.index.values)

    LBC.to_pickle(filename_PKL)

def instrument_DataFrame(
    instrument = None,
    date_start = "2010-01-01"
    ):

    """
    Access the following data of an instrument:

    - Open
    - High
    - Low
    - Close
    - Volume

    Return a DataFrame with the index set to datetime (DatetimeIndex) and with
    the columns Open, High, Low, Close, Volume and Instrument.
    """

    print("access instrument {instrument}".format(instrument = instrument))

    URL = "http://www.google.com/finance/historical"\
          "?q=NASDAQ:{instrument}"\
          "&startdate={date_start}"\
          "&output=csv".format(
              instrument = instrument,
              date_start = date_start
          )

    CSV = urlopen(URL).read()[3:].decode("utf-8").split()

    df = pd.read_csv(
        io.StringIO("\n".join(CSV)),
        na_values = None
    )
    df.index = df["Date"]
    del df["Date"]
    df.index = pd.to_datetime(df.index.values)
    df["Instrument"] = instrument

    return df

def merge_instrument_DataFrames(
    dfs          = None,
    change_names = True
    ):

    """
    Return a DataFrame of instrument DataFrames merged on the datetime index
    (DatetimeIndex). By default, the names of variables are changed for merging
    and the Instrument variable is removed because it is added to the changed
    names of the other variables.
    """

    if not change_names:

        return pd.concat(dfs)

    else:

        _dfs = []
        for df in dfs:
            instrument = df["Instrument"].values[0]
            df = df.rename(columns = {
                                         "Open":   "Open_"   + instrument,
                                         "High":   "High_"   + instrument,
                                         "Low":    "Low_"    + instrument,
                                         "Close":  "Close_"  + instrument,
                                         "Volume": "Volume_" + instrument
                                     }
                          )
            del df["Instrument"]
            _dfs.append(df)

        return functools.reduce(
                   lambda left, right: pd.merge(
                                           left,
                                           right,
                                           left_index  = True,
                                           right_index = True
                                       )
                                       , _dfs
               )

def get_currencies(
    URL = "https://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json"
    ):

    resources = requests.get(URL).json()["list"]["resources"]

    df = pd.DataFrame()

    for resource in resources:

        fields = resource["resource"]["fields"]

        df = df.append(
            {
                "datetime": datetime.datetime.strptime(fields["utctime"], "%Y-%m-%dT%H:%M:%S+0000"),
                "name":     fields["name"],
                "symbol":   fields["symbol"],
                "price":    fields["price"]
            },
            ignore_index = True
        )

    df.index = df["datetime"]
    del df["datetime"]

    return df

def convert_currency(
    value      = 1,
    currency_1 = "EUR",
    currency_2 = "GBP"
    ):

    df = get_currencies()

    rate_1 = float(df.query("(name == 'USD/" + currency_1 + "')")["price"].values[0])
    rate_2 = float(df.query("(name == 'USD/" + currency_2 + "')")["price"].values[0])
    result = float(value) * rate_2 / rate_1

    return result
