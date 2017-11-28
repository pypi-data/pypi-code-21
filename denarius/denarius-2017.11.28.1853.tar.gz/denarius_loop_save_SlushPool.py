#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# denarius_loop_save_SlushPool                                                 #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program loop records SlushPool address data.                            #
#                                                                              #
# copyright (C) 2017 De2thDr, De2thDr@yandex.com, Will Breaden Madden          #
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
#                                                                              #
# CHANGELOG                                                                    #
#                                                                              #
# v0.1: Initial release                                                        #
# v0.2: Added html5lib explicit dependency.                                    #
#       Modified basicPlotMacro.C: Three instances of "char*" changed to       #
#       "const char*" as required by ISO C++11.                                #
# v0.3: Fixed exception occurring on payout - and now prints exception to      #
#       standard output too.                                                   #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help                 display help message
    --version                  display version and exit

    --addresses=TEXT           address or comma-separated addresses
    --interval=FLOAT           loop time interval (s)                            [default: 120]
    --alarm=FLOAT              alarm will activate if hashpower drops below      [default: 5900000]
    --silent                   turn off sounds
    --no_live_view             turn off live ROOT plot

    --slushtoken=TEXT          token you get from Slush's website under API
    --slushtokenfile=FILEPATH  Slush API token filepath                          [default: ~/.slushpool]
    --slushloginname=TEXT      your login name for Slush
    --slushworkername=TEXT     your worker's name at Slush

    --graphtimespan=FLOAT      the time interval (seconds) to use for the graph  [default: 86400]
    --file_CSV=FILENAME        filename for saving CSV data                      [default: SlushPool.csv]
