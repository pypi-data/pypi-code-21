

from .MalsDataCollector import MalsDataCollector
from .MalsDataPlotter import MalsDataPlotter

import argparse

# setup and parse command line args
parser = argparse.ArgumentParser(description='MALS Data Recorder.')
parser.add_argument('-p', '--port', dest='port', default=None, help='The serial port used by the MALS detector')
parser.add_argument('-f', '--file', dest='file', default=None, help='The CSV file (full path) in which to write the collected data (or read data from if no port is given)')

args = parser.parse_args()
port = args.port 
filepath = args.file 


mdc = None
if port is not None:
	# if given a port number, then connect to hardware
	# if given a file path, then save data to file
    mdc = MalsDataCollector(port=port, filepath=filepath)
elif filepath is not None:
	# if not given a port number, then read and plot data from given file path
    mdc = MalsDataCollector(filepath=filepath)

if mdc is not None:
	mdp = MalsDataPlotter(mdc)
	mdp.run()
