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

description = "The insilicolynxdqi.run folder perform_in_vivo_calculations.py module"

class PerformInVivoCalculations:
	# Class variables


	# __init__
	def __init__(self):
		pass


	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi PerformInVivoCalculations class"
		
		except Exception as e:
			import sys
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


	# Run
	def run(self, **kwargs):
		try:
			import os
			import sys
			from insilicolynxdqi.system.calculation_inputs import CalculationInputs
			from insilicolynxdqi.system.csv_tools import CsvTools
			from insilicolynxdqi.system.data_folders import DataFolders	
			from insilicolynxdqi.system.file_path import FilePath
			from insilicolynxdqi.system.methods import Methods
			dataFolders = DataFolders()
			newPath = FilePath()
			methods = Methods()

			#
			# EXTRACT DATA FROM KWARGS
			#

			# Set dataFile
			if "dataFile" in kwargs:
				dataFile = kwargs["dataFile"]
			elif "df" in kwargs:
				dataFile = kwargs["df"]
			else:
				dataFile = ""

			# Set speciesName
			if "speciesName" in kwargs:
				speciesName = kwargs["speciesName"]
			elif "sn" in kwargs:
				speciesName = kwargs["sn"]
			else:
				speciesName = "h"

			# Set method
			if "method" in kwargs:
				method = kwargs["method"]
			elif "m" in kwargs:
				method = kwargs["m"]
			else:
				method = int(1)

			# Set doseInterval
			if "doseInterval" in kwargs:
				doseInterval = kwargs["doseInterval"]
			elif "di" in kwargs:
				doseInterval = kwargs["di"]
			else:
				doseInterval = float(12.00)

			# Set simulationLength
			if "simulationLength" in kwargs:
				simulationLength = kwargs["simulationLength"]
			elif "" in kwargs:
				simulationLength = kwargs["sl"]
			else:
				simulationLength = float(168.00)

			# Set compartment
			if "compartment" in kwargs:
				compartment = kwargs["compartment"]
			elif "c" in kwargs:
				compartment = kwargs["c"]
			else:
				compartment = "c"

			# Set name
			if "name" in kwargs:
				name = kwargs["name"]
			elif "n" in kwargs:
				name = kwargs["n"]
			else:
				name = "name"

			# Set upperVcentralToVssRatio
			if "upperVcentralToVssRatio" in kwargs:
				upperVcentralToVssRatio = kwargs["upperVcentralToVssRatio"]
			elif "uvr" in kwargs:
				upperVcentralToVssRatio = kwargs["uvr"]
			else:
				upperVcentralToVssRatio = float(0.50)

			# Set vterminalToVssRatioLower
			if "vterminalToVssRatioLower" in kwargs:
				vterminalToVssRatioLower = kwargs["vterminalToVssRatioLower"]
			elif "vrl" in kwargs:
				vterminalToVssRatioLower = kwargs["vrl"]
			else:
				vterminalToVssRatioLower = float(1.10)

			# Set vterminalToVssRatioUpper
			if "vterminalToVssRatioUpper" in kwargs:
				vterminalToVssRatioUpper = kwargs["vterminalToVssRatioUpper"]
			elif "vru" in kwargs:
				vterminalToVssRatioUpper = kwargs["vru"]
			else:
				vterminalToVssRatioUpper = float(2.00)

			# Set defaultIvDose
			if "defaultIvDose" in kwargs:
				defaultIvDose = kwargs["defaultIvDose"]
			elif "did" in kwargs:
				defaultIvDose = kwargs["did"]
			else:
				defaultIvDose = float(1.00)
			
			# Set absorptionDelay
			if "absorptionDelay" in kwargs:
				absorptionDelay = kwargs["absorptionDelay"]
			elif "ad" in kwargs:
				absorptionDelay = kwargs["ad"]
			else:
				absorptionDelay = float(-1.00)

			# Set intestinalTransitTime
			if "intestinalTransitTime" in kwargs:
				intestinalTransitTime = kwargs["intestinalTransitTime"]
			elif "itt" in kwargs:
				intestinalTransitTime = kwargs["itt"]
			else:
				intestinalTransitTime = float(-1.00)
			
			# Set saveRawDataFiles
			if "saveRawDataFiles" in kwargs:
				saveRawDataFiles = kwargs["saveRawDataFiles"]
			elif "srdf" in kwargs:
				saveRawDataFiles = kwargs["srdf"]
			else:
				saveRawDataFiles = "yes"
				
			#
			# CHECK AND/OR GENERATE THE PREREQUISITE INPUT DATA
			#
		
			# Dictionary of settings
			settings = {}

			# DataFile
			if not os.path.isfile(dataFile):
				import sys
				print("\nThe file " + dataFile + " does not exist. Please select a valid file.\nExiting.\n")
				raise sys.exit(0)
			else:
				settings.update({"dataFile":dataFile})
			
			# Species
			speciesName = str.lower(speciesName)
			if speciesName not in ["d", "dog", "h", "human", "r", "rat"]:
				import sys
				print("\nPlease enter d, h, or r with respect to the speciesName of interest.\nExiting.\n")
				raise sys.exit(0)
			else:
				if speciesName in ["d"]:
					speciesName = "dog"
				if speciesName in ["h"]:
					speciesName = "human"
				if speciesName in ["r"]:
					speciesName = "rat"
			settings.update({"speciesName":speciesName})	
			
			# Method	
			if method not in [1, 2, 3, 4, 5, 6]:
				import sys
				print("\nPlease enter an integer between 1 and 6 for the approximation method of interest.\nExiting.\n")
				raise sys.exit(0)
			else:
				settings.update({"method":method})
				if method == 1:
					methodName = "po_1c_total"	# Lower case
					settings.update({"compartment":"1CTotal"})
				elif method == 2:
					methodName = "po_1c_free"	# Lower case
					settings.update({"compartment":"1CFree"})
				elif method == 3:
					methodName = "po_2c_total"	# Lower case
					settings.update({"compartment":"2CTotal"})
				elif method == 4:
					methodName = "po_2c_free"	# Lower case
					settings.update({"compartment":"2CFree"})				
				elif method == 5:
					methodName = "iv_2c_total"	# Lower case
					settings.update({"compartment":"2CTotal"})
				elif method == 6:
					methodName = "iv_2c_free"	# Lower case
					settings.update({"compartment":"2CFree"})								
				settings.update({"methodName":methodName + "_" + settings["speciesName"]})

				if method in [1, 2, 3, 4]:
					settings.update({"ivOrPo":"po"})
				elif method in [5, 6]:
					settings.update({"ivOrPo":"iv"})

				if method in [1, 3, 5]:
					settings.update({"levels":"total"})
				elif method in [2, 4, 6]:
					settings.update({"levels":"free"})
					
				if method in [1, 2]:
					settings.update({"model":"1c"})
				elif method in [3, 4, 5, 6]:
					settings.update({"model":"2c"})
			
			# DoseInterval
			settings.update({"doseInterval":doseInterval})
		
			# Simulation length
			settings.update({"simulationLength":simulationLength})
			
			# Compartment
			if settings["model"] == "1c":
				settings.update({"compartment":"plasma"})	
			elif settings["model"] == "2c":
				compartmentData = str.lower(compartment)
				if compartment not in ["c", "p", "cp", "all"]:
					import sys
					print("\nPlease enter c, p, cp or all with respect to the compartment of interest to report.\nExiting.\n")
					raise sys.exit(0)
				else:
					if compartment in ["c"]:
						compartment = "central"
					if compartment in ["p"]:
						compartment = "peripheral"
					if compartment in ["cp"]:
						compartment = "central_peripheral"
					settings.update({"compartment":compartment})	

			# Name
			settings.update({"name":name})

			# UpperVcentralToVssRatio
			# 
			# Upper ratio for the volume of distribution in the central compartment to the volume of distribution at steady state
			#
			# Note, in all cases Vcentral < Vss, check that the ratio falls between 0 and less than 1. Based upon empirical observations, a value of 0.5 seems reasonable.
			#
			if 0 <= upperVcentralToVssRatio < 1:
				settings.update({"upperVcentralToVssRatio":upperVcentralToVssRatio})
			else:
				import sys
				print("\nFor the upperVcentralToVssRatio parameter, please enter an number between 0 and 1.\nExiting.\n")
				raise sys.exit(0)	
	
			# VterminalToVssRatioLower and vterminalToVssRatioUpper
			#
			# Terminal volume of distribution to volume of distribution at steady state ratios (lower and upper)
			#
			# Note, in all cases Vss < Vterminal. Hence the lower ratio is limited to 1.01 and the upper ratio is limited to 7.00. Based upon empirical observations, a lower ratio of 1.01 and an upper ratio of 2.00 seem reasonable.
			#
			if 1.01 <= vterminalToVssRatioLower:
				settings.update({"vterminalToVssRatioLower":vterminalToVssRatioLower})
			else:
				import sys
				print("\nFor the vterminalToVssRatioLower parameter, please enter an number greater than or equal to 1.01.\nExiting.\n")
				raise sys.exit(0)	
			if vterminalToVssRatioLower >= vterminalToVssRatioUpper:
				import sys
				print("\nThe terminal volume of distribution to volume of distribution at steady state ratio upper limit must be greater than the terminal volume of distribution to volume of distribution at steady state ratio lower limit.\nExiting.\n")
				raise sys.exit(0)
			if vterminalToVssRatioUpper <= 7.00:
				settings.update({"vterminalToVssRatioUpper":vterminalToVssRatioUpper})
			else:
				import sys
				print("\nFor the vterminalToVssRatioUpper parameter, please enter an number less than or equal to 7.00.\nExiting.\n")
				raise sys.exit(0)
				
			# DefaultIvDose: default dose (mg kg-1) to use with iv scenarios only
			settings.update({"defaultIvDose":defaultIvDose})

			# AbsorptionDelay: to use with po scenarios only
			if absorptionDelay == -1.00:
				settings.update({"dogAbsorptionDelay":30})	# min
				settings.update({"humanAbsorptionDelay":60})	# min
				settings.update({"ratAbsorptionDelay":15})	# min
			else:
				settings.update({"dogAbsorptionDelay":absorptionDelay * 60})	# min
				settings.update({"humanAbsorptionDelay":absorptionDelay * 60})	# min
				settings.update({"ratAbsorptionDelay":absorptionDelay * 60})	# min

			# IntestinalTransitTime: to use with po scenarios only
			if intestinalTransitTime == -1.00:
				settings.update({"dogIntestinalTransitTime":120})	# min
				settings.update({"humanIntestinalTransitTime":240})	# min
				settings.update({"ratIntestinalTransitTime":90})	# min		
			else:
				settings.update({"dogIntestinalTransitTime":intestinalTransitTime * 60})	# min
				settings.update({"humanIntestinalTransitTime":intestinalTransitTime * 60})	# min
				settings.update({"ratIntestinalTransitTime":intestinalTransitTime * 60})	# min
		
			# SaveRawDataFiles
			saveRawDataFiles = str.lower(saveRawDataFiles)
			if saveRawDataFiles not in ["y", "yes", "n", "no"]:
				print("\nPlease enter yes or no with respect to whether you want to save raw data files.\nExiting.\n")
				sys.exit()
			else:
				if saveRawDataFiles in ["y"]:
					saveRawDataFiles = "yes"
				if saveRawDataFiles in ["n"]:
					saveRawDataFiles = "no"
				settings.update({"saveRawDataFiles":saveRawDataFiles})
			
			#
			# DETERMINE OTHER VARIABLES
			#

			#
			# Folder and file section
			#
			
			# Directories and files
			settings.update({"folderName1":"simulations"}) 		
			settings.update({"folderName2":"raw"}) 
			settings.update({"folderName3":"amount"}) 
			settings.update({"folderName4":"concentration"})
			settings.update({"folderName5":"auc"})
			settings.update({"summaryFileName":"summary"}) 		
			settings.update({"textExtension":".txt"})					
			settings.update({"mainFolderText":settings["folderName1"]})
			settings.update({"subFolderText1":settings["mainFolderText"] + os.sep + settings["speciesName"]})
			settings.update({"subSubFolderText1":settings["subFolderText1"] + os.sep + settings["methodName"]})
			settings.update({"subSubSubFolderText1":settings["subSubFolderText1"] + os.sep + settings["folderName2"]})
			settings.update({"subSubSubFolderText2":settings["subSubFolderText1"] + os.sep + settings["folderName3"]})
			settings.update({"subSubSubFolderText3":settings["subSubFolderText1"] + os.sep + settings["folderName4"]})
			settings.update({"subSubSubFolderText4":settings["subSubFolderText1"] + os.sep + settings["folderName5"]})
			
			#
			# PK parameter section
			#

			# Absorption amplification factor
			if settings["ivOrPo"] == "po":
				settings.update({"dogAbsorptionAmplificationFactor":2})
				settings.update({"humanAbsorptionAmplificationFactor":2})
				settings.update({"ratAbsorptionAmplificationFactor":2})

			# AUC integration	
			settings.update({"numberOfSegments":100})

			# Body weight
			#
			# Reference for species body weight:
			#		Y. Kwon, in Handbook of Essential Pharmacokinetics, Pharmacodynamics, and Drug Metabolism for Industrial Scientists, Kluwer Academic / Plenum Publishers, New York, 2001, pp. 230.
			# 
			settings.update({"dogBodyWeight":10})	# kg
			settings.update({"humanBodyWeight":70})	# kg
			settings.update({"ratBodyWeight":0.33})	# kg
			settings.update({"bodyWeightSuffix":"BodyWeight"})
	
			# Charge types
			if settings["ivOrPo"] == "po":
				settings.update({"diAcidText":"diacid"})
				settings.update({"diBaseText":"dibase"})
				settings.update({"monoAcidText":"monoacid"})
				settings.update({"monoBaseText":"monobase"})
				settings.update({"neutralText":"neutral"})
				settings.update({"zwitterionText":"zwitterion"})
				
			# Dose
			if settings["ivOrPo"] == "iv":
				settings.update({"dose":[float(settings["defaultIvDose"]) * float(settings[settings["speciesName"] + settings["bodyWeightSuffix"]])]})	
			elif settings["ivOrPo"] == "po":
				settings.update({"doses":[0.000001, 0.000005, 0.00001, 0.00005, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 25.0, 50.0, 75.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0, 10000.0]}) # Doses are total amounts in mg and must be in ascending order

			# First pass hepatic clearance fraction (i.e., Fh)
			if settings["ivOrPo"] == "po":
				settings.update({"firstPassHepaticClearanceFractionLimit":0.02})

			# Hepatic blood flow	
			if settings["ivOrPo"] == "po":
				settings.update({"dogHepaticBloodFlow":309})	# mL min-1
				settings.update({"humanHepaticBloodFlow":1450})	# mL min-1
				settings.update({"ratHepaticBloodFlow":13.8})	# mL min-1
			
			# Intestinal fluid volume - small intestine	
			if settings["ivOrPo"] == "po":
				settings.update({"dogIntestinalFluidVolume":20})	# mL
				settings.update({"humanIntestinalFluidVolume":80})	# mL
				settings.update({"ratIntestinalFluidVolume":5})	# mL
			
			# Permeability
			if settings["ivOrPo"] == "po":
				settings.update({"pablCaco2Ph6P5":0.000247})	# cm s-1
				settings.update({"caco2Ph6P5ToPablCaco2Ph6P5Ratio":0.99})
				settings.update({"pmSlope":0.916})
				settings.update({"pmIntercept":1.579})	
				settings.update({"pablPeffPh6P5":0.000835})	# cm s-1
				settings.update({"peffPh6P5MaxValue":0.001})

			# Plasma volume
			#
			# Human plasma volume is assumed to be 3 L; plasma volume for dog and rat are based upon this human plasma volume scaled for body weight.
			#
			settings.update({"humanPlasmaVolume":3.000})	# L
			settings.update({"dogPlasmaVolume":(float(settings["dogBodyWeight"]) / float(settings["humanBodyWeight"])) * float(settings["humanPlasmaVolume"])})	# L
			settings.update({"ratPlasmaVolume":(float(settings["ratBodyWeight"]) / float(settings["humanBodyWeight"])) * float(settings["humanPlasmaVolume"])})	# L
			settings.update({"plasmaVolumeSuffix":"PlasmaVolume"})	

			# Radius - small intestine
			if settings["ivOrPo"] == "po":
				settings.update({"dogIntestinalRadius":0.25})	# cm
				settings.update({"humanIntestinalRadius":1.25})	# cm
				settings.update({"ratIntestinalRadius":0.10})	# cm	

			# Time intervals
			settings.update({"timeInterval":15}) # min
					
			# Units 
			settings.update({"hUnitsText":"h"})			
			settings.update({"lKgMinus1UnitsText":"L kg-1"})
			settings.update({"lMinMinus1UnitsText":"L min-1"})
			settings.update({"lUnitsText":"L"})
			settings.update({"mgUnitsText":"mg"})
			settings.update({"minUnitsText":"min"})
			settings.update({"mLMinMinus1KgMinus1UnitsText":"mL min-1 kg-1"})	
			settings.update({"sMinus1UnitsText":"s-1"})
			settings.update({"sUnitsText":"s"})
			
			# Units: level specific
			if settings["levels"] == "free":
				settings.update({"percentBoundUnitsText":"% bound"})
				settings.update({"percentFreeUnitsText":"% free"})
			
			# Units: ivOrPo specific
			if settings["ivOrPo"] == "po":
				settings.update({"cmSMinus1UnitsText":"cm s-1"})
				settings.update({"mUnitsText":"m"})
				settings.update({"naUnitsText":"na"})
			
			#
			# Text section
			#

			# CSV column headers
			settings.update({"csvFileColumnHeaderAmountText":"amount (mg)"})
			settings.update({"csvFileColumnHeaderDoseText":"dose (mg)"})
			settings.update({"csvFileColumnHeaderLog10Text":"log10"})
			settings.update({"csvFileColumnHeaderRawParameterText":"parameter"})
			settings.update({"csvFileColumnHeaderRawParameterValueText":"value"})
			settings.update({"csvFileColumnHeaderTimeText":"time (minute)"})			

			# CSV column headers: model specific 
			if settings["model"] == "1c":
				settings.update({"csvFileColumnHeaderAucAmountBText1":"auc amount plasma"})
				settings.update({"csvFileColumnHeaderAucConcentrationBText1":"auc concentration plasma"})	
				settings.update({"csvFileColumnHeaderConcentrationText":"plasma concentration (mg l-1)"})
				settings.update({"csvFileColumnHeaderMaxAmountText1":"max plasma amount (mg)"})
				settings.update({"csvFileColumnHeaderMaxConcentrationText1":"max plasma concentration (mg l-1)"})
				settings.update({"csvFileColumnHeaderMaxToMinRatioText1":"max/min plasma ratio"})
				settings.update({"csvFileColumnHeaderMidAmountText1":"mid plasma amount (mg)"})
				settings.update({"csvFileColumnHeaderMidConcentrationText1":"mid plasma concentration (mg l-1)"})
				settings.update({"csvFileColumnHeaderMinAmountText1":"min plasma amount (mg)"})			
				settings.update({"csvFileColumnHeaderMinConcentrationText1":"min plasma concentration (mg l-1)"})			
			elif settings["model"] == "2c":
				settings.update({"csvFileColumnHeaderAmountCentralText":"amount (central) (mg)"})
				settings.update({"csvFileColumnHeaderAmountPeripheralText":"amount (peripheral) (mg)"})
				settings.update({"csvFileColumnHeaderAucAmountBText1":"auc amount central"})
				settings.update({"csvFileColumnHeaderAucAmountBCText1":"auc amount central and peripheral"})
				settings.update({"csvFileColumnHeaderAucAmountCText1":"auc amount peripheral"})
				settings.update({"csvFileColumnHeaderAucConcentrationBText1":"auc concentration central"})		
				settings.update({"csvFileColumnHeaderConcentrationText":"central concentration (mg l-1)"})
				settings.update({"csvFileColumnHeaderMaxAmountText1":"max central amount (mg)"})
				settings.update({"csvFileColumnHeaderMaxAmountText2":"max peripheral amount (mg)"})
				settings.update({"csvFileColumnHeaderMaxAmountText3":"max central and peripheral amount (mg)"})
				settings.update({"csvFileColumnHeaderMaxConcentrationText1":"max central concentration (mg l-1)"})			
				settings.update({"csvFileColumnHeaderMaxToMinRatioText1":"max/min central ratio"})			
				settings.update({"csvFileColumnHeaderMaxToMinRatioText2":"max/min peripheral ratio"})	
				settings.update({"csvFileColumnHeaderMaxToMinRatioText3":"max/min central and peripheral ratio"})			
				settings.update({"csvFileColumnHeaderMidAmountText1":"mid central amount (mg)"})
				settings.update({"csvFileColumnHeaderMidAmountText2":"mid peripheral amount (mg)"})		
				settings.update({"csvFileColumnHeaderMidAmountText3":"mid central and peripheral amount (mg)"})
				settings.update({"csvFileColumnHeaderMidConcentrationText1":"mid central concentration (mg l-1)"})				
				settings.update({"csvFileColumnHeaderMinAmountText1":"min central amount (mg)"})
				settings.update({"csvFileColumnHeaderMinAmountText2":"min peripheral amount (mg)"})			
				settings.update({"csvFileColumnHeaderMinAmountText3":"min central and peripheral amount (mg)"})
				settings.update({"csvFileColumnHeaderMinConcentrationText1":"min central concentration (mg l-1)"})		

			# Text values
			settings.update({"clearanceText":"clearance_"})
			settings.update({"clText":"cl_in_vivo_plasma_"})
			settings.update({"columnHeaderSuffix":"scenario"})				
			settings.update({"doseIntervalText":"dose_interval_"})
			settings.update({"doseText":"dose_"})
			settings.update({"eliminationRateConstantText":"elimination_rate_constant_"})
			settings.update({"molecularWeightText":"mol_wt"})
			settings.update({"qualifierSuffix":"_qualifier"})
			settings.update({"quantityAucText":"auc_"})	
			settings.update({"quantityMaxText":"max_"})
			settings.update({"quantityMidText":"mid_"})
			settings.update({"quantityMinText":"min_"})
			settings.update({"simulationLengthText":"simulation_length_"})	
			settings.update({"unitsSuffix":"_units"})
			settings.update({"vssText":"v_steady_state_"})
			
			# Text values: level specific 
			if settings["levels"] == "free":
				settings.update({"ppbText":"ppb_"})
			
			# Text values: ivOrPo specific 
			if settings["ivOrPo"] == "po":
				settings.update({"absorptionAmplificationFactorSuffix": "AbsorptionAmplificationFactor"})
				settings.update({"absorptionDelaySuffix": "AbsorptionDelay"})
				settings.update({"absorptionDelayText":"absorption_delay_"})
				settings.update({"absorptionRateConstantCalculationMethodText":"caco2_6p5_human"})
				settings.update({"absorptionRateConstantText":"absorption_rate_constant_"})	
				settings.update({"absorptionSaturationConditionText":"absorption_saturation_condition_"})	
				settings.update({"absorptionSaturatedTimeText":"absorption_saturated_time_"})	
				settings.update({"amountTransferredToBodyUnderSaturatedConditionsText":"amount_transferred_to_body_under_saturated_conditions_"})	
				settings.update({"amountTransferredToBodyUnderAbsorptionConditionsText":"amount_transferred_to_body_under_absorption_conditions_"})
				settings.update({"amountTransferredToCentralCompartmentUnderSaturatedConditionsText":"amount_transferred_to_central_compartment_under_saturated_conditions_"})	
				settings.update({"amountTransferredToCentralCompartmentUnderAbsorptionConditionsText":"amount_transferred_to_central_compartment_under_absorption_conditions_"})
				settings.update({"amountTransferredToPeripheralCompartmentUnderSaturatedConditionsText":"amount_transferred_to_peripheral_compartment_under_saturated_conditions_"})	
				settings.update({"amountTransferredToPeripheralCompartmentUnderAbsorptionConditionsText":"amount_transferred_to_peripheral_compartment_under_absorption_conditions_"})
				settings.update({"caco26P5HumanText":"caco2_6p5_human"})
				settings.update({"chargeTypeText":"charge_type"})
				settings.update({"defaultCalculationMethodText":"default"})
				settings.update({"doseAucText":"dose_auc_"})		
				settings.update({"doseMaxText":"dose_max_"})
				settings.update({"doseMidText":"dose_mid_"})
				settings.update({"doseMinText":"dose_min_"})					
				settings.update({"firstPassFractionHepaticMetabolisedText":"first_pass_fraction_hepatic_metabolised_"})
				settings.update({"fractionNeutral6P5Text":"fraction_neutral_6p5"})
				settings.update({"fractionNeutral7P4Text":"fraction_neutral_7p4"})	
				settings.update({"hepaticBloodFlowSuffix":"HepaticBloodFlow"})
				settings.update({"highestLinearDoseAucText":"highest_linear_dose_auc_"})
				settings.update({"highestLinearDoseMaxText":"highest_linear_dose_max_"})
				settings.update({"highestLinearDoseMidText":"highest_linear_dose_mid_"})
				settings.update({"highestLinearDoseMinText":"highest_linear_dose_min_"})
				settings.update({"interceptAucText":"intercept_auc_"})
				settings.update({"interceptMaxText":"intercept_max_"})
				settings.update({"interceptMidText":"intercept_mid_"})
				settings.update({"interceptMinText":"intercept_min_"})
				settings.update({"intestinalFluidVolumeSuffix":"IntestinalFluidVolume"})
				settings.update({"intestinalRadiusSuffix":"IntestinalRadius"})
				settings.update({"intestinalTransitTimeSuffix":"IntestinalTransitTime"})
				settings.update({"intestinalTransitTimeText":"intestinal_transit_time_"})		
				settings.update({"intrinsicSolubilityText":"intrinsic_solubility"})
				settings.update({"lowestFlatRegionDoseAucText":"lowest_flat_region_dose_auc_"})	
				settings.update({"lowestFlatRegionDoseMaxText":"lowest_flat_region_dose_max_"})
				settings.update({"lowestFlatRegionDoseMidText":"lowest_flat_region_dose_mid_"})
				settings.update({"lowestFlatRegionDoseMinText":"lowest_flat_region_dose_min_"})	
				settings.update({"pKaA1Text":"pka_a1"})
				settings.update({"pKaB1Text":"pka_b1"})
				settings.update({"pKaA2Text":"pka_a2"})
				settings.update({"pKaB2Text":"pka_b2"})
				settings.update({"r2AucText":"r2_auc_"})
				settings.update({"r2MaxText":"r2_max_"})	
				settings.update({"r2MidText":"r2_mid_"})	
				settings.update({"r2MinText":"r2_min_"})	
				settings.update({"slopeAucText":"slope_auc_"})
				settings.update({"slopeMaxText":"slope_max_"})
				settings.update({"slopeMidText":"slope_mid_"})
				settings.update({"slopeMinText":"slope_min_"})
				settings.update({"solubility6P5Text":"solubility_6p5"})
				settings.update({"solubility6P5saturatedText":"solubility_6p5_saturated_"})
				settings.update({"solubility7P4Text":"solubility_7p4"})	
			
			# Text values: model specific 
			if settings["model"] == "1c":
				settings.update({"amountBPrefix":"amount_plasma_"})
				settings.update({"aucAmountBPrefix":"auc_amount_plasma_"})
				settings.update({"aucConcentrationBPrefix":"auc_concentration_plasma_"})
				settings.update({"concentrationBPrefix":"concentration_plasma_"})
			elif settings["model"] == "2c":
				settings.update({"alphaText":"alpha_"})	
				settings.update({"amountBPrefix":"amount_central_"})
				settings.update({"amountBCPrefix":"amount_central_peripheral_"})
				settings.update({"amountCPrefix":"amount_peripheral_"})	
				settings.update({"aucAmountBPrefix":"auc_amount_central_"})		
				settings.update({"aucAmountBCPrefix":"auc_amount_central_peripheral_"})
				settings.update({"aucAmountCPrefix":"auc_amount_peripheral_"})
				settings.update({"aucConcentrationBPrefix":"auc_concentration_central_"})
				settings.update({"betaText":"beta_"})
				settings.update({"centralToPeripheralCompartmentRateConstantText":"central_to_peripheral_compartment_rate_constant_"})
				settings.update({"concentrationBPrefix":"concentration_central_"})
				settings.update({"peripheralToCentralCompartmentRateConstantText":"peripheral_to_central_compartment_rate_constant_"})
				settings.update({"vcentralText":"v_central_"})
				settings.update({"vterminalText":"v_terminal_"})
		
			#
			# ESTABLISH FURTHER SETTINGS
			#
			
			# Determine the calculation inputs
			calculationInputs = CalculationInputs(settings)
			calculationInputData, calculationInputDataUnits, headerParameterComparisonRemoveList, headerParameterUnitsComparisonRemoveList = calculationInputs.calculationInputData(settings["method"])
			if settings["ivOrPo"] == "po":
				calculationAdditionalParameterOrder, calculationAdditionalParameter, calculationAdditionalParameterUnits = calculationInputs.calculationAdditionalParameter(settings["method"])
			
			# Check dataFile for prerequiste data
			csvTools = CsvTools(settings)
			csvTools.compareCSVHeaders(settings, calculationInputData, headerParameterComparisonRemoveList)

			# Check dataFile for prerequiste units 
			csvTools.compareCSVHeaders(settings, calculationInputDataUnits, headerParameterUnitsComparisonRemoveList)
				
			# Create data folders
			settings = dataFolders.createDataFolders(settings)				

			# Create a copy of the input file
			settings.update({"dataFileOriginal":newPath.setPath(dataFile, 'file', "_original")})
			settings.update({"dataFileNew":newPath.setPath(dataFile, 'file', "_" + settings["methodName"])})
			
			# Calculate any additional parameters
			if settings["ivOrPo"] == "po":
				methods.additionalParameterCalculations(calculationAdditionalParameterOrder, calculationAdditionalParameter, calculationAdditionalParameterUnits, settings)
				
			#
			# PERFORM IN-VIVO CALCULATIONS
			#
			
			print("\nPerform in-vivo calculations for method " +  str(int(settings["method"])) +  " (" +  str(settings["methodName"]) + ").")
			methods.doseQuantityCalculations(settings)
			
			print("")
		
			# Return the dataFileNew parameter
			return settings["dataFileNew"]
		
		except Exception as e:
			import sys
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

