#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# detect_transaction_RBS                                                       #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program gets the recent transactions of an RBS account using Firefox    #
# and Selenium and searches the transactions for a specified reference. It     #
# does this in a loop until the transaction is detected.                       #
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
    -h, --help              display help message
    --version               display version and exit

    --reference=TEXT        reference text to search for   [default: none]

    --interval=INT          time between recordings (s)    [default: 120]

    --credentials=FILEPATH  credentials file               [default: ~/.rbs]

    --sleep_time=INT        time between web interactions  [default: 1]
"""

import docopt
import time
import sys

import RBS

name    = "detect_transaction_RBS"
version = "2017-11-28T1851Z"
logo    = None

def main(options):

    reference            =     options["--reference"]
    interval             = int(options["--interval"])
    filepath_credentials =     options["--credentials"]
    sleep_time           = int(options["--sleep_time"])

    if reference == "none":
        print("reference not specified")
        sys.exit()

    found = False

    while not found:

        try:
            status = RBS.account_status(
                filepath_credentials = filepath_credentials,
                sleep_time           = sleep_time
            )
            df = status["transactions"]
            if df[df["description"].str.contains(reference)].values.any():
                print("transaction found:\n\n" + str(df[df["description"].str.contains(reference)]))
                found = True
            else:
                print("\ntransaction not found -- current transactions:\n")
                print(df)
                print("\nwait " + str(interval) + " s")
        except:
            print("error getting transactions")
            pass
        if not found:
            time.sleep(interval)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