"""

import docopt
from collections import OrderedDict
import json
import os
import requests
import sys
import time

from bs4 import BeautifulSoup
import html5lib

name    = "denarius_loop_save_SlushPool"
version = "2017-10-23T1107Z"
logo    = name

def main(options):

    addresses        =       options["--addresses"]
    interval         = float(options["--interval"])
    alarm            = float(options["--alarm"])
    silent           =       options["--silent"]
    no_live_view     =       options["--no_live_view"]
    slushtoken       =       options["--slushtoken"]
    filepath_token   =       options["--slushtokenfile"]
    slushloginname   =       options["--slushloginname"]
    slushworkername  =       options["--slushworkername"]
    graphtimespan    = float(options["--graphtimespan"])
    filename_CSV     =       options["--file_CSV"]

    filepath_token   = os.path.expanduser(os.path.expandvars(filepath_token))

    if not addresses:
        print("error -- no address specified")
        sys.exit()

    if not slushtoken:
        if os.path.isfile(filepath_token):
            file_token_contents =\
                [line.rstrip("\n") for line in open(filepath_token)]
            token = [line for line in file_token_contents if line]
            if token:
                slushtoken = token[0]
        else:
            print("error -- no Slush API token specified or found in token file. Get this from Slush's website.")
            sys.exit()

    if not slushloginname:
        print("error -- no Slush login name specified. Register at Slush's website.")
        sys.exit()

    if not slushworkername:
        print("error -- no Slush worker name specified. Register at Slush's website.")
        sys.exit()

    addresses = addresses.split(",")

    # Ensure dependencies.
    if not no_live_view:
        for program in ["root", "gv"]:
            if not which(program):
                print("error -- {program} not available".format(program = program))
                sys.exit()
    programs_sound = ["aplay", "afplay"]
    if not silent and not any([which(program) for program in programs_sound]):
        print("error -- no sound program found: " + ", ".join(programs_sound))

    #####################################################
    # Specify the variables we're interested in from Slush..
    #####################################################
    variables = OrderedDict([
        ("hashrate", "hash_rate_TH/s"),
        ("shares",     "shares")
    ])

    variablesOuter = OrderedDict([
        ("unconfirmed_reward",  "unconf_reward"),
        ("confirmed_reward",      "conf_reward")
    ])

    #####################################################
    # Define some variables to save/store values as we progress
    #####################################################
    sharesCheck=0
    totalReward=0.0
    totalRewardSave=0.0
    my_unconf_reward=0.0
    my_unconf_reward_save=0.0
    my_conf_reward=0.0
    my_conf_reward_save=0.0
    # NB: this stops the stupid InsecurePlatformWarning from SSL...
    requests.packages.urllib3.disable_warnings()
    paymentAmount=0.0
    blockfound=0
    firstLoop=1

    #####################################################
    # Begin to loop - do query and process result
    #####################################################
    while True:
        for address in addresses:
            try:
                URL         = "https://slushpool.com/accounts/profile/json/" + str(slushtoken)
                data_string = requests.get(URL, verify = False).text
                soup        = BeautifulSoup(data_string, "html5lib")
                data_JSON2  = json.loads(soup.findAll("body")[0].get_text())
                data_JSON   = data_JSON2["workers"][str(slushloginname) + "." + str(slushworkername)]

                #####################################################
                # First, and only once per GET request
                # Get a date/time in human format and also UNIX timestamp
                #####################################################
                humandate = os.system("date")
                timestamp = int(time.time())
                print("Timestamp: " + str(timestamp))

                #####################################################
                # Print the address and make it the first item in 'line'
                #####################################################
                print("\naddress: {address}".format(address = address))
                line = [address]

                #####################################################
                # Before we get the unconf_reward, save what we have
                # (could be 0) in case we found a block.
                # And set blockFound variables to 0.
                #####################################################
                my_unconf_reward_save = my_unconf_reward
                blockFound=0

                #####################################################
                # First loop over "variablesOuter" to get
                # unconf/conf rewards and add them
                #####################################################
                for variableOuter_key in list(variablesOuter.keys()):
                    # Get the value and then Print the list items found -- only those found which are also in the list "OrderedDict"!
                    valueOuter = data_JSON2[variableOuter_key]
                    if variableOuter_key == "unconfirmed_reward":
                        print("unconf_reward: " + str(valueOuter))
                        my_unconf_reward=valueOuter
                    if variableOuter_key == "confirmed_reward":
                        print("conf_reward:   " + str(valueOuter))
                        my_conf_reward=valueOuter

                totalReward=float(my_unconf_reward)+float(my_conf_reward)
                print("TOTAL REWARD:  " + str(totalReward))

                #####################################################
                # my_conf_reward can drop if there's a payout..
                #####################################################
                paymentAmount=0.0
                if float(my_conf_reward_save) > float(my_conf_reward):
                    print("PAYMENT HAS OCCURRED!")
                    paymentAmount = float(my_conf_reward_save) - float(my_conf_reward)
                    print("===========================================")
                    print("PAYMENT=" + str(paymentAmount))
                    print("===========================================")
                    print("my_conf_reward_save: " + str(my_conf_reward_save))
                    print("my_conf_reward: " + str(my_conf_reward_save))

                #####################################################
                #Save the totalReward here for use in the next iteration
                #####################################################
                my_conf_reward_save = float(my_conf_reward)

                #####################################################
                # Loop over the rest of the variables from the JSON
                #####################################################
                for variable_key in list(variables.keys()):

                    #####################################################
                    #Get the value and then Print the list items found -- only those found which are also in the list "OrderedDict"!
                    #####################################################
                    value = data_JSON[variable_key]
                    line.append(str(value))

                    #####################################################
                    # This traps a situation where there is a sharp/rapid
                    # and profound drop in hashrate...
                    #####################################################
                    if variable_key == "hashrate":
                        print("hashrate:      " + str(value))
                        if float(value) < alarm:
                            #####################################################
                            # User can add any type of alarm they like here.
                            #####################################################
                            if not silent:
                                play_sound(filename = "CarterAirRaidSiren.wav")
                            print("value < threshold CALL ALARM!")

                    if variable_key == "shares":
                        if int(value) >= sharesCheck:
                            sharesCheck=int(value)
                            print("Shares increased/stayed same... no block..."+str(sharesCheck))
                        else:
                            #####################################################
                            # User can add any type of celebration they like here.
                            #####################################################
                            if not silent:
                                play_sound(filename = "ateamhires.mp3")
                            print("SHARES HAVE REDUCED! WE HAVE A BLOCK :) ")
                            sharesCheck=int(value)
                            blockFound=1

                #####################################################
                # Store the timestamp and any rewards.
                #####################################################
                line.append(str(timestamp))
                line.append(str(my_unconf_reward))
                line.append(str(my_conf_reward))
                line.append(str(totalReward))
                line.append(str(paymentAmount))
                line.append(str(blockFound))

                #####################################################
                # Write to the .csv file.
                #####################################################
                with open(filename_CSV, "ab") as file_CSV:
                    file_CSV.write(",".join(line) + "\n")

                if not no_live_view:

                    #####################################################
                    # Run root macro in 'batch' mode (to stop focus stealing),
                    # and use -q to get the macro to exit after it runs.
                    #####################################################
                    os.system('root -l -q -b "basicPlotMacro.C(' + str(graphtimespan) + ', \\"SlushPool.csv\\")" &')

                    #####################################################
                    # Try to open the "eps" file using GhostView (gv)
                    # NB: The first time this code runs, there will be no .eps
                    # file until the root command "basicPlotMacro.C" has run.
                    # so I introduce a little 'sleep' command here to hope it
                    # will finish executing before we try to draw the result with 'gv'
                    ################a#####################################
                    if firstLoop == 1:
                        try:
                            print("Wait 5 seconds to allow root process to finish..")
                            time.sleep(5)
                            os.system('gv -watch SlushPool.eps&')
                            firstLoop=0
                        except:
                            print("Couldn't find / display .eps file..")

            #####################################################
            # Trap exceptions here
            #####################################################
            except Exception as e:
                pass
                print(e)
                #####################################################
                # User can add any type of alarm they like here.
                #####################################################
                if not silent:
                    play_sound(filename = "CarterAirRaidSiren.wav")
                print("AN EXCEPTION OCCURRED!")

        #####################################################
        # Sleep for a few seconds (interval)..
        #####################################################
        print("\nwait {interval} s".format(interval = interval))
        time.sleep(interval)

def play_sound(
    filename = None
    ):

    if which("aplay"):

        command = """
        aplay --quiet "{filename}" &
        """.format(
            filename = filename
        )

    elif which("afplay"):

        command = """
        afplay "{filename}" &
        """.format(
            filename = filename
        )

    os.system(command)

def which(
    program
    ):

    def is_exe(fpath):

        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    if fpath:

        if is_exe(program):

            return(program)

    else:

        for path in os.environ["PATH"].split(os.pathsep):

            path = path.strip('"')
            exe_file = os.path.join(path, program)

            if is_exe(exe_file):

                return exe_file

    return None

if __name__ == "__main__":
    options = docopt.docopt(__doc__)
    if options["--version"]:
        print(version)
        exit()
    main(options)

