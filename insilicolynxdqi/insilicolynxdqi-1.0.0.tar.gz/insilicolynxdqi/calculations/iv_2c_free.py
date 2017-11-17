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

description = "The insilicolynxdqi.calculations folder iv_2c_free.py module"

class Iv2CFree:
	# Class variables


	# __init__
	def __init__(self):
		pass
	
	
	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi Iv2CFree class"
		
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
				

	# Process file
	def processFile(self, settings):
		try:
			import csv
			import math
			from insilicolynxdqi.system.analysis import Analysis
			from insilicolynxdqi.system.common_methods import CommonMethods
			from insilicolynxdqi.system.csv_tools import CsvTools
			analysis = Analysis(settings)
			commonMethods = CommonMethods()
			csvTools = CsvTools(None)

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
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.
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
					midConcentrationBValues = {}
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
					# Set calculation variables for system B (= C) -> D:
					# B and C are drug in central and peripheral compartments of the body, respectively, and D is the drug eliminated from B
					# Assume first-order rate constant for distribution (i.e., B -> C and C -> B) and elimination (i.e., B -> D)
					# First dose occurs at t=0 and than at regular intervals (i.e., equivalent to t=3) until the end of the simulation (i.e., t=4)
					# Scale to minute scale and dose is in mg
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
					
					# Determine times (times returned with units of min)
					t0 = 0
					t1 = 0
					t2 = 0
					t3, t4 = commonMethods.setT3T4(row, settings)
					doseTimes, timeVector, timesAUC = commonMethods.createTimeVector(t1, t2, t3, t4, settings)
					
					# Set cl, v and rates (cl returned with units of L min-1, v returned with units of L and rates returned with units of min-1)
					cl, vss, vcentralList, k2K3RatioList, k2Rates, k3Rates, k4Rates, vterminalList = commonMethods.setK2K3K4Rates(row[settings["clText"] + settings["speciesName"]], row[settings["clText"] + settings["speciesName"] + settings["unitsSuffix"]], row[settings["vssText"] + settings["speciesName"]], row[settings["vssText"] + settings["speciesName"] + settings["unitsSuffix"]], settings) 
					
					# Add to list of names
					allNames.append(row[settings["name"]])
					
					# Loop through the scenarios
					for index in range(0, 5):
						extrapolatedData = {}
						for dose in settings["dose"]:
							# Determine alpha and beta values bases on k2, k3 and k4 values
							alpha, beta = commonMethods.setAlphaBeta(k2Rates[index], k3Rates[index], k4Rates[index])
							
							# Calculate levels
							amountBVector, amountCVector, amountBCVector = self.iv2CFree(doseTimes, timeVector, dose, k2Rates[index], k3Rates[index], k4Rates[index], alpha, beta)			
							
							# Calculate AUC during a chosen time interval	
							aucAmountB, aucAmountC = self.iv2CFreeAUC(timesAUC, dose, k2Rates[index], k3Rates[index], k4Rates[index], alpha, beta, settings["numberOfSegments"])
							
							# Create concentrationBVector list which is an elementwise division of amountBVector by vcentral
							concentrationBVector = [x / float(vcentralList[index]) for x in amountBVector] 
							
							if settings["saveRawDataFiles"] == "yes":
								# Add raw parameter details
								rawValues = commonMethods.addRawParameters2C(settings, [cl, vss, vcentralList[index], k2Rates[index], k3Rates[index], k4Rates[index], vterminalList[index], alpha, beta, t3, t4])
								rawDataFile = settings["pathSubSubSub1"] + row[settings["name"]] + "_" + str(dose).replace(".","p") + columnHeaderSuffix[index] + settings["textExtension"]
								csvTools.exportFiveListsToCSV(rawDataFile, timeVector, amountBVector, concentrationBVector, amountCVector, amountBCVector, rawValues, settings["csvFileColumnHeaderTimeText"], 
								settings["csvFileColumnHeaderAmountCentralText"], settings["csvFileColumnHeaderConcentrationText"], settings["csvFileColumnHeaderAmountPeripheralText"], settings["csvFileColumnHeaderAmountText"], 
								settings["csvFileColumnHeaderRawParameterText"], settings["csvFileColumnHeaderRawParameterValueText"])
							
							# Determine maximum and minimum values
							maxAmountBValue, minAmountBValue = commonMethods.extremeValues(timeVector, t1, amountBVector, doseTimes)								
							maxConcentrationBValue, minConcentrationBValue = commonMethods.extremeValues(timeVector, t1, concentrationBVector, doseTimes)					
							maxAmountCValue, minAmountCValue = commonMethods.extremeValues(timeVector, t1, amountCVector, doseTimes)
							maxAmountBCValue, minAmountBCValue = commonMethods.extremeValues(timeVector, t1, amountBCVector, doseTimes)	
			
							# Add maximum, minimum, middle and auc values to dictionaries
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
							# Perform analyse using "dose" ~ "amount_B_max" and "dose" ~ "amount_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBValues, minAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analyse using "dose" ~ "amount_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analyse using "dose" ~ "auc_amount_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBValues, settings["aucAmountBPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "concentration_B_max" and "dose" ~ "concentration_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxConcentrationBValues, minConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])

							# Perform analyse using "dose" ~ "concentration_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "auc_concentration_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucConcentrationBValues, settings["aucConcentrationBPrefix"], columnHeaderSuffix[index])
						
						elif settings["compartment"] == "peripheral":
							# Perform analyse using "dose" ~ "amount_C_max" and "dose" ~ "amount_C_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountCValues, minAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
						
							# Perform analyse using "dose" ~ "amount_C_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "auc_amount_C" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountCValues, settings["aucAmountCPrefix"], columnHeaderSuffix[index])

						elif settings["compartment"] == "central_peripheral":
							# Perform analyse using "dose" ~ "amount_BC_max" and "dose" ~ "amount_BC_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBCValues, minAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
						
							# Perform analyse using "dose" ~ "amount_BC_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "auc_amount_BC" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBCValues, settings["aucAmountBCPrefix"], columnHeaderSuffix[index])
						
						elif settings["compartment"] == "all":
							# Perform analyse using "dose" ~ "amount_B_max" and "dose" ~ "amount_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBValues, minAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analyse using "dose" ~ "amount_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[index])

							# Perform analyse using "dose" ~ "auc_amount_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBValues, settings["aucAmountBPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "concentration_B_max" and "dose" ~ "concentration_B_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxConcentrationBValues, minConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])

							# Perform analyse using "dose" ~ "concentration_B_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "auc_concentration_B" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucConcentrationBValues, settings["aucConcentrationBPrefix"], columnHeaderSuffix[index])
						
							# Perform analyse using "dose" ~ "amount_C_max" and "dose" ~ "amount_C_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountCValues, minAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
						
							# Perform analyse using "dose" ~ "amount_C_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountCValues, settings["amountCPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "auc_amount_C" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountCValues, settings["aucAmountCPrefix"], columnHeaderSuffix[index])
						
							# Perform analyse using "dose" ~ "amount_BC_max" and "dose" ~ "amount_BC_min" data and return dictionary
							extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBCValues, minAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
						
							# Perform analyse using "dose" ~ "amount_BC_mid" data and return dictionary
							extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBCValues, settings["amountBCPrefix"], columnHeaderSuffix[index])
							
							# Perform analyse using "dose" ~ "auc_amount_BC" data and return dictionary
							extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBCValues, settings["aucAmountBCPrefix"], columnHeaderSuffix[index])
						
						if index == 0:
							# Add additional parameters to a dictionary of values
							values1 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t3, t4, settings["dose"][0]], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile1 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data	
							allValues1.update({row[settings["name"]]:values1})
						elif index == 1:
							# Add additional parameters to a dictionary of values
							values2 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t3, t4, settings["dose"][0]], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile2 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data
							allValues2.update({row[settings["name"]]:values2})
						elif index == 2:
							# Add additional parameters to a dictionary of values
							values3 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t3, t4, settings["dose"][0]], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile3 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data	
							allValues3.update({row[settings["name"]]:values3})
						elif index == 3:
							# Add additional parameters to a dictionary of values
							values4 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t3, t4, settings["dose"][0]], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile4 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data
							allValues4.update({row[settings["name"]]:values4})
						elif index == 4:
							# Add additional parameters to a dictionary of values
							values5 = commonMethods.addParameters2C(settings, [molecularWeight, k2Rates[index], k3Rates[index], k4Rates[index], t3, t4, settings["dose"][0]], extrapolatedData, columnHeaderSuffix[index])
							# Define filepath to save data
							dataFile5 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[index] + settings["textExtension"]
							# Update data
							allValues5.update({row[settings["name"]]:values5})
					
			# Export all the information within the allValues1, allValues2, allValues3, allValues4 and allValues5 dictionaries to CSV file		
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting.\n")
			raise sys.exit(0)	
		
		finally:
			fileToRead.close()
			
		
	# Iv 2C free levels
	def iv2CFree(self, doseTimes, timeVector, dose, k2, k3, k4, alpha, beta):   				  
		try:
			#
			# Use principle of superposition - separately calculate amount in B and C for each dose from its time of dosing up to the end of the simulation and then combine all the amounts for a given time point  
			#
			b0 = dose # c0 = 0 at t = 0
			amountBVector = [0 for x in range(0, len(timeVector))]
			amountCVector = [0 for x in range(0, len(timeVector))]
			for doseTime in doseTimes:
				for timeVectorIndex, t in enumerate(timeVector):
					if doseTime <= t:
						timeToUse = t - doseTime
						tAmountB = self.amountB_1(timeToUse, [b0, k2, k3, k4, alpha, beta])
						tAmountC = self.amountC_1(timeToUse, [b0, k2, k3, k4, alpha, beta])
						amountBVector[timeVectorIndex] += tAmountB
						amountCVector[timeVectorIndex] += tAmountC		
			
			# Create amountBCVector list which is an elementwise sum of amountBVector and amountCVector 
			amountBCVector = [sum(x) for x in zip(amountBVector, amountCVector)]
	
			# Return output
			return amountBVector, amountCVector, amountBCVector
					
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
			
		
	# Iv 2C free levels AUC
	def iv2CFreeAUC(self, timesAUC, dose, k2, k3, k4, alpha, beta, numberOfSegments):
		try:
			from insilicolynxdqi.system.area_under_curve import AreaUnderCurve
			areaUnderCurve = AreaUnderCurve()
			
			# timesAUC{dosingIntervalsToConsider:[lowerTime, upperTime]}
			aucAmountB = 0
			aucAmountC = 0
			for doseInterval in timesAUC:
				tLower = timesAUC[doseInterval][0]
				tUpper = timesAUC[doseInterval][1] # tUpper > tLower
				aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dose, k2, k3, k4, alpha, beta], int(tLower), int(tUpper), numberOfSegments)
				aucAmountC += areaUnderCurve.integrateAUC(self.amountC_1, [dose, k2, k3, k4, alpha, beta], int(tLower), int(tUpper), numberOfSegments)
	
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting.\n")
			raise sys.exit(0)


	# Amount in B at t
	def amountB_1(self, t, constants):
		try:
			import math
			
			b0 = constants[0]
			k2 = constants[1]
			k3 = constants[2]
			k4 = constants[3]
			alpha = constants[4]
			beta = constants[5]

			a = float(b0) / (float(beta) - float(alpha))
			b = (float(k3) - float(alpha)) * math.exp(-1 * float(alpha) * float(t))
			c = (float(k3) - float(beta)) * math.exp(-1 * float(beta) * float(t))
			
			bt = float(a) * (float(b) - float(c))
				
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting.\n")
			raise sys.exit(0)


	# Amount in C at t
	def amountC_1(self, t, constants):
		try:
			import math

			b0 = constants[0]
			k2 = constants[1]
			k3 = constants[2]
			k4 = constants[3]
			alpha = constants[4]
			beta = constants[5]
			
			a = (float(k2) * float(b0)) / (float(beta) - float(alpha))
			b = math.exp(-1 * float(alpha) * float(t))
			c = math.exp(-1 * float(beta) * float(t))
			
			ct = float(a) * (float(b) - float(c))
				
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
			print("Code object line number where error handled:\n\t" + errorHandlerLineNumber + "\nExiting.\n")
			raise sys.exit(0)		

