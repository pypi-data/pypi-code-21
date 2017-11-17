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

description = "The insilicolynxdqi.run folder analyse_in_vivo_calculations.py module"

class AnalyseInVivoCalculations:
	# Class variables


	# __init__
	def __init__(self):
		pass


	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi AnalyseInVivoCalculations class"
		
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
			from insilicolynxdqi.system.process_data import ProcessData
			processData = ProcessData()

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
				method = int(0)

			# Set nameSubstring
			if "nameSubstring" in kwargs:
				nameSubstring = kwargs["nameSubstring"]
			elif "ns" in kwargs:
				nameSubstring = kwargs["ns"]
			else:
				nameSubstring = "_#"

			# Set compartment
			if "compartment" in kwargs:
				compartment = kwargs["compartment"]
			elif "c" in kwargs:
				compartment = kwargs["c"]
			else:
				compartment = "c"

			# Set removeOutliers
			if "removeOutliers" in kwargs:
				removeOutliers = kwargs["removeOutliers"]
			elif "ro" in kwargs:
				removeOutliers = kwargs["ro"]
			else:
				removeOutliers = int(0)

			# Set intervalLevelDistribution
			if "intervalLevelDistribution" in kwargs:
				intervalLevelDistribution = kwargs["intervalLevelDistribution"]
			elif "ild" in kwargs:
				intervalLevelDistribution = kwargs["ild"]
			else:
				intervalLevelDistribution = float(80.00)
				 
			# Set confidenceMeanLevel
			if "confidenceMeanLevel" in kwargs:
				confidenceMeanLevel = kwargs["confidenceMeanLevel"]
			elif "cml" in kwargs:
				confidenceMeanLevel = kwargs["cml"]
			else:
				confidenceMeanLevel = float(80.00)
				 
			# Set smiles
			if "smiles" in kwargs:
				smiles = kwargs["smiles"]
			elif "s" in kwargs:
				smiles = kwargs["s"]
			else:
				smiles = "smiles"
	
			#
			# CHECK AND/OR GENERATE THE PREREQUISITE INPUT DATA
			#
			
			# Dictionary of settings
			settings = {}
			
			# DataFile
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
			settings.update({"method":method})
			
			# NameSubstring
			settings.update({"nameSubstring":nameSubstring})
			
			# Compartment
			settings.update({"compartment":compartment.lower()})

			# RemoveOutliers
			settings.update({"removeOutliers":removeOutliers})
			
			# IntervalLevelDistribution
			if 70.0 < intervalLevelDistribution < 100.0:
				settings.update({"intervalLevelDistribution":intervalLevelDistribution})
			else:
				import sys
				print("\nThe distribution interval level to calculate is restricted to a range of 70.0% to 99.9%. Please reenter a distribution interval level from the allowable range.\nExiting.\n")
				raise sys.exit(0)
			
			# ConfidenceMeanLevel
			if 70.0 < confidenceMeanLevel < 99.9:
				settings.update({"confidenceMeanLevel":confidenceMeanLevel})
				settings.update({"oneSidedProbabilityLevel":float(1) - ((float(1) - (float(settings["confidenceMeanLevel"]) / float(100))) / float(2))})
			else:
				import sys
				print("\nThe two-sided confidence interval of the mean level is restricted to a range of 70.0% to 99.9%. Please reenter a confidence interval of the mean level from the allowable range.\nExiting.\n")
				raise sys.exit(0)
						
			# Smiles
			settings.update({"smiles":smiles})
			
			#
			# DETERMINE OTHER VARIABLES
			#

			# Files to consider section
			#
			
			# Files to analyses
			filesToConsider = []
			methods = []		
			if settings["dataFile"].find(".txt") == -1:
				if os.getcwd() != os.path.dirname(settings["dataFile"]):
					if os.path.dirname(settings["dataFile"]) == "":
						settings["dataFile"] = os.getcwd() + os.sep + os.path.dirname(settings["dataFile"]) + os.path.splitext(os.path.basename(settings["dataFile"]))[0]
					else:
						settings["dataFile"] = os.getcwd() + os.sep + os.path.dirname(settings["dataFile"]) + os.sep + os.path.splitext(os.path.basename(settings["dataFile"]))[0]
				else:
					settings["dataFile"] = os.getcwd() + os.sep + os.path.splitext(os.path.basename(settings["dataFile"]))[0]
				
				fileName = settings["dataFile"] + "po_1c_total_" + settings["speciesName"] + ".txt"
				if os.path.exists(fileName):
					filesToConsider.append(fileName)
					methods.append(1)
				fileName = settings["dataFile"] + "po_1c_free_" + settings["speciesName"] + ".txt"
				if os.path.exists(fileName):
					filesToConsider.append(fileName)
					methods.append(2)						
				fileName = settings["dataFile"] + "po_2c_total_" + settings["speciesName"] + ".txt"
				if os.path.exists(fileName):
					filesToConsider.append(fileName)
					methods.append(3)					
				fileName = settings["dataFile"] + "po_2c_free_" + settings["speciesName"] + ".txt"
				if os.path.exists(fileName):
					filesToConsider.append(fileName)
					methods.append(4)
				fileName = settings["dataFile"] + "iv_2c_total_" + settings["speciesName"] + ".txt"
				if os.path.exists(fileName):
					filesToConsider.append(fileName)
					methods.append(5)					
				fileName = settings["dataFile"] + "iv_2c_free_" + settings["speciesName"] + ".txt"
				if os.path.exists(fileName):
					filesToConsider.append(fileName)
					methods.append(6)
				
				if len(filesToConsider) == 0:
					import sys
					print("\nNo files available to process with the substring " + dataFile + ". Please select a valid substring.\nExiting.\n")
					raise sys.exit(0)
				
				elif len(filesToConsider) == 1:
					# Export files
					if methods[0] in [1, 3, 5]:
						settings.update({"fileNameTotal":os.path.dirname(settings["dataFile"]) + os.sep + "analysis_" + os.path.splitext(os.path.basename(filesToConsider[0]))[0] + ".txt"})			
					elif methods[0] in [2, 4, 6]:
						settings.update({"fileNameFree":os.path.dirname(settings["dataFile"]) + os.sep + "analysis_" + os.path.splitext(os.path.basename(filesToConsider[0]))[0] + ".txt"})											
				else:
					# Export files
					settings.update({"fileNameTotal":os.path.dirname(settings["dataFile"]) + os.sep + "analysis_multiple_methods" + "_total_" + settings["speciesName"] + ".txt"})
					settings.update({"fileNameFree":os.path.dirname(settings["dataFile"]) + os.sep + "analysis_multiple_methods" + "_free_" + settings["speciesName"] + ".txt"})
				
			else:
				if method in [1, 2, 3, 4, 5, 6]:					
					if os.getcwd() != os.path.dirname(settings["dataFile"]):
						if os.path.dirname(settings["dataFile"]) == "":
							settings["dataFile"] = os.getcwd() + os.sep + os.path.dirname(settings["dataFile"]) + os.path.splitext(os.path.basename(settings["dataFile"]))[0] + ".txt"
						else:
							settings["dataFile"] = os.getcwd() + os.sep + os.path.dirname(settings["dataFile"]) + os.sep + os.path.splitext(os.path.basename(settings["dataFile"]))[0] + ".txt"
					else:
						settings["dataFile"] = os.getcwd() + os.sep + os.path.splitext(os.path.basename(settings["dataFile"]))[0] + ".txt"
					
					if not os.path.isfile(settings["dataFile"]):
						print("\nThe file " + dataFile + " does not exist. Please select a valid file.\nExiting.\n")
						raise sys.exit(0)
					else:
						filesToConsider.append(settings["dataFile"])
						methods.append(method)
						
						# Export files
						if method in [1, 3, 5]:
							settings.update({"fileNameTotal":os.path.dirname(settings["dataFile"]) + os.sep + "analysis_" + os.path.splitext(os.path.basename(dataFile))[0] + ".txt"})
						elif method in [2, 4, 6]:
							settings.update({"fileNameFree":os.path.dirname(settings["dataFile"]) + os.sep + "analysis_" + os.path.splitext(os.path.basename(dataFile))[0] + ".txt"})
				else:
					import sys
					print("\nPlease enter an integer between 1 and 6 for the approximation method of interest.\nExiting.\n")
					raise sys.exit(0)
					
			# FilesToConsider		
			settings.update({"filesToConsider":filesToConsider})
			
			# Methods
			settings.update({"methods":methods})

			#
			# Data analysis section
			#

			# ConcentrationScales
			settings.update({"concentrationScales":["concentration_", "auc_concentration_"]})
						
			# ExportRescaledUnitsText - dictionary whose key correspond to the scale
			settings.update({"exportRescaledUnitsText":{"concentration_":"(M)", "auc_concentration_":"M min"}})
			
			# ExportUnitsText - dictionary whose key correspond to the scale
			settings.update({"exportUnitsText":{"amount_":"(mg)", "concentration_":"(mg_L-1)", "auc_amount_":"(mg_min)", "auc_concentration_":"(mg_min_L-1)"}})

			# InterceptLabels
			settings.update({"interceptLabels":["intercept_max_", "intercept_min_", "intercept_mid_", "intercept_auc_"]})
			
			# DoseLabels
			settings.update({"doseLabels":["dose_max_", "dose_min_", "dose_mid_", "dose_auc_"]})

			# PrefixOptions
			settings.update({"prefixOptions":["concentration_peripheral_", "concentration_central_peripheral_", "auc_concentration_peripheral_", "auc_concentration_central_tissue_"]})

			# QuantityLabels
			settings.update({"quantityLabels":["max_", "min_", "mid_", "auc_"]})
						
			# Scales
			settings.update({"scales":["amount_", "concentration_", "auc_amount_", "auc_concentration_"]})
			
			# TextFileExtension
			settings.update({"textFileExtension":".txt"})

			# IvTitlesText
			settings.update({"ivTitlesText":["maximum_value", "minimum_value", "mid_value", "value"]})
			
			# PoTitlesText
			settings.update({"poTitlesText":["intercept_max_vs_dose_max", "intercept_min_vs_dose_min", "intercept_mid_vs_dose_mid", "intercept_auc_vs_dose_auc"]})
			
			#
			# Statistics section
			#
	
			# Current T critical value degrees of freedom
			settings.update({"currentTCriticalValueDegreesOfFreedom":0})

			#
			# Text section
			#

			# Compartments
			settings.update({"compartments":["c", "p", "cp", "all"]})
			if any(item in settings["methods"] for item in [3, 4, 5, 6]) and settings["compartment"] not in settings["compartments"]:
				import sys
				print("\nPlease enter c, p, cp or all with respect to the compartment.\nExiting.\n")
				raise sys.exit(0)

			# Data column header text
			settings.update({"andText":"and"})
			settings.update({"approximateText":"_approximate_"})
			settings.update({"areaText":"area"})
			settings.update({"centroidText":"_centroid"})
			settings.update({"iXText":"2nd_moment_of_area_x_dimension"}) 
			settings.update({"iYText":"2nd_moment_of_area_y_dimension"})
			settings.update({"log10Text":"log10("})
			settings.update({"lowerConfidenceIntervalOfTheMeanText":"percent_lower_confidence_interval_of_the_mean"})
			settings.update({"lowerDistributionIntervalText":"percent_lower_distribution_interval"})
			settings.update({"meanText":"mean"})
			settings.update({"parenthesisText":")"})
			settings.update({"spaceText":"_"})
			settings.update({"stDevText":"stdev"})
			settings.update({"upperConfidenceIntervalOfTheMeanText":"percent_upper_confidence_interval_of_the_mean"})
			settings.update({"upperDistributionIntervalText":"percent_upper_distribution_interval"})
			settings.update({"xCentroidText":"x_centroid"})
			settings.update({"xDataText":"x"})
			settings.update({"yCentroidText":"y_centroid"}) 

			# File prefix and suffix
			settings.update({"analysisPrefix":"analysis_"})
			settings.update({"summarySuffix":"_summary"})

			# GroupReference - should be present in the input data set
			settings.update({"groupReference":"group_reference"})
			
			# MolecularWeight - should be present in the input data set
			settings.update({"molecularWeightText":"mol_wt"})
			
			# Name - should be present in the input data set
			settings.update({"name":"name"})
			
			# Reference - should be present in the input data set
			settings.update({"reference":"reference"})

			#		
			# ANALYSE IN-VIVO CALCULATIONS
			#
			
			print("\nAnalyse in-vivo calculations.")
			processData.processData(settings)
			
			print("\n")
		
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

