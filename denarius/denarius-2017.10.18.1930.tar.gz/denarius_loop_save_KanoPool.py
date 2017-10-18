#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius_loop_save_KanoPool                                                  #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program loop records KanoPool address data.                             #
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
    -h, --help           display help message
    --version            display version and exit

    --addresses=TEXT     address or comma-separated addresses
    --interval=FLOAT     loop time interval (s)        [default: 60]
    --file_CSV=FILENAME  filename for saving CSV data  [default: KanoPool.csv]
"""

from bs4 import BeautifulSoup
import docopt
import json
from collections import OrderedDict
import os
import requests
import sys
import time

name    = "denarius_loop_save_KanoPool"
version = "2017-07-10T1020Z"
logo    = name

def main(options):

    addresses    =       options["--addresses"]
    interval     = float(options["--interval"])
    filename_CSV =       options["--file_CSV"]

    if not addresses:
        print("error -- no address specified")
        sys.exit()

    addresses = addresses.split(",")

    variables = OrderedDict([
        ("hashrate5m",  "hash_rate_TH/s_5m"),
        ("hashrate1hr", "hash_rate_TH/s_1hr"),
        ("hashrate1d",  "hash_rate_TH/s_1d"),
        ("lastupdate",  "last_update"),
        ("workers",     "workers"),
        ("shares",      "shares"),
        ("bestshare",   "best_share")
    ])

    # if new file, add header
    if not os.path.isfile(filename_CSV):
        with open(filename_CSV, "a") as file_CSV:
            line = ["address"]
            line.extend(list(variables.values()))
            file_CSV.write(",".join(line))

    while True:

        for address in addresses:

            try:
                URL         = "https://www.kano.is/address.php?a=" + address
                data_string = requests.get(URL).text
                soup        = BeautifulSoup(data_string, "lxml")
                data_JSON   = json.loads(soup.findAll("body")[0].get_text())

                line = [address]
                print("\naddress: {address}".format(address = address))
                for variable_key in list(variables.keys()):
                    if "hashrate" in variable_key:
                        value = data_JSON[variable_key].rstrip("T")
                    else:
                        value = data_JSON[variable_key]
                    print("{variable}: {value}".format(
                        variable = variables[variable_key],
                        value    = value
                    ))
                    line.append(str(value))
                with open(filename_CSV, "ab") as file_CSV:
                    file_CSV.write("\n" + ",".join(line))
            except:
                pass

        print("\nwait {interval} s".format(interval = interval))
        time.sleep(interval)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
