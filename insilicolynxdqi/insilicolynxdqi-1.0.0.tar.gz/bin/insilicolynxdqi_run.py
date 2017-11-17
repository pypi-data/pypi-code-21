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

description = "The insilicolynxdqi.bin folder insilicolynx_run.py script"

# Commandline parser
import argparse
import textwrap

name = "The insilicolynxdqi_run.py script using the insilicolynxdqi Python library"
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
parser.add_argument("-ro", "--removeOutliers", default = int(0), type = int, help = "If the number of available records permits, the number of outliers to remove - to use with po scenarios only.")
parser.add_argument("-ild", "--intervalLevelDistribution", default = float(80.00), type = float, help = "If the number of available records permits, the (approximate) two-sided distribution interval level to calculate - accepted range : 70.00 percent to 100.00 percent (default = 80.00 percent).")
parser.add_argument("-cml", "--confidenceMeanLevel", default = float(80.00), type = float, help = "If the number of available records permits, the (approximate) two-sided confidence interval of the mean level to calculate - accepted range : 70.00 percent to 99.90 percent (default = 80.00 percent).  (Note, a minimum of four records is required to calculate the confidence intervals of the mean; and where the degrees of freedom is greater than 150 the t-critical value is calculated for 150 degrees of freedom.)")
parser.add_argument("-s", "--smiles", default = "smiles", type = str, help = "If applicable, smiles column header as it appears in the input data set (default = smiles).")
parser.add_argument("-bp", "--byPass", default = "no", type = str, help = "Bypass the Python version and platform check: yes or no (default).")
args = parser.parse_args()

# Main
def main(dataFile, speciesName, method, errorScenarios, errorParameters, mappingsFile, rmsepFile, qsarDefaultRmsep, qsarExperimentalStandardDeviation, defaultParameterStandardDeviation, nameSubstring, doseInterval, 
simulationLength, compartment, name, upperVcentralToVssRatio, vterminalToVssRatioLower, vterminalToVssRatioUpper, defaultIvDose, absorptionDelay, intestinalTransitTime, saveRawDataFiles, removeOutliers, 
intervalLevelDistribution, confidenceMeanLevel, smiles, byPass):
	
	try:
		import sys
		from insilicolynxdqi.run.generate_in_vivo_scenarios import GenerateInVivoScenarios
		from insilicolynxdqi.run.perform_in_vivo_calculations import PerformInVivoCalculations
		from insilicolynxdqi.run.analyse_in_vivo_calculations import AnalyseInVivoCalculations
		generateInVivoScenarios = GenerateInVivoScenarios()
		performInVivoCalculations = PerformInVivoCalculations()
		analyseInVivoCalculations = AnalyseInVivoCalculations()

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
		dataFileNew = generateInVivoScenarios.run(
													dataFile = dataFile, speciesName = speciesName, method = method, errorScenarios = errorScenarios, errorParameters = errorParameters, mappingsFile = mappingsFile, 
													rmsepFile = rmsepFile, qsarDefaultRmsep = qsarDefaultRmsep, qsarExperimentalStandardDeviation = qsarExperimentalStandardDeviation, 
													defaultParameterStandardDeviation = defaultParameterStandardDeviation, nameSubstring = nameSubstring
													)
		
		# Perform in-vivo calculations
		dataFileNew = performInVivoCalculations.run(
													dataFile = dataFileNew, speciesName = speciesName, method = method, doseInterval = doseInterval, simulationLength = simulationLength, compartment = compartment, 
													name = name, upperVcentralToVssRatio = upperVcentralToVssRatio, vterminalToVssRatioLower = vterminalToVssRatioLower, vterminalToVssRatioUpper = vterminalToVssRatioUpper, 
													defaultIvDose = defaultIvDose, absorptionDelay = absorptionDelay, intestinalTransitTime = intestinalTransitTime, saveRawDataFiles = saveRawDataFiles
													)
				
		# Analyse in-vivo calculations
		analyseInVivoCalculations.run(
										dataFile = dataFileNew, speciesName = speciesName, method = method, nameSubstring = nameSubstring, compartment = compartment, removeOutliers = removeOutliers, 
										intervalLevelDistribution = intervalLevelDistribution, confidenceMeanLevel = confidenceMeanLevel, smiles = smiles
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
			args.defaultParameterStandardDeviation, args.nameSubstring, args.doseInterval, args.simulationLength, args.compartment, args.name, args.upperVcentralToVssRatio, args.vterminalToVssRatioLower, 
			args.vterminalToVssRatioUpper, args.defaultIvDose, args.absorptionDelay, args.intestinalTransitTime, args.saveRawDataFiles, args.removeOutliers, args.intervalLevelDistribution, args.confidenceMeanLevel, 
			args.smiles, args.byPass
			)

