#
# This file is part of TransportMaps.
#
# TransportMaps is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TransportMaps is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with TransportMaps.  If not, see <http://www.gnu.org/licenses/>.
#
# Transport Maps Library
# Copyright (C) 2015-2017 Massachusetts Institute of Technology
# Uncertainty Quantification group
# Department of Aeronautics and Astronautics
#
# Author: Transport Map Team
# Website: transportmaps.mit.edu
# Support: transportmaps.mit.edu/qa/
#

import sys, getopt
import codecs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook

def bytespdate2num(fmt, encoding='us-ascii'):
    strconverter = mdates.strpdate2num(fmt)
    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)
    return bytesconverter

def usage():
    print('PlotExchanges.py --input-data=<fname>')

argv = sys.argv[1:]
IN_FNAME = None
try:
    opts, args = getopt.getopt(argv, "h", ["input-data="])
except getopt.GetoptError:
    usage()
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        usage()
        sys.exit()
    elif opt == '--input-data':
        IN_FNAME = arg
if None in [IN_FNAME]:
    usage()
    sys.exit(3)

with open(IN_FNAME,'r') as datafile:
    dates, exchanges, variations = \
        np.loadtxt(datafile, skiprows=2, usecols=[0,1,2], delimiter=',',
                   unpack=True, converters={0: bytespdate2num('%m/%d/%y')})

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(dates, exchanges)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
ax.set_xlabel("Day")
ax.set_ylabel("Exchange rate")
ax1 = ax.twiny()
ax1.set_xlabel("Number")
ax1.plot(exchanges,alpha=0)
fig.autofmt_xdate()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(dates,variations)
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
ax.set_xlabel("Day")
ax.set_ylabel("Variation")
ax1 = ax.twiny()
ax1.set_xlabel("Number")
ax1.plot(variations,alpha=0)
fig.autofmt_xdate()

plt.show(False)