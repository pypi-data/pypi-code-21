#!/usr/bin/python

'''
*******************************************************************************************************************************************

Copyright (C) 2017 InSilicoLynx Limited
All Rights Reserved.

This file is part of insilicolynxdqi.

The insilicolynxdqi software is covered by a BSD 3-clause license that is included in the LICENSE.txt file distributed with this software.

*******************************************************************************************************************************************
'''

'''
*******************************************************************************************************************************************

Change log

17th November 2017: First release written by Mark Wenlock.

*******************************************************************************************************************************************
'''

description = "The insilicolynxdqi.bin folder insilicolynx_perform_calculations.py script"

# Commandline parser
import argparse
import textwrap

name = "The insilicolynxdqi_perform_calculations.py script using The insilicolynxdqi Python library"
author = "InSilicoLynx Limited"
contact = "contact@insilicolynx.com"
copyrightText = "Copyright 2017 InSilicoLynx Limited"

parser = argparse.ArgumentParser(
								formatter_class = argparse.RawDescriptionHelpFormatter,
								description = str(name) + "\n\nPython script: " + description + "\n\n" + textwrap.dedent('''\
								The following optional arguments can be used with this program:
								'''),
								epilog = "Author: " + str(author) + "\n\nContact: " + str(contact) + "\n\nCopyright: " + str(copyrightText) + "\n "
								)				
# Commandline parser arguments
parser.add_argument("-df", "--dataFile", required = True, help = "REQUIRED - full file name of the tab-delimited file containing the data set.")
parser.add_argument("-sn", "--speciesName", default = "h", type = str, help = "Species: d = dog, h = human, r = rat (default = h).")
parser.add_argument("-m", "--method", default = int(1), type = int, help = "Method: 1 (po 1c total), 2 (po 1c free), 3 (po 2c total), 4 (po 2c free), 5 (iv 2c total), 6 (iv 2c free) (default = 1).")
parser.add_argument("-di", "--doseInterval", default = float(12.00), type = float, help = "Dose interval (frequency), units: hours (default = 12.00).")
parser.add_argument("-sl", "--simulationLength", default = float(168.00), type = float, help = "Simulation length, units = hours (default = 168.00).")
parser.add_argument("-c", "--compartment", default = "c", type = str, help = "Compartment to consider: c = central, p = peripheral, cp = central_peripheral or all (default = c).  (Note, not relevant for methods involving only one compartment.)")
parser.add_argument("-n", "--name", default = "name", type = str, help = "Name (of molecule) column header as it appears in the input data set (default = name).")
parser.add_argument("-uvr", "--upperVcentralToVssRatio", default = float(0.50), type = float, help = "Upper ratio for the volume of distribution in the central compartment to the volume of distribution at steady state (needs to be a number between 0.00 and less than 1.00) (default = 0.50).")
parser.add_argument("-vrl", "--vterminalToVssRatioLower", default = float(1.10), type = float, help = "Terminal volume of distribution to volume of distribution at steady state ratio lower limit (needs to be greater than or equal to 1.01) (default = 1.10).")
parser.add_argument("-vru", "--vterminalToVssRatioUpper", default = float(2.00), type = float, help = "Terminal volume of distribution to volume of distribution at steady state ratio upper limit (needs to be less than or equal to 7.00) (default = 2.00).")
parser.add_argument("-did", "--defaultIvDose", default = float(1.00), type = float, help = "Default dose to use with iv scenarios only, units: mg kg-1 (default = 1.00).")
parser.add_argument("-ad", "--absorptionDelay", default = float(-1.00), type = float, help = "Absorption delay to use with po scenarios only, units: hours (default = -1.00 (and hard coded values used: dog = 0.50; human = 1.00; rat = 0.25)).")
parser.add_argument("-itt", "--intestinalTransitTime", default = float(-1.00), type = float, help = "Intestinal transit time to use with po scenarios only, units: hours (default = -1.00 (and hard coded values used: dog = 2.00; human = 4.00; rat = 1.50)).")
parser.add_argument("-srdf", "--saveRawDataFiles", default = "yes", type = str, help = "Save raw data files: yes (default) or no.")
parser.add_argument("-bp", "--byPass", default = "no", type = str, help = "Bypass the Python version and platform check: yes or no (default).")
args = parser.parse_args()

