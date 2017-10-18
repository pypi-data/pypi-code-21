#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius_save_stock_prices                                                   #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program saves Google Finance stock prices to CSV.                       #
#                                                                              #
# copyright (C) 2017 Will Breaden Madden, wbm@protonmail.ch                    #
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

usage:
    program [options]

options:
    -h, --help               display help message
    --version                display version and exit

    --instruments=TEXT       comma-separated instruments list to save (none for
                             default list)          [default: none]
    --filename_CSV=FILENAME  filename of output CSV [default: stocks.csv]
    --filename_PKL=FILENAME  filename of output PKL [default: stocks.pkl]
    --output_CSV=BOOL        save to CSV            [default: true]
    --output_PKL=BOOL        save to PKL            [default: true]
"""

import docopt
import io
try:
    from urllib.request import urlopen
except:
    from urllib2 import urlopen

import denarius
import pandas as pd

name    = "denarius_save_stock_prices"
version = "2017-10-08T1836Z"
logo    = None

def main(options):

    instruments  = options["--instruments"]
    filename_CSV = options["--filename_CSV"]
    filename_PKL = options["--filename_PKL"]
    output_CSV   = options["--output_CSV"].lower() == "true"
    output_PKL   = options["--output_PKL"].lower() == "true"

    if instruments == "none":
        instruments = [
            "AAPL",
            "GOOGL",
            "GOOG",
            "MSFT",
            #"FB",
            "ORCL",
            #"TSM",
            "INTC",
            "CSCO",
            #"IBM",
            #"SAP",
            #"AVGO",
            #"DCM",
            "NVDA",
            "QCOM"
        ]
    else:
        instruments = instruments.split(",")

    dfs = []
    for instrument in instruments:
        dfs.append(denarius.instrument_DataFrame(instrument = instrument))
    df = denarius.merge_instrument_DataFrames(dfs = dfs)

    if output_CSV:
        print("save to " + filename_CSV)
        df.to_csv(filename_CSV)
    if output_PKL:
        print("save to " + filename_PKL)
        df.to_pickle(filename_PKL)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
