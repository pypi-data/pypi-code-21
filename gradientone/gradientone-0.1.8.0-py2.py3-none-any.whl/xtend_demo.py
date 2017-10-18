"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited 
without the express permission of GradientOne Inc.

"""

#!/usr/bin/env python

import time
import sys
import os
import numpy as np

from os.path import join, dirname, abspath
# TODO: change instruments to a package to avoid this nonsense
sys.path.append(join(dirname(abspath(__file__)), "device_drivers"))

from xtend import Xtend
from tek import GOMDO4104
from agilent import GOU2001A

pm = GOU2001A("USB::0x2a8d::0x2b18::INSTR")
mdo = GOMDO4104("TCPIP::192.168.1.108::INSTR")

xt = Xtend("/dev/ttyUSB0", 9600)

pm._interface.timeout = 10

# set up power meter for trace measurement
print("Setting up U2001A power sensor")
pm.utility.reset()
time.sleep(1)
# offset 13 dB coupling loss in directional coupler
pm.channels[0].offset = 13
# 902 to 928 MHz band, center is 915 MHz
pm.channels[0].correction_frequency = 915e6
# set up for trace capture
# 35 ms trace, start 1 ms before trigger
# high resolution sampling
# internal trigger rising across 0 dBm
pm.trace.state = 1
pm.trace.offset_time = -1e-3
pm.trace.time = 35e-3
pm.trigger.source = "internal"
pm.trigger.level = 0
pm.trigger.slope = "positive"

# set up MDO for time correlated spectrum measurement
print("Setting up MDO4104")
mdo.utility.reset()
time.sleep(3)
for ch in mdo.channels:
    ch.enabled = False
# module RXD
rxd_ch = mdo.channels[1]
rxd_ch.enabled = True
rxd_ch.range = 100
rxd_ch.offset = -30
# module TXD
txd_ch = mdo.channels[2]
txd_ch.enabled = True
txd_ch.range = 100
txd_ch.offset = -10
# spectrum
# offset 14 dB attenuator
mdo.rf.frequency = 915e6
mdo.rf.span = 50e6
mdo.rf.reflevel = 30
mdo.rf.scale = 10
# average power
mdo.rf.amplitude.vertical_position = -4
mdo.rf.amplitude.vertical_scale = 0.2
# horizontal
mdo.timebase.position = 30e-3
mdo.timebase.range = 100e-3
# trigger
mdo.trigger.source = rxd_ch
mdo.trigger.type = 'edge'
mdo.trigger.level = 0
mdo.trigger.slope = 'rising'
mdo.trigger.continuous = False

time.sleep(5)

# initate single-shot measurement
mdo.measurement.initiate()

time.sleep(1)

# send some RF data
print("Send RF packet")
xt.testing()


# dump power sensor data
print("Save power sensor trace")
data = pm.get_data()

if sys.byteorder == 'little':
    data.byteswap()

with open("xtend_power_trace.csv", "w") as f:
    for p in data:
        f.write("%f\n" % p)

# save MDO spectrum data
print("Wait for MDO to finish computing...")
time.sleep(25)

print("Save MDO screen")
with open("xtend_mdo_scr.png", "wb") as f:
    f.write(mdo.display.fetch_screenshot())

print("Save MDO serial rxd/txd data")
rxd_data = rxd_ch.measurement.fetch_waveform()
txd_data = txd_ch.measurement.fetch_waveform()

data = np.vstack((rxd_data.x, rxd_data.y, txd_data.y)).T
np.savetxt("xtend_mdo_rxd_txd.csv", data, '%.6e', ',')

print("Save MDO RF amplitude data")
data = mdo.channels['rf_amplitude'].measurement.fetch_waveform()

data = np.vstack((data.x, data.y)).T
np.savetxt("xtend_mdo_rf_amplitude.csv", data, '%.6e', ',')

print("Save MDO RF spectrum data")

if not os.path.exists("xtend_mdo_rf_trace"):
    os.mkdir("xtend_mdo_rf_trace")

# save 1 slice per ms
for i in range(61):
    print("%dms" % i)
    mdo.timebase.window.position = i*1e-3
    data = mdo.channels['rf_normal'].measurement.fetch_waveform()
    
    data = np.vstack((data.x, data.y)).T
    np.savetxt("xtend_mdo_rf_trace/xtend_mdo_rf_trace_%dms.csv" % i, data, '%.6e', ',')
    
    with open("xtend_mdo_rf_trace/xtend_mdo_rf_trace_%dms_scr.png" % i, "wb") as f:
        f.write(mdo.display.fetch_screenshot())