# Main
def main(dataFile, speciesName, method, doseInterval, simulationLength, compartment, name, upperVcentralToVssRatio, vterminalToVssRatioLower, vterminalToVssRatioUpper, defaultIvDose, absorptionDelay, 
intestinalTransitTime, saveRawDataFiles, byPass):
	
	try:
		import sys
		from insilicolynxdqi.run.perform_in_vivo_calculations import PerformInVivoCalculations
		performInVivoCalculations = PerformInVivoCalculations()

		# Python version and system platform
		if byPass.lower() in ["no", "n"]: 
			systemFine = False
			if (sys.platform.startswith('linux') == True) or (sys.platform.startswith('win') == True):
				if (sys.version_info[0] == 2 and sys.version_info[1] == 7) or (sys.version_info[0] == 3):
					systemFine = True
				
			if systemFine == False:
				print("\nYour Python version: " +  str(sys.version_info) + "\nYour system platform: " +  str(sys.platform))
				print("\nThis Python script and the insilicolynxdqi Python library it uses should be compatible with Python 2.7(.z) and Python 3(.y.z) running on a Linux platform or a Win32 platform.")
				print("\nThis Python script and the insilicolynxdqi Python library have not been tested using the above Python version and system platform; it is possible that they may not work properly.")
				print("\nIf you wish to attempt running this Python script and the insilicolynxdqi Python library using the above Python version and system platform, set the commandline argument -bp to yes to by-pass this check.\n\nExiting.\n")		
				raise sys.exit(0)
				
		else:
			print("\n********** CAUTION! **********")
			print("\nYou have choosen to by-pass the Python version and system platform check - it is possible that this script may not work using your Python version and system platform!")
			print("\n******************************")

		# Perform in-vivo calculations
		performInVivoCalculations.run(
										dataFile = dataFile, speciesName = speciesName, method = method, doseInterval = doseInterval, simulationLength = simulationLength, compartment = compartment, 
										name = name, upperVcentralToVssRatio = upperVcentralToVssRatio, vterminalToVssRatioLower = vterminalToVssRatioLower, vterminalToVssRatioUpper = vterminalToVssRatioUpper, 
										defaultIvDose = defaultIvDose, absorptionDelay = absorptionDelay, intestinalTransitTime = intestinalTransitTime, saveRawDataFiles = saveRawDataFiles
										)
	
	except Exception as e:
		errorHandlerLineNumber = str(sys.exc_info()[2].tb_frame.f_lineno -2)		
		print("\n*** ERROR ***\n")
		print("Error type:\n\t" + sys.exc_info()[0].__name__)
		print("Error:\n\t" + sys.exc_info()[1].__doc__)
		print("Error description:\n\t" + str(sys.exc_info()[1]))
		print("Code object file name:\n\t" + sys.exc_info()[2].tb_frame.f_code.co_filename)
		print("Code object purpose:\n\t" + description)
		print("Code object function name:\n\t" + sys.exc_info()[2].tb_frame.f_code.co_name)
		print("Code object start line:\n\t" + str(sys.exc_info()[2].tb_frame.f_code.co_firstlineno))
		print("Code object line number where error occurred:\n\t" + str(sys.exc_info()[2].tb_lineno))
		print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
		raise sys.exit(0)		


# If this script is run from the command line then the current namespace is "__main__"" - check if "__name__"" is equal to "__main__""
if __name__ == "__main__":
	main(
			args.dataFile, args.speciesName, args.method, args.doseInterval, args.simulationLength, args.compartment, args.name, args.upperVcentralToVssRatio, args.vterminalToVssRatioLower, args.vterminalToVssRatioUpper, 
			args.defaultIvDose, args.absorptionDelay, args.intestinalTransitTime, args.saveRawDataFiles, args.byPass
			)

