#!/usr/bin/env python

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
import numpy as np
import logging

import TransportMaps.Distributions.Examples.BiochemicalOxigenDemand as BOD

def usage():
    str_usage = """
DataGeneration.py --output=FNAME
  [--numy=N --timey=N --sigma=N]
    """
    print(str_usage)

def full_usage():
    usage()

argv = sys.argv[1:]
numy = 0
timey = 0.
sigma = np.sqrt(1e-3)
OUT_FNAME = None
try:
    opts, args = getopt.getopt(argv,"h", [
        "output=",
        "numy=", "timey=", "sigma="])
except getopt.GetoptError:
    full_usage()
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        full_usage()
        sys.exit()
    elif opt in ("--output"):
        OUT_FNAME = arg
    elif opt in ("--numy"):
        numy = int(arg)
    elif opt in ("--timey"):
        timey = float(arg)
    elif opt in ("--sigma"):
        sigma = float(arg)
if None in [OUT_FNAME]:
    logging.warn("The density won't be stored")
    
d = BOD.BODjoint(numy, timey, sigma)

if OUT_FNAME is not None:
    d.store(OUT_FNAME)

#####
# PLOTTING
import TransportMaps.Diagnostics as DIAG
DIAG.plotAlignedConditionals(d, range_vec=[-5,5])