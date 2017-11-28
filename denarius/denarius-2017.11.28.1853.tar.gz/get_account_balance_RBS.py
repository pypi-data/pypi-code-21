#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# get_account_balance_RBS                                                      #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program returns the balance and recent transactions of an RBS account   #
# using Firefox and Selenium. The default behaviour is to open the RBS web     #
# interface and to display the balance and recent transactions in the          #
# terminal, leaving the browser open. The behaviour instead can be set to loop #
# with a certain time interval, closing the browser and displaying the balance #
# and recent transactions in the terminal continuously.                        #
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

    --loop
    --interval=INT          time between recordings (s)    [default: 120]

    --credentials=FILEPATH  credentials file               [default: ~/.rbs]

    --sleep_time=INT        time between web interactions  [default: 1]
"""

import docopt
import time

import RBS

name    = "get_account_balance_RBS"
version = "2017-11-28T1853Z"
logo    = None

def main(options):

    loop                 =     options["--loop"]
    interval             = int(options["--interval"])
    filepath_credentials =     options["--credentials"]
    sleep_time           = int(options["--sleep_time"])

    if loop:

        while True:
            text = RBS.printout(
                filepath_credentials = filepath_credentials,
                log_out              = True,
                close_driver         = True,
                sleep_time           = sleep_time
            )
            print(text)
            time.sleep(interval)

    else:

        text = RBS.printout(
            filepath_credentials = filepath_credentials,
            log_out              = False,
            close_driver         = False,
            sleep_time           = sleep_time
        )
        print(text)

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)
