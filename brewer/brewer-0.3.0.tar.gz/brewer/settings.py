#!/usr/bin/env python
#this file is used to store common variables for the adaptibrew configuration

port = "/dev/ttyAMA0"

# this is the address of the PID, which is controlled by the minimalmodbus lib
rimsAddress = 1

switchAddress = 2

baudRate = 19200

timeout = 0.05

#master start byte
MA0 = '55'

#master1 byte
MA1 = 'AA'

#master end byte
MAE = '77'

#hex byte for controller number
CN = '02'

# these are relay numbers on the STR116 board and should be custom for each installation
# on to boiler, off to mash
relays = {
    "hltToMash": 0,
    "hlt": 1,
    "rimsToMash": 2,
    "pump": 3
}
DEBUG = False
