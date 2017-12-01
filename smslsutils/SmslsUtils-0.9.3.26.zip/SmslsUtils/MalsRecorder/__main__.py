

from .MalsDataCollector import MalsDataCollector
from .MalsDataPlotter import MalsDataPlotter

import argparse
import sys
import datetime
import os

# setup and parse command line args
parser = argparse.ArgumentParser(prog='SmslsUtils.MalsRecorder', description='MALS Data Recorder.')
parser.add_argument('-p', '--port', dest='port', default=None, help='The serial port used by the MALS detector')
parser.add_argument('-f', '--file', dest='file', default=None, help='The CSV file (full path) in which to write the collected data (or read data from if no port is given)')
parser.add_argument('-fd', '--filedate', dest='filedate', action='store_true', help='Append date and timestamp to file name.')
parser.set_defaults(filedate=False)

args = parser.parse_args()
port = args.port 
filepath = args.file 
filedate = args.filedate

mdc = None
if port is not None:
    # if given a port number, then connect to hardware
    # if given a file path, then save data to file
    if (filepath is not None) and (filedate == True):
        filename, file_ext = os.path.splitext(filepath)
        dt = datetime.datetime.now().strftime("_%Y%m%dT%H%M%S")
        filepath = filename + dt + file_ext

    print(filepath)

    mdc = MalsDataCollector(port=port, filepath=filepath)
elif filepath is not None:
    # if not given a port number, then read and plot data from given file path
    mdc = MalsDataCollector(filepath=filepath)
else:
    # if no args are given, then print usage help and exit
    parser.print_help()
    sys.exit(1)


if mdc is not None:
    mdp = MalsDataPlotter(mdc)
    mdp.run()
