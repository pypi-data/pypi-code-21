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

from __future__ import print_function

import sys
import getopt
import os
import shutil
import time
import datetime
import dill

from TransportMaps.ObjectBase import TMO

__all__ = ['Script']

class Script(TMO):

    def usage(self):
        raise NotImplementedError("To be implemented in subclasses")

    def description(self):
        raise NotImplementedError("To be implemented in subclasses")

    def full_usage(self):
        self.usage()

    def full_doc(self):
        self.full_usage()
        self.description()

    def tstamp_print(self, msg, *args, **kwargs):
        tstamp = datetime.datetime.fromtimestamp(
            time.time()
        ).strftime('%Y-%m-%d %H:%M:%S')
        print(tstamp + " " + msg, *args, **kwargs)

    def filter_tstamp_print(self, msg, *args, **kwargs):
        if self.VERBOSE:
            self.tstamp_print(msg, *args, **kwargs)

    def filter_print(self, *args, **kwargs):
        if self.VERBOSE:
            print(*args, **kwargs)

    def safe_store(self, data, fname):
        # Backup copy
        shutil.copyfile(fname, fname + '.bak')
        # Store data
        with open(fname, 'wb') as out_stream:
            dill.dump(data, out_stream);
        # Remove backup
        os.remove(fname + '.bak')

    @property
    def short_options(self):
        return "hvI"

    @property
    def long_options(self):
        return [
            # I/O
            "input=", "output=",
            # Logging
            "log=",
            # Computation
            "nprocs="
        ]

    def load_opts(self, opts):
        for opt, arg in opts:
            if opt == '-h':
                self.full_doc()
                sys.exit()

            # Verbose
            elif opt == '-v':
                self.VERBOSE = True

            # Interactive
            elif opt in ("-I"):
                self.INTERACTIVE = True

            # I/O
            elif opt in ("--input"):
                self.INPUT = arg
            elif opt in ("--output"):
                self.OUTPUT = arg

            # Logging
            elif opt in ['--log']:
                self.LOGGING_LEVEL = int(arg)

            # Computation
            elif opt in ("--nprocs"):
                self.NPROCS = int(arg)
        
    def __init__(self, argv):
        super(Script, self).__init__()

        # Options
        self.INTERACTIVE = False
        # I/O
        self.INPUT = None
        self.OUTPUT = None
        # Logging
        self.VERBOSE = False
        self.LOGGING_LEVEL = 30 # Warnings
        # Parallelization
        self.NPROCS = 1

        # Parse
        try:
            opts, args = getopt.getopt(
                argv, self.short_options, self.long_options)
        except getopt.GetoptError as e:
            self.full_usage()
            raise e

        self.load_opts(opts)

        # Check for required arguments
        if None in [self.INPUT, self.OUTPUT]:
            self.usage()
            self.tstamp_print("ERROR: Option --input and --output must be specified")
            sys.exit(3)


    def load(self):
        raise NotImplementedError("To be implemented in sub-classes")

    def run(self, mpi_pool):
        raise NotImplementedError("To be implemented in sub-classes")