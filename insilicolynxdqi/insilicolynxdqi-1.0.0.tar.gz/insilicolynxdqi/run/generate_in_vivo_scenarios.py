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

description = "The insilicolynxdqi.run folder generate_in_vivo_scenarios.py module"

class GenerateInVivoScenarios:
	# Class variables


	# __init__
	def __init__(self):
		pass


	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi GenerateInVivoScenarios class"
		
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
			import types
			from insilicolynxdqi.system.csv_tools import CsvTools

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

			# Set errorScenarios
			if "errorScenarios" in kwargs:
				errorScenarios = kwargs["errorScenarios"]
			elif "es" in kwargs:
				errorScenarios = kwargs["es"]
			else:
				errorScenarios = int(0)

			# Set errorParameters
			if "errorParameters" in kwargs:
				errorParameters = kwargs["errorParameters"]
			elif "ep" in kwargs:
				errorParameters = kwargs["ep"]
			else:
				errorParameters = ""

			# Set mappingsFile
			if "mappingsFile" in kwargs:
				mappingsFile = kwargs["mappingsFile"]
			elif "mf" in kwargs:
				mappingsFile = kwargs["mf"]
			else:
				mappingsFile = ""

			# Set rmsepFile
			if "rmsepFile" in kwargs:
				rmsepFile = kwargs["rmsepFile"]
			elif "rf" in kwargs:
				rmsepFile = kwargs["ef"]
			else:
				rmsepFile = ""
				 
			# Set qsarDefaultRmsep
			if "qsarDefaultRmsep" in kwargs:
				qsarDefaultRmsep = kwargs["qsarDefaultRmsep"]
			elif "qdr" in kwargs:
				qsarDefaultRmsep = kwargs["qdr"]
			else:
				qsarDefaultRmsep = float(1.00)

			# Set qsarExperimentalStandardDeviation
			if "qsarExperimentalStandardDeviation" in kwargs:
				qsarExperimentalStandardDeviation = kwargs["qsarExperimentalStandardDeviation"]
			elif "qesd" in kwargs:
				qsarExperimentalStandardDeviation = kwargs["qesd"]
			else:
				qsarExperimentalStandardDeviation = float(0.30)

			# Set defaultParameterStandardDeviation
			if "defaultParameterStandardDeviation" in kwargs:
				defaultParameterStandardDeviation = kwargs["defaultParameterStandardDeviation"]
			elif "dpsd" in kwargs:
				defaultParameterStandardDeviation = kwargs["dpsd"]
			else:
				defaultParameterStandardDeviation = float(0.30)

			# Set nameSubstring
			if "nameSubstring" in kwargs:
				nameSubstring = kwargs["nameSubstring"]
			elif "ns" in kwargs:
				nameSubstring = kwargs["ns"]
			else:
				nameSubstring = "_#"
				
			#
			# CHECK AND/OR GENERATE THE PREREQUISITE INPUT DATA
			#
			
			# Dictionary of settings
			settings = {}

			# DataFile
			if not os.path.isfile(dataFile):
				print("\nThe file " + dataFile + " does not exist. Please select a valid file.\nExiting.\n")
				raise sys.exit(0)
			else:
				settings.update({"dataFile":dataFile})
	
				# Set file path for temp and new file
				inputFileDirectory = os.path.dirname(settings["dataFile"])
				base = os.path.splitext(os.path.basename(settings["dataFile"]))[0]
				extension = os.path.splitext(os.path.basename(settings["dataFile"]))[1]
				if inputFileDirectory != "":
					settings.update({"dataFileTemp":inputFileDirectory + os.sep + base + "_temp" + extension})
					settings.update({"dataFileNew":inputFileDirectory + os.sep + base + "_revised" + extension})
				else:
					settings.update({"dataFileTemp":base + "_temp" + extension})
					settings.update({"dataFileNew":base + "_revised" + extension})
				
			# Species
			speciesName = str.lower(speciesName)
			if speciesName not in ["d", "dog", "h", "human", "r", "rat"]:
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
				if method in [1, 2, 3, 4]:
					settings.update({"ivOrPo":"po"})
				elif method in [5, 6]:
					settings.update({"ivOrPo":"iv"})

				if method in [1, 3, 5]:
					settings.update({"levels":"total"})
				elif method in [2, 4, 6]:
					settings.update({"levels":"free"})
			
			# ErrorScenarios
			if errorScenarios == int(0) or errorScenarios >= 2:
				settings.update({"errorScenarios":errorScenarios})
			else:
				print("\nThe number of error scenarios can not be set to 1. Please enter either 0 or a number greater than or equal to 2.\nExiting.\n")
				raise sys.exit(0)
			
			# ErrorParameters
			if type(errorParameters) is str:
				errorParameters = errorParameters.split(" ")

			# MappingsFile
			if mappingsFile != "":
				if not os.path.isfile(mappingsFile):
					print("\nThe mappings file " + mappingsFile + " does not exist. Please select a valid file.\nExiting.\n")
					raise sys.exit(0)
			settings.update({"mappingsFile":mappingsFile})
			
			# RmsepFile
			if rmsepFile != "":
				if not os.path.isfile(rmsepFile):
					print("\nThe rmsep file " + rmsepFile + " does not exist. Please select a valid file.\nExiting.\n")
					raise sys.exit(0)
			settings.update({"rmsepFile":rmsepFile})
			
			# QsarDefaultRmsep
			settings.update({"qsarDefaultRmsep":qsarDefaultRmsep})			

			# QsarExperimentalStandardDeviation
			settings.update({"qsarExperimentalStandardDeviation":qsarExperimentalStandardDeviation})

			# DefaultParameterStandardDeviation
			settings.update({"defaultParameterStandardDeviation":defaultParameterStandardDeviation})
			
			# NameSubstring
			settings.update({"nameSubstring":nameSubstring})

			#
			# DETERMINE OTHER VARIABLES
			#

			#
			# PK parameters section
			#

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

			# Parameter limits
			settings.update({"clLowerLimit":0.0001})	# mL min-1 kg-1
			settings.update({"clUpperLimit":10000})	# mL min-1 kg-1
			settings.update({"vUpperLimit":10000})	# L kg-1

			# Parameter limits: ivOrPo specific
			if settings["ivOrPo"] == "po":
				settings.update({"caco2LowerLimit":0.0000000001})	# cm s-1
				settings.update({"caco2UpperLimit":0.1})	# cm s-1
				settings.update({"solubilityLowerLimit":0.0000000001})	 # M
				settings.update({"solubilityUpperLimit":10.0})	# M
			
			# Parameter limits: level specific
			if settings["levels"] == "free":			
				settings.update({"ppbLowerLimit":0.0001})
				settings.update({"ppbUpperLimit":99.9999})
			
			
			# Plasma volume
			# 
			# Human plasma volume is assumed to be 3 L; plasma volume for dog and rat are based upon this human plasma volume scaled for body weight.
			#
			settings.update({"humanPlasmaVolume":3.000})	# L
			settings.update({"dogPlasmaVolume":(float(settings["dogBodyWeight"]) / float(settings["humanBodyWeight"])) * float(settings["humanPlasmaVolume"])})	# L
			settings.update({"ratPlasmaVolume":(float(settings["ratBodyWeight"]) / float(settings["humanBodyWeight"])) * float(settings["humanPlasmaVolume"])})	# L
			settings.update({"plasmaVolumeSuffix":"PlasmaVolume"})	
			
			#
			# Text section
			#
			
			# pKa terms
			if settings["ivOrPo"] == "po":			
				settings.update({"chargeTypeText":"charge_type"})
				settings.update({"pKaPrefix":"pka_"})
				settings.update({"pKaA1":"pka_a1"})
				settings.update({"pKaA2":"pka_a2"})
				settings.update({"pKaB1":"pka_b1"})
				settings.update({"pKaB2":"pka_b2"})

			# GroupReference
			settings.update({"groupReference":"group_reference"})
			
			# Name - preset based on mapping file
			settings.update({"name":"name"})
			
			# Reference
			settings.update({"reference":"reference"})
			
			# RMSEP labels
			settings.update({"parameterText":"parameter"})
			settings.update({"rmsepSimilarityScore0p5Text":"rmsep_similarity_score_0p5"})
			settings.update({"rmsepSimilarityScore0p6Text":"rmsep_similarity_score_0p6"})
			settings.update({"rmsepSimilarityScore0p7Text":"rmsep_similarity_score_0p7"})
			settings.update({"rmsepSimilarityScore0p8Text":"rmsep_similarity_score_0p8"})
			settings.update({"rmsepSimilarityScore0p9Text":"rmsep_similarity_score_0p9"})
			settings.update({"rmsepSimilarityScore1p0Text":"rmsep_similarity_score_1p0"})
			settings.update({"rmsepOverallText":"rmsep_overall"})	

			# Species abbreviation suffix
			if speciesName == "dog":
				settings.update({"speciesNameAbbreviationSuffix":"_d"})
			elif speciesName == "human":
				settings.update({"speciesNameAbbreviationSuffix":"_h"})
			elif speciesName == "rat":
				settings.update({"speciesNameAbbreviationSuffix":"_r"})

			# Text variables
			settings.update({"prefix":"Prefix"})
			settings.update({"qualifierSuffix":"_qualifier"})
			settings.update({"similaritySuffix":"_similarity"})
			settings.update({"standardDeviationSuffix":"_standard_deviation"})
			settings.update({"unitsSuffix":"_units"})

			#
			# ESTABLISH FURTHER SETTINGS
			#
			
			# Create a revisedErrorParameters list where the speciesName abbreviations is added to cl, v and ppb and "_h" to caco2 in the entered errorParameters list 
			revisedErrorParameters = []
			if errorParameters:
				for parameter in errorParameters:
					if parameter.split("_")[0] in ["cl", "v"]:
						revisedErrorParameters.append(parameter.split("_")[0] + settings["speciesNameAbbreviationSuffix"])
					elif settings["levels"] == "free" and parameter.split("_")[0] == "ppb":
						revisedErrorParameters.append(parameter.split("_")[0] + settings["speciesNameAbbreviationSuffix"])
					elif settings["ivOrPo"] == "po" and parameter.split("_")[0] == "caco2":
						revisedErrorParameters.append(parameter.split("_")[0] + "_h")
					elif settings["ivOrPo"] == "po" and parameter == "solubility":
						revisedErrorParameters.append(parameter)	
			else:
				revisedErrorParameters.append("cl" + settings["speciesNameAbbreviationSuffix"])
				revisedErrorParameters.append("v" + settings["speciesNameAbbreviationSuffix"])
				if settings["ivOrPo"] == "po":
					revisedErrorParameters.append("caco2" + "_h")
					revisedErrorParameters.append("solubility")
				if settings["levels"] == "free":
					revisedErrorParameters.append("ppb" + settings["speciesNameAbbreviationSuffix"])			
				
			settings.update({"revisedErrorParameters":revisedErrorParameters})			
				
			settings.update({"clText":"cl" + settings["speciesNameAbbreviationSuffix"]})
			settings.update({"vText":"v" + settings["speciesNameAbbreviationSuffix"]})
			if settings["ivOrPo"] == "po":
				settings.update({"caco2Text":"caco2_h"})
				settings.update({"solubilityText":"solubility"})

			if settings["levels"] == "free":
				settings.update({"ppbText":"ppb" + settings["speciesNameAbbreviationSuffix"]})
			
			# Column header prefix text
			settings.update({settings["clText"] + settings["prefix"]:"cl_in_vivo_plasma_" + speciesName})	# In vivo clearance (i.e., Cl)
			settings.update({settings["vText"] + settings["prefix"]:"v_steady_state_" + speciesName})	# Volume of distribution @ steady state
			if settings["ivOrPo"] == "po":
				settings.update({settings["caco2Text"] + settings["prefix"]:"caco2_6p5_human"})	# Caco2 (Papp A to B at pH) 6.5 (i.e., Caco2) (always human)
				settings.update({settings["solubilityText"] + settings["prefix"]:"solubility_7p4"})	# (Aqueous) solubility (pH) 7.4 header (not dependent on speciesName)
			if settings["levels"] == "free":
				settings.update({settings["ppbText"] + settings["prefix"]:"ppb_" + speciesName})	# Plasma protein binding (i.e., PPB)
			
			# Parameter units enter as lower cases
			settings.update({settings["clText"] + settings["prefix"] + settings["unitsSuffix"]:["mL min-1 kg-1"]})
			settings.update({settings["vText"] + settings["prefix"] + settings["unitsSuffix"]:["L kg-1"]})
			if settings["ivOrPo"] == "po":
				settings.update({settings["caco2Text"] + settings["prefix"] + settings["unitsSuffix"]:["cm s-1"]})
				settings.update({settings["solubilityText"] + settings["prefix"] + settings["unitsSuffix"]:["m"]})
			if settings["levels"] == "free":
				settings.update({settings["ppbText"] + settings["prefix"] + settings["unitsSuffix"]:["% bound","% free"]})

			# Get column header mappings either from the inputted column header mappings file or insilicolynxdqi/resources/column_header_mappings.txt file
			csvTools = CsvTools(settings)
			if settings["mappingsFile"] != "":
				settings.update({"columnHeaderMappings": csvTools.createDictionaryFromFile(settings["mappingsFile"])})
			else:
				settings.update({"columnHeaderMappings": csvTools.createDictionaryFromFile(os.path.dirname(sys.modules["insilicolynxdqi"].__file__) + os.sep + "resources" + os.sep + "column_header_mappings.txt")})
			
			# Get rmsep data either from the input rmsep file
			if settings["rmsepFile"] != "":
				settings.update({"rmsepDictionary": csvTools.createDictionaryFromFile(settings["rmsepFile"])})
			else:
				settings.update({"rmsepDictionary": []})
			
			# Determine what columns the input dataFile contains
			columnHeadersFound, missingColumnHeaders, potentialColumnsToAdd = csvTools.compareColumnHeaders(settings)		
			if len(missingColumnHeaders) > 0 :
				if len(missingColumnHeaders) == 1:
					print("\nThe file " + dataFile + " is missing the following column header:")
				else:
					print("\nThe file " + dataFile + " is missing the following column headers:")
				for i in missingColumnHeaders:
					print("\t" + i)
				print("Please make alterations to the file " + dataFile + " or rerun this script making reference to an appropriate mappings file (using the arg.mappingsFile command line option).\nExiting.\n")
				raise sys.exit(0)
			
			# ColumnHeadersFound
			settings.update({"columnHeadersFound":columnHeadersFound})
			
			# PotentialColumnsToAdd
			settings.update({"potentialColumnsToAdd":potentialColumnsToAdd})
				
			#
			# GENERATE IN-VIVO SCENARIOS
			#
			
			print("\nGenerate in-vivo scenarios.")
			csvTools.createRevisedScenarioDictionaryFromFile(settings)

			print("")

			# Return the dataFileNew parameter
			return settings["dataFileNew"]
			
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
			
