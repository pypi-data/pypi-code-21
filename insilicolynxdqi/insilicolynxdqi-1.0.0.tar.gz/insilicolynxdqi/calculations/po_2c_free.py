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

description = "The insilicolynxdqi.calculations folder po_2c_free.py module"

class Po2CFree:	
	# Class variables


	# __init__	
	def __init__(self):
		pass


	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi Po2CFree class"
		
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)
			
			
	# Process file
	def processFile(self, settings):
		try:			
			import csv
			import math
			from insilicolynxdqi.system.csv_tools import CsvTools
			from insilicolynxdqi.system.common_methods import CommonMethods
			from insilicolynxdqi.system.analysis import Analysis
			csvTools = CsvTools(None)
			commonMethods = CommonMethods()
			analysis = Analysis(settings)

			allNames = []
			allValues1 = {}
			allValues2 = {}
			allValues3 = {}
			allValues4 = {}
			allValues5 = {}
			# Column header suffix text
			columnHeaderSuffix = []		
			for i in range(5):
				columnHeaderSuffix.append("_(" + settings["columnHeaderSuffix"] + "_" + str(i + 1) + ")")
			
			# Open data file
			fileToRead = open(settings["dataFile"], 'r')

			print("")
			with fileToRead:
				reader = csv.DictReader(fileToRead, delimiter="\t")
				i = 0
				for row in reader:
					i += 1
					print("\t" + str(i) + " out of " + str(settings["numberRows"]) + ": " + row[settings["name"]])
					maxAmountBValues = {}
					minAmountBValues = {}
					midAmountBValues = {}	
					aucAmountBValues = {}
					maxConcentrationBValues = {}
					minConcentrationBValues = {}
					midConcentrationBValues ={}
					aucConcentrationBValues ={}
					maxAmountCValues = {}
					minAmountCValues = {}
					midAmountCValues = {}
					aucAmountCValues = {}
					maxAmountBCValues = {}
					minAmountBCValues = {}
					midAmountBCValues = {}
					aucAmountBCValues = {}
					
					#
					# Set calculation variables for system A -> B (= C) -> D:
					# A is drug in small intestines, B and C are drug in central and peripheral compartments of the body, respectively, and D is the drug eliminated from B
					# Assume first-order rate constant for absorption (i.e., A -> B), distribution (i.e., B -> C and C -> B) and elimination (i.e., B -> D)
					# First dose occurs at t=0 and then at regular intervals (i.e., equivalent to t=3) until the end of the simulation (i.e., t=4)
					# Assume a time delay before absorption can occur (i.e., from t=0 to t=1)
					# Absorption can only occur over a particular time window under saturated and / or unsaturated conditions (i.e., from t=1 to t=2)
					# After which further absorption from a particular dose is ignored upto the end of the simulation (i.e., from t=2 to t=4)
					# Saturated conditions occur when the amount of drug in A exceeds solubility_6p5 (mg mL-1) x (small) intestinal fluid volume (mL)
					# Assume instant dispersion and dissolution of drug in the (small) intestinal fluid volume such that rate under saturated conditions is solubility6P5Saturated x k1
					# Once the amount of drug in A drops to solubility6P5Saturated assume first-order rate (i.e., solubility6P5Saturated x exp(-1 x k1 x t))
					# Time is on a minute scale and doses are in mg
					#
					# t0 = start of simulation (min), i.e., 0 min
					# t1 = absorption delay time (min)
					# t2 = intestinal transit time (min)
					# t3 = dose interval time (min)
					# t4 = simulation length (min)
					#

					# Fraction unbound
					fu = commonMethods.setFu(row[settings["ppbText"] + settings["speciesName"]], row[settings["ppbText"] + settings["speciesName"] + settings["unitsSuffix"]], settings)
					
					# Determine molecularWeight
					molecularWeight = row[settings["molecularWeightText"]]				
					
					# Solubility parameters
					solubility6P5MgPerML = commonMethods.setSolubility6P5MgPerML(molecularWeight, row[settings["solubility6P5Text"]])
					solubility6P5Saturated = commonMethods.setSolubility6P5Saturated(solubility6P5MgPerML, settings)
					
					# Determine times (times returned with units of min)
					t0 = 0
					t1 = settings[settings["speciesName"] + settings["absorptionDelaySuffix"]]	# Already in min
					t2 = settings[settings["speciesName"] + settings["intestinalTransitTimeSuffix"]]	# Already in min
					t3, t4 = commonMethods.setT3T4(row, settings)
					doseTimes, timeVector, timesAUC = commonMethods.createTimeVector(t1, t2, t3, t4, settings)
									
					# Set k1 (k1 returned with units of min-1)
					k1 = commonMethods.setK1(row[settings["absorptionRateConstantText"] + settings["speciesName"]], row[settings["absorptionRateConstantText"] + settings["speciesName"] + settings["unitsSuffix"]], settings)
								
					# Set cl, v and rates (cl returned with units of L min-1, v returned with units of L and rates returned with units of min-1)
					cl, vss, vcentralList, k2K3RatioList, k2Rates, k3Rates, k4Rates, vterminalList = commonMethods.setK2K3K4Rates(row[settings["clText"] + settings["speciesName"]], row[settings["clText"] + settings["speciesName"] + settings["unitsSuffix"]], row[settings["vssText"] + settings["speciesName"]], row[settings["vssText"] + settings["speciesName"] + settings["unitsSuffix"]], settings)
			
					# First pass hepatic clearance fraction limit (cl has units of L min-1)
					fh = commonMethods.setFh(cl, settings)
					
					# Add to list of names
					allNames.append(row[settings["name"]])
					
					# Loop through the two scenarios
					for index in range(0, 5):
						extrapolatedData = {}
						# Loop through doses
						for dose in settings["doses"]:
							# Determine alpha and beta values bases on k2, k3 and k4 values
							alpha, beta = commonMethods.setAlphaBeta(k2Rates[index], k3Rates[index], k4Rates[index])
					
							# Calculate levels
							amountBVector, amountCVector, amountBCVector, t12Condition, t12Saturated, bt12Saturated, bt2, ct12Saturated, ct2, dosingParametersAUC = self.po2CFree(doseTimes, timeVector, dose, vcentralList[index], k2Rates[index], k3Rates[index], k4Rates[index], alpha, beta, solubility6P5Saturated, fh, k1, t0, t1, t2, t3, t4)	

							# Calculate AUC during a chosen time interval	
							aucAmountB, aucAmountC = self.calculateAUC(timesAUC, dose, vcentralList[index], k2Rates[index], k3Rates[index], k4Rates[index], alpha, beta, settings["numberOfSegments"], fh, k1, dosingParametersAUC)
							
							# Create concentrationBVector list which is an elementwise division of amountBVector by v1
							concentrationBVector = [x / float(vcentralList[index]) for x in amountBVector] 
							
							if settings["saveRawDataFiles"] == "yes":							
								# Add raw parameter details
								rawValues = commonMethods.addRawParameters2C(settings, [cl, vss, vcentralList[index], k2Rates[index], k3Rates[index], k4Rates[index], vterminalList[index], alpha, beta, t1, t2, t3, t4, fh, solubility6P5Saturated, k1, t12Condition, t12Saturated, bt12Saturated, bt2, ct12Saturated, ct2])
								rawDataFile = settings["pathSubSubSub1"] + row[settings["name"]] + "_" + str(dose).replace(".","p") + columnHeaderSuffix[index] + settings["textExtension"]
								csvTools.exportFiveListsToCSV(rawDataFile, timeVector, amountBVector, concentrationBVector, amountCVector, amountBCVector, rawValues, settings["csvFileColumnHeaderTimeText"], 
								settings["csvFileColumnHeaderAmountCentralText"], settings["csvFileColumnHeaderConcentrationText"], settings["csvFileColumnHeaderAmountPeripheralText"], settings["csvFileColumnHeaderAmountText"], 
								settings["csvFileColumnHeaderRawParameterText"], settings["csvFileColumnHeaderRawParameterValueText"])
								
							# Determine maximum and minimum values
							maxAmountBValue, minAmountBValue = commonMethods.extremeValues(timeVector, t1, amountBVector, doseTimes)								
							maxConcentrationBValue, minConcentrationBValue = commonMethods.extremeValues(timeVector, t1, concentrationBVector, doseTimes)											
							maxAmountCValue, minAmountCValue = commonMethods.extremeValues(timeVector, t1, amountCVector, doseTimes)					
							maxAmountBCValue, minAmountBCValue = commonMethods.extremeValues(timeVector, t1, amountBCVector, doseTimes)		
							
							# Add maximum, minimum, midedle and auc values to dictionaries
							maxAmountBValues.update({dose:float(maxAmountBValue) * float(fu)})
							minAmountBValues.update({dose:float(minAmountBValue) * float(fu)})					
							if maxAmountBValue != 'nan' and minAmountBValue != 'nan':
								midAmountBValues.update({dose:float(math.pow(10, ((math.log10(float(maxAmountBValue)) + math.log10(float(minAmountBValue))) / 2)) * float(fu))})
							else:
								midAmountBValues.update({dose:'nan'})
							aucAmountBValues.update({dose:float(aucAmountB) * float(fu)})
		
							maxConcentrationBValues.update({dose:float(maxConcentrationBValue) * float(fu)})
							minConcentrationBValues.update({dose:float(minConcentrationBValue) * float(fu)})
							if maxConcentrationBValue != 'nan' and minConcentrationBValue != 'nan':
								midConcentrationBValues.update({dose:float(math.pow(10, ((math.log10(float(maxConcentrationBValue)) + math.log10(float(minConcentrationBValue))) / 2)) * float(fu))})
							else:
								midConcentrationBValues.update({dose:'nan'})
							aucConcentrationBValues.update({dose:(float(aucAmountB) / float(vcentralList[index])) * float(fu)})
							
							maxAmountCValues.update({dose:float(maxAmountCValue) * float(fu)})
							minAmountCValues.update({dose:float(minAmountCValue) * float(fu)})						
							if maxAmountCValue != 'nan' and minAmountCValue != 'nan':
								midAmountCValues.update({dose:float(math.pow(10, ((math.log10(float(maxAmountCValue)) + math.log10(float(minAmountCValue))) / 2)) * float(fu))})
							else:
								midAmountCValues.update({dose:'nan'})
							aucAmountCValues.update({dose:float(aucAmountC) * float(fu)})
							
							maxAmountBCValues.update({dose:float(maxAmountBCValue) * float(fu)})
							minAmountBCValues.update({dose:float(minAmountBCValue) * float(fu)})
							if maxAmountBCValue != 'nan' and minAmountBCValue != 'nan':
								midAmountBCValues.update({dose:float(math.pow(10, ((math.log10(float(maxAmountBCValue)) + math.log10(float(minAmountBCValue))) / 2)) * float(fu))})
							else:
								midAmountBCValues.update({dose:'nan'})
							aucAmountBCValues.update({dose:float(aucAmountB + aucAmountC) * float(fu)})
							
						# Export maximum, minimum and middle amount data from nine dictionaries that share the same keys to CSV file
						rawDataFile = settings["pathSubSubSub2"] + row[settings["name"]] + columnHeaderSuffix[index] + settings["textExtension"]
						csvTools.exportNineDictionariesToCSV(rawDataFile, maxAmountBValues, minAmountBValues, midAmountBValues, maxAmountCValues, minAmountCValues, midAmountCValues, maxAmountBCValues, minAmountBCValues, midAmountBCValues, settings)
						
						# Export maximum, minimum and middle concentration data from three dictionaries that share the same keys to CSV file
						rawDataFile = settings["pathSubSubSub3"] + row[settings["name"]] + columnHeaderSuffix[index] + settings["textExtension"]
						csvTools.exportThreeDictionariesToCSV(rawDataFile, maxConcentrationBValues, minConcentrationBValues, midConcentrationBValues, settings, "concentrations")
						
						# Export aucAmountBValues, aucConcentrationBValues, aucAmountCValues and aucAmountBCValues data from four dictionaries that share the same keys to CSV file
						rawDataFile = settings["pathSubSubSub4"] + row[settings["name"]] + columnHeaderSuffix[index] + settings["textExtension"]
						csvTools.exportAucDictionariesToCSV(rawDataFile, aucAmountBValues, aucConcentrationBValues, aucAmountCValues, aucAmountBCValues, settings)

						if settings["compartment"] == "central":
							# Perform analysis using "dose" ~ "amount_B_max" and "dose" ~ "amount_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBValues, minAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analysis using "dose" ~ "amount_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analysis using "dose" ~ "auc_amount_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBValues, settings["aucAmountBPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "concentration_B_max" and "dose" ~ "concentration_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxConcentrationBValues, minConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])

							# Perform analysis using "dose" ~ "concentration_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "auc_concentration_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucConcentrationBValues, settings["aucConcentrationBPrefix"], columnHeaderSuffix[index])
						
						elif settings["compartment"] == "peripheral":
							# Perform analysis using "dose" ~ "amount_C_max" and "dose" ~ "amount_C_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountCValues, minAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
						
							# Perform analysis using "dose" ~ "amount_C_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "auc_amount_C" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountCValues, settings["aucAmountCPrefix"], columnHeaderSuffix[index])

						elif settings["compartment"] == "central_peripheral":
							# Perform analysis using "dose" ~ "amount_BC_max" and "dose" ~ "amount_BC_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBCValues, minAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
						
							# Perform analysis using "dose" ~ "amount_BC_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "auc_amount_BC" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBCValues, settings["aucAmountBCPrefix"], columnHeaderSuffix[index])
						
						elif settings["compartment"] == "all":
							# Perform analysis using "dose" ~ "amount_B_max" and "dose" ~ "amount_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBValues, minAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analysis using "dose" ~ "amount_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analysis using "dose" ~ "auc_amount_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBValues, settings["aucAmountBPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "concentration_B_max" and "dose" ~ "concentration_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxConcentrationBValues, minConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])

							# Perform analysis using "dose" ~ "concentration_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "auc_concentration_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucConcentrationBValues, settings["aucConcentrationBPrefix"], columnHeaderSuffix[index])
						
							# Perform analysis using "dose" ~ "amount_C_max" and "dose" ~ "amount_C_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountCValues, minAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
						
							# Perform analysis using "dose" ~ "amount_C_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "auc_amount_C" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountCValues, settings["aucAmountCPrefix"], columnHeaderSuffix[index])
						
							# Perform analysis using "dose" ~ "amount_BC_max" and "dose" ~ "amount_BC_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBCValues, minAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
						
							# Perform analysis using "dose" ~ "amount_BC_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
							
							# Perform analysis using "dose" ~ "auc_amount_BC" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBCValues, settings["aucAmountBCPrefix"], columnHeaderSuffix[index])
					
						if index == 0:
							# Add additional parameters to a dictionary of values
							values1 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t1, t2, t3, t4, fh], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile1 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data	
							allValues1.update({row[settings["name"]]:values1})
						elif index == 1:
							# Add additional parameters to a dictionary of values
							values2 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t1, t2, t3, t4, fh], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile2 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data
							allValues2.update({row[settings["name"]]:values2})
						elif index == 2:
							# Add additional parameters to a dictionary of values
							values3 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t1, t2, t3, t4, fh], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile3 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data	
							allValues3.update({row[settings["name"]]:values3})
						elif index == 3:
							# Add additional parameters to a dictionary of values
							values4 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t1, t2, t3, t4, fh], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile4 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data
							allValues4.update({row[settings["name"]]:values4})
						elif index == 4:
							# Add additional parameters to a dictionary of values
							values5 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t1, t2, t3, t4, fh], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile5 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data
							allValues5.update({row[settings["name"]]:values5})	
			
			# Export all the information within the allValues1, allValues2, allValues3 and allValues4 dictionaries to CSV file		
			csvTools.exportValuesToCSV(dataFile1, allNames, allValues1)
			csvTools.exportValuesToCSV(dataFile2, allNames, allValues2)
			csvTools.exportValuesToCSV(dataFile3, allNames, allValues3)
			csvTools.exportValuesToCSV(dataFile4, allNames, allValues4)
			csvTools.exportValuesToCSV(dataFile5, allNames, allValues5)
									
			# Return output
			return allNames, allValues1, allValues2, allValues3, allValues4, allValues5, columnHeaderSuffix
			
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)		
		
		finally:
			fileToRead.close()


	# Po 2C free levels
	def po2CFree(self, doseTimes, timeVector, dose, v1, k2, k3, k4, alpha, beta, solubility6P5Saturated, fh, k1, t0, t1, t2, t3, t4):				   
		try:
			#
			# Determine whether at t=1 saturated or unsaturated conditions apply, if the former determine how long saturated conditions last
			#		
			if float(dose) > float(solubility6P5Saturated):
				#
				# Saturated conditions apply at t1
				#
				t12Saturated = float(dose) / (float(solubility6P5Saturated) * float(k1))
				
				if t12Saturated > t2:
					t12Condition = "saturated"
					a0 = solubility6P5Saturated
					bt12Saturated = self.amountB_1(t2, [a0, fh, k1, k2, k3, k4, alpha, beta])
					ct12Saturated = self.amountC_1(t2, [a0, fh, k1, k2, k3, k4, alpha, beta])		
				else:
					t12Condition = "saturated_becoming_unsaturated"
					#
					# Calculate the amount of drug in B and C at the transition point between saturated and unsaturated conditions
					# Apply self.amountB_1 and self.amountC_1 where the starting conditions for A0 = solubility6P5Saturated, B0 = 0 and C0 = 0
					# bt12Saturated and ct12Saturated will equal the amount in B and C at the end of the saturation period
					#
					a0 = solubility6P5Saturated
					bt12Saturated = self.amountB_1(t12Saturated, [a0, fh, k1, k2, k3, k4, alpha, beta])
					ct12Saturated = self.amountC_1(t12Saturated, [a0, fh, k1, k2, k3, k4, alpha, beta])	
			else:
				# Unsaturated conditions apply at t1
				t12Saturated = 0
				t12Condition = "unsaturated"
				a0 = dose
				bt12Saturated = 0
				ct12Saturated = 0
				
			#
			# Use principle of superposition - separately calculate amount in B for each dose from its time of dosing up to the end of the simulation and then combine all the amounts for a given time point  
			#
			amountBVector = [0 for x in range(0, len(timeVector))]
			amountCVector = [0 for x in range(0, len(timeVector))]
			dosingParametersAUC = {}
			bt2 = 0
			ct2 = 0
			for doseTime in doseTimes:
				for timeVectorIndex, t in enumerate(timeVector):
					if doseTime <= t:
						timeToUse = t - doseTime
						if timeToUse < t1:
							#
							# Amount t=0 to t=1
							# Nothing of the dose in B or C throughout due to absorption delay
							#
							tAmountB = 0
							tAmountC = 0
							
						if t1 <= timeToUse <= (t2 + t1):
							#
							# Amount t=1 to t=2
							# Absorption period - absorption (under saturated and unsaturated conditions) and elimination
							# 
							if t12Condition == "saturated":
								#
								# Rate of absorption under saturated conditions
								# Apply self.amountB_1 self.amountC_1 and reset the time - use timeToUseAdjusted = timeToUse - t1
								# The amount in A = solubility6P5Saturated throughout
								# Nothing of the dose in B or C at timeToUseAdjusted = 0 
								#
								timeToUseAdjusted = timeToUse - t1
								tAmountB = self.amountB_1(timeToUseAdjusted, [a0, fh, k1, k2, k3, k4, alpha, beta])
								tAmountC = self.amountC_1(timeToUseAdjusted, [a0, fh, k1, k2, k3, k4, alpha, beta])
								if timeToUse == (t1 + t2):
									bt2 = tAmountB
									ct2 = tAmountC
							
							elif t12Condition == "saturated_becoming_unsaturated":
								#
								# Rate of absorption initially under saturated and then unsaturated conditions
								# Apply self.amountB_1 and self.amountC_1 and reset the time - use timeToUseAdjusted = timeToUse - t1
								# While timeToUseAdjusted < t12Saturated, saturated conditions apply
								# The amount in A = solubility6P5Saturated throughout
								# Nothing of the dose in B or C at timeToUseAdjusted = 0 
								# When timeToUseAdjusted >= t12Saturated, unsaturated conditions apply
								# Apply self.amountB_2 and self.amountC_2 resetting the time again - use timeToUseAdjustedAgain = timeToUseAdjusted - t12Saturated
								# The amount in A at the start = solubility6P5Saturated
								# The amount in B at the start = bt12Saturated
								# The amount in C at the start = ct12Saturated
								#
								timeToUseAdjusted = timeToUse - t1
								if timeToUseAdjusted < t12Saturated:
									tAmountB = self.amountB_1(timeToUseAdjusted, [a0, fh, k1, k2, k3, k4, alpha, beta])
									tAmountC = self.amountC_1(timeToUseAdjusted, [a0, fh, k1, k2, k3, k4, alpha, beta])
								elif timeToUseAdjusted >= t12Saturated:
									timeToUseAdjustedAgain = timeToUseAdjusted - t12Saturated
									b0 = bt12Saturated 
									c0 = ct12Saturated
									tAmountB = self.amountB_2(timeToUseAdjustedAgain, [a0, b0, c0, fh, k1, k2, k3, k4, alpha, beta])
									tAmountC = self.amountC_2(timeToUseAdjustedAgain, [a0, b0, c0, fh, k1, k2, k3, k4, alpha, beta])
								if timeToUse == (t1 + t2):
									bt2 = tAmountB
									ct2 = tAmountC
								
							elif t12Condition == "unsaturated":
								#
								# Rate of absorption under unsaturated conditions
								# Use timeToUseAdjusted = timeToUse - t1
								# At timeToUseAdjusted = 0, the amount in A (i.e., A0) = dose
								# Nothing of the dose in B and C at timeToUseAdjusted = 0 
								#
								timeToUseAdjusted = timeToUse - t1
								b0 = 0
								c0 = 0
								tAmountB = self.amountB_2(timeToUseAdjusted, [a0, b0, c0, fh, k1, k2, k3, k4, alpha, beta])
								tAmountC = self.amountC_2(timeToUseAdjusted, [a0, b0, c0, fh, k1, k2, k3, k4, alpha, beta])	
								if timeToUse == (t1 + t2):
									bt2 = tAmountB
									ct2 = tAmountC
											
						if (t2 + t1) < timeToUse:
							#
							# Amount t=2 to t=4
							# No absorption just elimination
							# Use timeToUseAdjusted = timeToUse - t2
							# At timeToUseAdjusted = 0, the amount in B (i.e., B0) = B(t=2) and the amount in C (i.e., C0) = C(t=2)
							#
							timeToUseAdjusted = timeToUse - (t2 + t1)		
							b0 = bt2
							c0 = ct2
							tAmountB = self.amountB_3(timeToUseAdjusted, [b0, c0, k1, k2, k3, k4, alpha, beta])
							tAmountC = self.amountC_3(timeToUseAdjusted, [b0, c0, k1, k2, k3, k4, alpha, beta])
							
						amountBVector[timeVectorIndex] += tAmountB
						amountCVector[timeVectorIndex] += tAmountC
			
			dosingParametersAUC.update({dose:[t12Condition, t0, t1, t2, t12Saturated, a0, bt12Saturated, ct12Saturated, bt2, ct2]})
			
			# Create amountBCVector list which is an elementwise sum of amountCVector and amountCVector 
			amountBCVector = [sum(x) for x in zip(amountBVector, amountCVector)]
							
			# Return output
			return amountBVector, amountCVector, amountBCVector, t12Condition, t12Saturated, bt12Saturated, bt2, ct12Saturated, ct2, dosingParametersAUC			
			
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)


	# Calculate AUC
	def calculateAUC(self, timesAUC, dose, v1, k2, k3, k4, alpha, beta, numberOfSegments, fh, k1, dosingParametersAUC):
		try:
			from insilicolynxdqi.system.area_under_curve import AreaUnderCurve
			areaUnderCurve = AreaUnderCurve()
			
			# timesAUC{dosingIntervalsToConsider:[lowerTime, upperTime]} - multiple doses in dictionary
			# dosingParametersAUC{dose:[t12Condition, t0, t1, t2, t12Saturated, a0, bt12Saturated, ct12Saturated, bt2, ct2]} - only 1 dose returned as a list within a dictionary
			
			aucAmountB = 0
			aucAmountC = 0
			for doseInterval in timesAUC:
				tLower = timesAUC[doseInterval][0]
				tUpper = timesAUC[doseInterval][1] # tUpper > tLower
				t12Condition = dosingParametersAUC[dose][0]
				t0 = dosingParametersAUC[dose][1] # Time of dose = 0
				t1 = dosingParametersAUC[dose][2] # Time of absorption delay
				t2 = dosingParametersAUC[dose][3] # Time of absorption window
				t12Saturated = dosingParametersAUC[dose][4] # Time of saturation

				#
				# Saturated scenario (e.g. t1 = 60 min and t2 = 240 min):
				#
				# Times: 	t0				Eq.0			t1								Eq.1								   t12				Eq.3
				#		  (0 min)						 (60 min) <---------------------- (240 min) ---------------------------> (300 min)				
				# (01):		|								|																		|		tLower <----------------------------> tUpper	
				# (02):		|		tLower <--> tUpper		|																		|
				# (03):		|		tLower <--------------->|<------------------------------------------------> tUpper				|
				# (04):		|		tLower <--------------->|<--------------------------------------------------------------------->|<------------------------> tUpper
				# (05):		|								|	tLower <--------------------------------------> tUpper				|
				# (06):		|								|	tLower <----------------------------------------------------------->|<------------------------> tUpper
				#
				# Unsaturated scenario (e.g. t1 = 60 min and t2 = 240 min):
				#
				# Times: 	t0				Eq.0			t1								Eq.2								   t12				Eq.3
				#		  (0 min)						 (60 min) <---------------------- (240 min) ---------------------------> (300 min)				
				# (07):		|		tLower <--> tUpper		|																		|
				# (08):		|		tLower <--------------->|<------------------------------------------------> tUpper				|
				# (09):		|		tLower <--------------->|<--------------------------------------------------------------------->|<------------------------> tUpper
				# (10):		|								|	tLower <--------------------------------------> tUpper				|
				# (11):		|								|	tLower <----------------------------------------------------------->|<------------------------> tUpper
				#
				# Saturated becoming unsaturated scenario (e.g. t1 = 60 min, t12Saturated = 100 min  and t2 = 240 min):
				#
				# Times: 	t0				Eq.0			t1			Eq.1			   t12S				Eq.2				   t12				Eq.3
				#		  (0 min)						 (60 min) <---- (100 min) ----> (160 min) <---------------------------> (300 min)				
				# (12):		|		tLower <--> tUpper		|								|										|
				# (13):		|		tLower <--------------->|<-----------------> tUpper		|										|
				# (14):		|		tLower <--------------->|<----------------------------->|<----------------> tUpper				|
				# (15):		|		tLower <--------------->|<----------------------------->|<------------------------------------->|<------------------------> tUpper
				# (16):		|								|	tLower <-------> tUpper		|										|
				# (17):		|								|	tLower <------------------->|<----------------> tUpper				|
				# (18):		|								|	tLower <------------------->|<------------------------------------->|<------------------------> tUpper
				# (19):		|								|								|	tLower <------> tUpper				|
				# (20):		|								|								|	tLower <--------------------------->|<------------------------> tUpper
				#

				# Note AUC between t0 and t1  = 0

				t12 = int(t1) + int(t2) # e.g., t12 = 300 min 
				# Is tLower greater than t12?
				if int(tLower) >= int(t12): # Check for scenario (01)
				
					# Yes, scenario (01) applies
					# "(01) Integrate Eq. 3 from ", int(tLower) - int(t12), " to ", int(tUpper) - int(t12) 
					aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t12)), (int(tUpper) - int(t12)), numberOfSegments)
					aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t12)), (int(tUpper) - int(t12)), numberOfSegments)
				
				else:
					# No. Need to establish absorption conditions and then decide on which scenario applies
					if t12Condition == "saturated":
						# Is tLower < t1?
						if int(tLower) < int(t1):
							# Yes - scenario (02), (03) or (04) could apply
							if int(tUpper) <= int(t1): # Check for scenario (02)
								
								# Yes, scenario (02) applies
								# "(02) AUC = 0"
								aucAmountB += 0
								aucAmountC += 0
							
							elif int(t1) < int(tUpper) <= int(t12): # Check for scenario (03)
								
								# Yes, scenario (03) applies
								# "(03) Integrate Eq. 1 from ", 0, " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t1)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t1)), numberOfSegments)
							
							elif int(tUpper) > int(t12): # Check for scenario (04)
								
								# Yes, scenario (04) applies
								# "(04a) Integrate Eq. 1 from ", 0, " to ", int(t2)
								# "(04b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, int(t2), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, int(t2), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
						
						elif int(t1) <= int(tLower):
							# No  scenarios (05) or (06) apply
							if int(t1) < int(tUpper) <= int(t12): # Check for scenario (05)
								
								# Yes, scenario (05) applies
								# "(05) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)
							
							elif int(tUpper) > int(t12): # Check for scenario (06)
								
								# Yes, scenario (06) applies
								# "(06a) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(t2)
								# "(06b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t2), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t2), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
						
					elif t12Condition == "unsaturated":
						# Is tLower < t1?
						if int(tLower) < int(t1):
							# Yes - scenario (07), (08) or (09) could apply
							if int(tUpper) <= int(t1): # Check for scenario (07)
								
								# Yes, scenario (07) applies
								# "(07) AUC = 0"
								aucAmountB += 0
								aucAmountC += 0
								
							elif int(t1) < int(tUpper) <= int(t12): # Check for scenario (08)
								
								# Yes, scenario (08) applies
								# "(08) Integrate Eq. 2 from ", 0, " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t1)), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t1)), numberOfSegments)	
								
							elif int(tUpper) > int(t12): # Check for scenario (09)
								
								# Yes, scenario (09) applies
								# "(09a) Integrate Eq. 2 from ", 0, " to ", int(t2)
								# "(09b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], 0, int(t2), numberOfSegments)	
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], 0, int(t2), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
						elif int(t1) <= int(tLower):
							# No  scenarios (10) or (11) apply
							if int(t1) < int(tUpper) <= int(t12): # Check for scenario (10)
								
								# Yes, scenario (10) applies
								# "(10) Integrate Eq. 2 from ", int(tLower) - int(t1), " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)	
								
							elif int(tUpper) > int(t12): # Check for scenario (11)
								
								# Yes, scenario (11) applies
								# "(11a) Integrate Eq. 2 from ", int(tLower) - int(t1), " to ", int(t2)
								# "(11b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t2), numberOfSegments)	
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], 0, 0, fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t2), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
					elif t12Condition == "saturated_becoming_unsaturated":
						t12S = int(t1) + int(t12Saturated) # e.g., t12S = 160 min
						# Is tLower < t1?
						if int(tLower) < int(t1):
							# Yes - scenario (12), (13), (14) or (15) could apply
							if int(tUpper) <= int(t1): # Check for scenario (12)
								
								# Yes, scenario (12) applies
								# "(12) AUC = 0"
								aucAmountB += 0
								aucAmountC += 0
								
							elif int(t1) < int(tUpper) <= int(t12S): # Check for scenario (13)
								
								# Yes, scenario (13) applies
								# "(13) Integrate Eq. 1 from ", 0, " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t1)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t1)), numberOfSegments)
							
							elif int(t12S) < int(tUpper) <= int(t12): # Check for scenario (14)
								
								# Yes, scenario (14) applies
								# "(14a) Integrate Eq. 1 from ", 0, " to ", int(t12Saturated)
								# "(14b) Integrate Eq. 2 from ", 0, " to ", int(tUpper) - int(t12S)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12S)), numberOfSegments)					
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, int(t12Saturated), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12S)), numberOfSegments)	
							
							elif int(tUpper) > int(t12): # Check for scenario (15)
								
								# Yes, scenario (15) applies
								# "(15a) Integrate Eq. 1 from ", 0, " to ", int(t12Saturated)
								# "(15b) Integrate Eq. 2 from ", 0, " to ", int(t2) - int(t12Saturated)
								# "(15c) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								if int(t12Saturated) > 0:
									aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(t2) - int(t12Saturated)), numberOfSegments)					
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								if int(t12Saturated) > 0:
									aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], 0, int(t12Saturated), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(t2) - int(t12Saturated)), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
						elif int(t1) <= int(tLower) < int(t12S):
							# Yes, scenario (16), (17) or (18) could apply
							if int(tUpper) <= int(t12S): # Check for scenario (16)
								
								# Yes, scenario (16) applies
								# "(16) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)
								
							elif int(t12S) < int(tUpper) <= int(t12): # Check for scenario (17)
								
								# Yes, scenario (17) applies
								# "(17a) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(t12Saturated)
								# "(17b) Integrate Eq. 2 from ", 0, " to ", int(tUpper) - int(t12S)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12S)), numberOfSegments)					
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t12Saturated), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12S)), numberOfSegments)	
							
							elif int(tUpper) > int(t12): # Check for scenario (18)
								
								# Yes, scenario (18) applies
								# "(18a) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(t12Saturated)
								# "(18b) Integrate Eq. 2 from ", 0, " to ", int(t2) - int(t12Saturated)
								# "(18c) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(t2) - int(t12Saturated)), numberOfSegments)					
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dosingParametersAUC[dose][5], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t1)), int(t12Saturated), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], 0, (int(t2) - int(t12Saturated)), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
						elif int(t12S) <= int(tLower) < int(t12):
							# Yes, scenario (19) or (20) could apply
							if int(tUpper) <= int(t12): # Check for scenario (19)
								
								# Yes, scenario (19) applies
								# "(19) Integrate Eq. 2 from ", int(tLower) - int(t12S), " to ", int(tUpper) - int(t12S)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t12S)), (int(tUpper) - int(t12S)), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], (int(tLower) - int(t12S)), (int(tUpper) - int(t12S)), numberOfSegments)	
								
							elif int(tUpper) > int(t12): # Check for scenario (20)
								
								# Yes, scenario (17) applies
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], (int(Lower) - int(t12S)), int(t2), numberOfSegments)	
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], dosingParametersAUC[dose][7], fh, k1, k2, k3, k4, alpha, beta], (int(Lower) - int(t12S)), int(t2), numberOfSegments)	
								aucAmountC += areaUnderCurve.integrateAUC(self.amountC_3, [dosingParametersAUC[dose][8], dosingParametersAUC[dose][9], k1, k2, k3, k4, alpha, beta], 0, (int(tUpper) - int(t12)), numberOfSegments)
						
			# Return output
			return aucAmountB, aucAmountC
			
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)


	# Amount in B at t: absorption under saturated conditions and elimination
	def amountB_1(self, t, constants):
		try:
			import math
			
			a0 = constants[0]
			fh = constants[1]
			k1 = constants[2]
			k2 = constants[3]
			k3 = constants[4]
			k4 = constants[5]
			alpha = constants[6]
			beta = constants[7]
			
			a = float(fh) * float(a0) * float(k1)
			b = float(k3) / (float(alpha) * float(beta))
			c = ((float(k3) - float(alpha)) * math.exp(-1 * float(alpha) * float(t))) / (float(alpha) * (float(beta) - float(alpha)))
			d = ((float(k3) - float(beta)) * math.exp(-1 * float(beta) * float(t))) / (float(beta) * (float(beta) - float(alpha)))
			
			bt = float(a) * (float(b) - float(c) + float(d))
									
			# Return output
			return bt

		except ZeroDivisionError:
			print("\t\tZero division error: amountB_1, t = " + str(t))
			return 0		
			
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)


	# Amount in C at t: absorption under saturated conditions and elimination
	def amountC_1(self, t, constants):
		try:
			import math

			a0 = constants[0]
			fh = constants[1]
			k1 = constants[2]
			k2 = constants[3]
			k3 = constants[4]
			k4 = constants[5]
			alpha = constants[6]
			beta = constants[7]

			a = float(fh) * float(a0) * float(k1) * float(k2)			
			b = 1 / (float(alpha) * float(beta))
			c = math.exp(-1 * float(alpha) * float(t)) / (float(alpha) * (float(beta) - float(alpha)))
			d = math.exp(-1 * float(beta) * float(t)) / (float(beta) * (float(beta) - float(alpha)))
			
			ct = float(a) * (float(b) - float(c) + float(d))
									
			# Return output
			return ct

		except ZeroDivisionError:
			print("\t\tZero division error: amountC_1, t = " + str(t))
			return 0		
			
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)
			

	# Amount in B at t: absorption under unsaturated conditions and elimination
	def amountB_2(self, t, constants):
		try:
			import math
			
			a0 = constants[0]
			b0 = constants[1]
			c0 = constants[2]
			fh = constants[3]
			k1 = constants[4]
			k2 = constants[5]
			k3 = constants[6]
			k4 = constants[7]
			alpha = constants[8]
			beta = constants[9]
			
			a = float(fh) * float(k1) * float(a0)
			b = ((float(k3) - float(k1)) * math.exp(-1 * float(k1) * float(t))) / ((float(alpha) - float(k1)) * (float(beta) - float(k1)))
			c = ((float(k3) - float(alpha)) * math.exp(-1 * float(alpha) * float(t))) / ((float(alpha) - float(k1)) * (float(beta) - float(alpha)))
			d = ((float(k3) - float(beta)) * math.exp(-1 * float(beta) * float(t))) / ((float(beta) - float(k1)) * (float(beta) - float(alpha)))
			e = float(b0) / (float(beta) - float(alpha))
			f = (float(k3) - float(alpha)) * math.exp(-1 * float(alpha) * float(t)) 
			g = (float(k3) - float(beta)) * math.exp(-1 * float(beta) * float(t))
			h = (float(k3) * float(c0)) / (float(beta) - float(alpha))
			i = math.exp(-1 * float(alpha) * float(t)) - math.exp(-1 * float(beta) * float(t))
			
			bt = (float(a) * (float(b) - float(c) + float(d))) + (float(e) * (float(f) - float(g))) + (float(h) * float(i))
									
			# Return output
			return bt

		except ZeroDivisionError:
			print("\t\tZero division error: amountB_2, t = " + str(t))
			return 0		
		
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)
			

	# Amount in C at t: absorption under unsaturated conditions and elimination
	def amountC_2(self, t, constants):
		try:
			import math
			
			a0 = constants[0]
			b0 = constants[1]
			c0 = constants[2]
			fh = constants[3]
			k1 = constants[4]
			k2 = constants[5]
			k3 = constants[6]
			k4 = constants[7]
			alpha = constants[8]
			beta = constants[9]
			
			a = (float(k2) * float(b0)) / (float(beta) - float(alpha))
			b = math.exp(-1 * float(alpha) * float(t)) - math.exp(-1 * float(beta) * float(t))
			c = float(c0) * math.exp(-1 * float(k3) * float(t))
			d = float(k2) * float(k3) * float(c0)
			e = ((float(beta) - float(alpha)) * math.exp(-1 * float(k3) * float(t))) + ((float(k3) - float(beta)) * math.exp(-1 * float(alpha) * float(t))) + ((float(alpha) - float(k3)) * math.exp(-1 * float(beta) * float(t)))
			f = (float(alpha) - float(k3)) * (float(beta) - float(alpha)) * (float(k3) - float(beta))
			g = float(fh) * float(k1) * float(k2) * float(a0)
			h = ((float(beta) - float(alpha)) * math.exp(-1 * float(k1) * float(t))) + ((float(k1) - float(beta)) * math.exp(-1 * float(alpha) * float(t))) + ((float(alpha) - float(k1)) * math.exp(-1 * float(beta) * float(t)))
			i = (float(alpha) - float(k1)) * (float(beta) - float(alpha)) * (float(k1) - float(beta))
			
			ct = (float(a) * float(b)) + float(c) - (float(d) * (float(e) / float(f))) - (float(g) * (float(h) / float(i)))
									
			# Return output
			return ct

		except ZeroDivisionError:
			print("\t\tZero division error: amountC_2, t = " + str(t))
			return 0
		
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)


	# Amount in B at t: no absorption just elimination
	def amountB_3(self, t, constants):
		try:
			import math
			
			b0 = constants[0]
			c0 = constants[1]
			k1 = constants[2]
			k2 = constants[3]
			k3 = constants[4]
			k4 = constants[5]
			alpha = constants[6]
			beta = constants[7]
			
			a = (float(k3) * float(c0)) / (float(beta) - float(alpha))
			b = math.exp(-1 * float(alpha) * float(t)) - math.exp(-1 * float(beta) * float(t))
			c = float(b0) / (float(beta) - float(alpha))
			d = (float(k3) - float(alpha)) * math.exp(-1 * float(alpha) * float(t))
			e = (float(k3) - float(beta)) * math.exp(-1 * float(beta) * float(t))
				
			bt = (float(a) * float(b)) + (float(c) * (float(d) - float(e)))
									
			# Return output
			return bt

		except ZeroDivisionError:
			print("\t\tZero division error: amountB_3, t = " + str(t))
			return 0		
			
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)


	# Amount in C at t: no absorption just elimination
	def amountC_3(self, t, constants):
		try:
			import math
			
			b0 = constants[0]
			c0 = constants[1]
			k1 = constants[2]
			k2 = constants[3]
			k3 = constants[4]
			k4 = constants[5]
			alpha = constants[6]
			beta = constants[7]
			
			a = float(c0) * math.exp(-1 * float(k3) * float(t))
			b = (float(k2) * float(b0)) / (float(beta) - float(alpha))
			c = math.exp(-1 * float(alpha) * float(t)) - math.exp(-1 * float(beta) * float(t))
			d = float(k2) * float(k3) * float(c0)
			e = ((float(beta) - float(alpha)) * math.exp(-1 * float(k3) * float(t))) + ((float(k3) - float(beta)) * math.exp(-1 * float(alpha) * float(t))) + ((float(alpha) - float(k3)) * math.exp(-1 * float(beta) * float(t)))
			f = (float(alpha) - float(k3)) * (float(beta) - float(alpha)) * (float(k3) - float(beta))
			
			ct = float(a) + (float(b) * float(c)) - (float(d) * (float(e) / float(f)))
						
			# Return output
			return ct

		except ZeroDivisionError:
			print("\t\tZero division error: amountC_3, t = " + str(t))
			return 0
			
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting...\n")
			raise sys.exit(0)

