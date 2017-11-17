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

description = "The insilicolynxdqi.bin folder insilicolynx_generate_scenarios.py script"

# Commandline parser
import argparse
import textwrap

name = "The insilicolynxdqi_generate_scenarios.py script using the insilicolynxdqi Python library"
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
parser.add_argument("-es", "--errorScenarios", default = int(0), type = int, help = "Number of error scenarios to consider (default = 0, can not equal 1).")
parser.add_argument("-ep", "--errorParameters", nargs = '*', help = "Enter the parameter abbreviation for error consideration (in vivo clearance (cl), volume of distribution at steady state (v), Caco2 Papp A to B at pH 6.5 (caco2), aqueous solubility at pH 7.4 (solubility) and plasma protein binding (ppb)) e.g., cl v caco2 solubility ppb.  (Note, do not add speech marks.)")
parser.add_argument("-mf", "--mappingsFile", default = "", type = str, help = "Full file path of the file containing the column header mappings for the input data set.")
parser.add_argument("-rf", "--rmsepFile", default = "", type = str, help = "Full file path of the file containing the rmsep values for the associated QSAR models.")
parser.add_argument("-qdr", "--qsarDefaultRmsep", default = float(1.00), type = float, help = "Assumed RMSEP for a QSAR model without an entry in the rmsep file.  The value reflects the RMSEP between predicted and observed values both on a logarithmic base-10 scale for cl_in_vivo_plasma_(species), v_steady_state_(species), caco2_6p5_human, solubility_7p4 and predicted and observed values both on a logarithmic base-10 percent bound over percent free scale for ppb_(species) (default = 1.00).  (Note, the species text refers to dog, human or rat.)")
parser.add_argument("-qesd", "--qsarExperimentalStandardDeviation", default = float(0.30), type = float, help = "Assumed default experimental standard deviation associated to measured data.  For cl_in_vivo_plasma_(species), v_steady_state_(species), caco2_6p5_human and solubility_7p4 this value reflects a logarithmic base-10 scale, and for ppb_(species) this value reflects a logarithmic base-10 percent bound over percent free scale (default = 0.30).  (Note, the species text refers to dog, human or rat.)")
parser.add_argument("-dpsd", "--defaultParameterStandardDeviation", default = float(0.30), type = float, help = "Assumed default parameter standard deviation to be used in the absence of a valid compound standard deviation value and/or a valid compound similarity score.  For cl_in_vivo_plasma_(species), v_steady_state_(species), caco2_6p5_human and solubility_7p4 this value reflects a logarithmic base-10 scale, and for ppb_(species) this value reflects a logarithmic base-10 percent bound over percent free scale (default = 0.30).  (Note, the species text refers to dog, human or rat.)")
parser.add_argument("-ns", "--nameSubstring", default = "_#", type = str, help = "The substring appended to the name (followed by an integer) to indicate an error scenario row (default = _#).")
parser.add_argument("-bp", "--byPass", default = "no", type = str, help = "Bypass the Python version and platform check: yes or no (default).")
args = parser.parse_args()

# Main
def main(dataFile, speciesName, method, errorScenarios, errorParameters, mappingsFile, rmsepFile, qsarDefaultRmsep, qsarExperimentalStandardDeviation, defaultParameterStandardDeviation, nameSubstring, byPass):
	
	try:
		import sys
		from insilicolynxdqi.run.generate_in_vivo_scenarios import GenerateInVivoScenarios
		generateInVivoScenarios = GenerateInVivoScenarios()

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

		# Generate in-vivo scenarios
		generateInVivoScenarios.run(
									dataFile = dataFile, speciesName = speciesName, method = method, errorScenarios = errorScenarios, errorParameters = errorParameters, mappingsFile = mappingsFile, 
									rmsepFile = rmsepFile, qsarDefaultRmsep = qsarDefaultRmsep, qsarExperimentalStandardDeviation = qsarExperimentalStandardDeviation, 
									defaultParameterStandardDeviation = defaultParameterStandardDeviation, nameSubstring = nameSubstring
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting.\n")
			raise sys.exit(0)
	

# If this script is run from the command line then the current namespace is "__main__"" - check if "__name__"" is equal to "__main__""
if __name__ == "__main__":
	main(	
			args.dataFile, args.speciesName, args.method, args.errorScenarios, args.errorParameters, args.mappingsFile, args.rmsepFile, args.qsarDefaultRmsep, args.qsarExperimentalStandardDeviation, 
			args.defaultParameterStandardDeviation, args.nameSubstring, args.byPass
			)
	
