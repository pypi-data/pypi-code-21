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

description = "The insilicolynxdqi.calculations folder po_1c_free.py module"

class Po1CFree:	
	# Class variables


	# __init__
	def __init__(self):
		pass
		

	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi Po1CFree class"
		
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
			# Column header suffix text
			columnHeaderSuffix = []		
			for i in range(1):
				columnHeaderSuffix.append("")
			
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
					midConcentrationBValues = {}
					aucConcentrationBValues ={}
					
					#
					# Set calculation variables for system A -> B -> D:
					# A is drug in small intestines, B is drug in body and D is the drug eliminated from B
					# Assume first-order rate constant for both absorption (i.e., A -> B) and elimination (i.e., B -> D)
					# First dose occurs at t=0 and then at regular intervals (i.e., equivalent to t=3) until the end of the simulation (i.e., t=4)
					# Assume a time delay before absorption can occur (i.e., from t=0 to t=1)
					# Absorption can only occur over a particular time window under saturated and / or unsaturated conditions (i.e., from t=1 to t=2)
					# After which further absorption from a particular dose is ignored upto the end of the simulation (i.e., from t=2 to t=4)
					# Saturated conditions occur when the amount of drug in A exceeds solubility_6p5 (mg mL-1) x (small) intestinal fluid volume (mL)
					# Assume instant dispersion and dissolution of drug in the (small) intestinal fluid volume such that rate under saturated conditions is solubility6P5Saturated x k1
					# Once the amount of drug in A drops to solubility6P5Saturated assume first-order rate (i.e., solubility6P5Saturated x exp(-1 x k1 x t))
					# Drug entering B is assumed to undergo instanteous distribution between plasma and all tissues
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
															
					# Set cl, vss and k4 (cl returned with units of L min-1, vss returned with units of L and k4 returned with units of min-1)
					cl, vss, k4 = commonMethods.setK4Rate(row[settings["clText"] + settings["speciesName"]], row[settings["clText"] + settings["speciesName"] + settings["unitsSuffix"]], row[settings["vssText"] + settings["speciesName"]], row[settings["vssText"] + settings["speciesName"] + settings["unitsSuffix"]], settings)

					# First pass hepatic clearance fraction limit (cl has units of L min-1)
					fh = commonMethods.setFh(cl, settings)
					
					# Add to list of names
					allNames.append(row[settings["name"]])
					
					# Loop through doses
					extrapolatedData = {}
					for dose in settings["doses"]:
						# Calculate levels
						amountBVector, t12Condition, t12Saturated, bt12Saturated, bt2, dosingParametersAUC = self.po1CFree(doseTimes, timeVector, dose, vss, k4, solubility6P5Saturated, fh, k1, t0, t1, t2, t3, t4)			
						
						# Calculate AUC during a chosen time interval	
						aucAmountB = self.calculateAUC(timesAUC, dose, vss, k4, settings["numberOfSegments"], fh, k1, dosingParametersAUC)		
						
						# Create concentrationBVector list which is an elementwise division of amountBVector by vss
						concentrationBVector = [x / float(vss) for x in amountBVector] 		
									
						if settings["saveRawDataFiles"] == "yes":
							# Add raw parameter details
							rawValues = commonMethods.addRawParameters1C(settings, [cl, vss, k4, t1, t2, t3, t4, fh, solubility6P5Saturated, k1, t12Condition, t12Saturated, bt12Saturated, bt2])
							rawDataFile = settings["pathSubSubSub1"] + row[settings["name"]] + "_" + str(dose).replace(".","p") + columnHeaderSuffix[0] + settings["textExtension"]
							csvTools.exportThreeListsToCSV(rawDataFile, timeVector, amountBVector, concentrationBVector, rawValues, settings["csvFileColumnHeaderTimeText"], settings["csvFileColumnHeaderAmountText"], 
							settings["csvFileColumnHeaderConcentrationText"], settings["csvFileColumnHeaderRawParameterText"], settings["csvFileColumnHeaderRawParameterValueText"])
						
						# Determine maximum and minimum values
						maxAmountBValue, minAmountBValue = commonMethods.extremeValues(timeVector, t1, amountBVector, doseTimes)
						maxConcentrationBValue, minConcentrationBValue = commonMethods.extremeValues(timeVector, t1, concentrationBVector, doseTimes)							
						
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
						aucConcentrationBValues.update({dose:(float(aucAmountB) / float(vss)) * float(fu)})
						
					# Export maximum, minimum and middle amount data from three dictionaries that share the same keys to CSV file
					rawDataFile = settings["pathSubSubSub2"] + row[settings["name"]] + columnHeaderSuffix[0] + settings["textExtension"]
					csvTools.exportThreeDictionariesToCSV(rawDataFile, maxAmountBValues, minAmountBValues, midAmountBValues, settings, "amounts")
					
					# Export maximum, minimum and middle concentration data from three dictionaries that share the same keys to CSV file
					rawDataFile = settings["pathSubSubSub3"] + row[settings["name"]] + columnHeaderSuffix[0] + settings["textExtension"]
					csvTools.exportThreeDictionariesToCSV(rawDataFile, maxConcentrationBValues, minConcentrationBValues, midConcentrationBValues, settings, "concentrations")
					
					# Export aucAmountBValues and aucConcentrationBValues data from two dictionaries that share the same keys to CSV file
					rawDataFile = settings["pathSubSubSub4"] + row[settings["name"]] + columnHeaderSuffix[0] + settings["textExtension"]
					csvTools.exportAucDictionariesToCSV(rawDataFile, aucAmountBValues, aucConcentrationBValues, "", "", settings)
		
					if settings["compartment"] == "plasma":
						# Perform analysis using "dose" ~ "amount_B_max" and "dose" ~ "amount_B_min" data and return dictionary
						extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxAmountBValues, minAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[0])

						# Perform analysis using "dose" ~ "amount_B_mid" data and return dictionary
						extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midAmountBValues, settings["amountBPrefix"], columnHeaderSuffix[0])
						
						# Perform analysis using "dose" ~ "auc_amount_B" data and return dictionary
						extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucAmountBValues, settings["aucAmountBPrefix"], columnHeaderSuffix[0])
																					
						# Perform analysis using "dose" ~ "concentration_B_max" and "dose" ~ "concentration_B_min" data and return dictionary
						extrapolatedData = analysis.analyseDoseQuantityDictionaries(extrapolatedData, maxConcentrationBValues, minConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[0])
					
						# Perform analysis using "dose" ~ "concentration_B_mid" data and return dictionary
						extrapolatedData = analysis.analyseDoseMidQuantityDictionary(extrapolatedData, midConcentrationBValues, settings["concentrationBPrefix"], columnHeaderSuffix[0])
					
						# Perform analysis using "dose" ~ "auc_concentration_B" data and return dictionary
						extrapolatedData = analysis.analyseDoseAucDictionary(extrapolatedData, aucConcentrationBValues, settings["aucConcentrationBPrefix"], columnHeaderSuffix[0])
								
					# Add additional parameters to the dictionary of values
					values1 = commonMethods.addParameters1C(settings, [molecularWeight, k4, t1, t2, t3, t4, fh], extrapolatedData, columnHeaderSuffix[0])
			
					# Define filepath to save data
					dataFile1 = settings["pathSubSub1"] + settings["methodName"] + "_" + settings["summaryFileName"] + columnHeaderSuffix[0] + settings["textExtension"]
					
					# Update data	
					allValues1.update({row[settings["name"]]:values1})
				
			# Export all the information within the "allValues" dictionary to CSV file		
			csvTools.exportValuesToCSV(dataFile1, allNames, allValues1)
			
			# Return output
			return allNames, allValues1, columnHeaderSuffix	
			
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


	# Po 1C free levels
	def po1CFree(self, doseTimes, timeVector, dose, vss, k4, solubility6P5Saturated, fh, k1, t0, t1, t2, t3, t4):
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
					bt12Saturated = self.amountB_1(t2, [a0, fh, k1, k4])
				else:
					t12Condition = "saturated_becoming_unsaturated"
					#
					# Calculate the amount of drug in B at the transition point between saturated and unsaturated conditions
					# Apply self.amountB_1 where the starting conditions for A0 = solubility6P5Saturated and B0 = 0 
					# bt12Saturated will equal the amount in B at the end of the saturation period
					#
					a0 = solubility6P5Saturated
					bt12Saturated = self.amountB_1(t12Saturated, [a0, fh, k1, k4])
			else:
				# Unsaturated conditions apply at t1
				t12Saturated = 0
				t12Condition = "unsaturated"
				a0 = dose
				bt12Saturated = 0
			
			#
			# Use principle of superposition - separately calculate amount in B for each dose from its time of dosing up to the end of the simulation and then combine all the amounts for a given time point  
			#
			amountBVector = [0 for x in range(0, len(timeVector))]
			dosingParametersAUC = {}
			bt2 = 0
			for doseTime in doseTimes:
				for timeVectorIndex, t in enumerate(timeVector):
					if doseTime <= t:
						timeToUse = t - doseTime
						if timeToUse < t1:
							#
							# Amount t=0 to t=1
							# Nothing of the dose in B throughout due to absorption delay
							#
							tAmountB = 0
							
						if t1 <= timeToUse <= (t2 + t1):
							#
							# Amount t=1 to t=2
							# Absorption period - absorption (under saturated and unsaturated conditions) and elimination
							# 
							if t12Condition == "saturated":
								#
								# Rate of absorption under saturated conditions
								# Apply self.amountB_1 and reset the time - use timeToUseAdjusted = timeToUse - t1
								# The amount in A = solubility6P5Saturated throughout
								# Nothing of the dose in B at timeToUseAdjusted = 0 
								#
								timeToUseAdjusted = timeToUse - t1
								tAmountB = self.amountB_1(timeToUseAdjusted, [a0, fh, k1, k4])
								if timeToUse == (t1 + t2):
									bt2 = tAmountB			
							
							elif t12Condition == "saturated_becoming_unsaturated":
								#
								# Rate of absorption initially under saturated and then unsaturated conditions
								# Apply self.amountB_1 and reset the time - use timeToUseAdjusted = timeToUse - t1
								# While timeToUseAdjusted < t12Saturated, saturated conditions apply
								# The amount in A = solubility6P5Saturated throughout
								# Nothing of the dose in B at timeToUseAdjusted = 0 
								# When timeToUseAdjusted >= t12Saturated, unsaturated conditions apply
								# Apply self.amountB_2 resetting the time again - use timeToUseAdjustedAgain = timeToUseAdjusted - t12Saturated
								# The amount in A at the start = solubility6P5Saturated
								# The amount in B at the start = bt12Saturated
								#
								timeToUseAdjusted = timeToUse - t1
								if timeToUseAdjusted < t12Saturated:
									tAmountB = self.amountB_1(timeToUseAdjusted, [a0, fh, k1, k4])
								elif timeToUseAdjusted >= t12Saturated:
									timeToUseAdjustedAgain = timeToUseAdjusted - t12Saturated
									b0 = bt12Saturated 
									tAmountB = self.amountB_2(timeToUseAdjustedAgain, [a0, b0, fh, k1, k4])
								if timeToUse == (t1 + t2):
									bt2 = tAmountB
								
							elif t12Condition == "unsaturated":
								#
								# Rate of absorption under unsaturated conditions
								# Use timeToUseAdjusted = timeToUse - t1
								# At timeToUseAdjusted = 0, the amount in A (i.e., A0) = dose
								# Nothing of the dose in B at timeToUseAdjusted = 0 
								#
								timeToUseAdjusted = timeToUse - t1
								b0 = 0
								tAmountB = self.amountB_2(timeToUseAdjusted, [a0, b0, fh, k1, k4])
								if timeToUse == (t1 + t2):
									bt2 = tAmountB
											
						if (t2 + t1) < timeToUse:
							#
							# Amount t=2 to t=4
							# No absorption just elimination
							# Use timeToUseAdjusted = timeToUse - t2
							# At timeToUseAdjusted = 0, the amount in B (i.e., B0) = B(t=2)
							#
							timeToUseAdjusted = timeToUse - (t2 + t1)		
							b0 = bt2
							tAmountB = self.amountB_3(timeToUseAdjusted, [b0, k4])
							
						amountBVector[timeVectorIndex] += tAmountB
			
			dosingParametersAUC.update({dose:[t12Condition, t0, t1, t2, t12Saturated, a0, bt12Saturated, bt2]})			
				
			# Return output
			return amountBVector, t12Condition, t12Saturated, bt12Saturated, bt2, dosingParametersAUC		
			
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
	def calculateAUC(self, timesAUC, dose, vss, k4, numberOfSegments, fh, k1, dosingParametersAUC):
		try:
			from insilicolynxdqi.system.area_under_curve import AreaUnderCurve
			areaUnderCurve = AreaUnderCurve()
			
			# timesAUC{dosingIntervalsToConsider:[lowerTime, upperTime]} - multiple doses in dictionary
			# dosingParametersAUC{dose:[t12Condition, t0, t1, t2, t12Saturated, a0, bt12Saturated, bt2]} - only 1 dose returned as a list within a dictionary
			
			aucAmountB = 0
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
					aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], (int(tLower) - int(t12)), (int(tUpper) - int(t12)), numberOfSegments)
				
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
							
							elif int(t1) < int(tUpper) <= int(t12): # Check for scenario (03)
								
								# Yes, scenario (03) applies
								# "(03) Integrate Eq. 1 from ", 0, " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], 0, (int(tUpper) - int(t1)), numberOfSegments)
							
							elif int(tUpper) > int(t12): # Check for scenario (04)
								
								# Yes, scenario (04) applies
								# "(04a) Integrate Eq. 1 from ", 0, " to ", int(t2)
								# "(04b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], 0, int(t2), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], 0, (int(tUpper) - int(t12)), numberOfSegments)
						
						elif int(t1) <= int(tLower):
							# No  scenarios (05) or (06) apply
							if int(t1) < int(tUpper) <= int(t12): # Check for scenario (05)
								
								# Yes, scenario (05) applies
								# "(05) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4] , (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)
							
							elif int(tUpper) > int(t12): # Check for scenario (06)
								
								# Yes, scenario (06) applies
								# "(06a) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(t2)
								# "(06b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], (int(tLower) - int(t1)), int(t2), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], 0, (int(tUpper) - int(t12)), numberOfSegments)
						
					elif t12Condition == "unsaturated":
						# Is tLower < t1?
						if int(tLower) < int(t1):
							# Yes - scenario (07), (08) or (09) could apply
							if int(tUpper) <= int(t1): # Check for scenario (07)
								
								# Yes, scenario (07) applies
								# "(07) AUC = 0"
								aucAmountB += 0
								
							elif int(t1) < int(tUpper) <= int(t12): # Check for scenario (08)
								
								# Yes, scenario (08) applies
								# "(08) Integrate Eq. 2 from ", 0, " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, fh, k1, k4], 0, (int(tUpper) - int(t1)), numberOfSegments)	
								
							elif int(tUpper) > int(t12): # Check for scenario (09)
								
								# Yes, scenario (09) applies
								# "(09a) Integrate Eq. 2 from ", 0, " to ", int(t2)
								# "(09b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, fh, k1, k4], 0, int(t2), numberOfSegments)	
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
						elif int(t1) <= int(tLower):
							# No  scenarios (10) or (11) apply
							if int(t1) < int(tUpper) <= int(t12): # Check for scenario (10)
								
								# Yes, scenario (10) applies
								# "(10) Integrate Eq. 2 from ", int(tLower) - int(t1), " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, fh, k1, k4], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)	
								
							elif int(tUpper) > int(t12): # Check for scenario (11)
								
								# Yes, scenario (11) applies
								# "(11a) Integrate Eq. 2 from ", int(tLower) - int(t1), " to ", int(t2)
								# "(11b) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], 0, fh, k1, k4], (int(tLower) - int(t1)), int(t2), numberOfSegments)	
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
					elif t12Condition == "saturated_becoming_unsaturated":
						t12S = int(t1) + int(t12Saturated) # e.g., t12S = 160 min
						# Is tLower < t1?
						if int(tLower) < int(t1):
							# Yes - scenario (12), (13), (14) or (15) could apply
							if int(tUpper) <= int(t1): # Check for scenario (12)
								
								# Yes, scenario (12) applies
								# "(12) AUC = 0"
								aucAmountB += 0
								
							elif int(t1) < int(tUpper) <= int(t12S): # Check for scenario (13)
								
								# Yes, scenario (13) applies
								# "(13) Integrate Eq. 1 from ", 0, " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], 0, (int(tUpper) - int(t1)), numberOfSegments)
							
							elif int(t12S) < int(tUpper) <= int(t12): # Check for scenario (14)
								
								# Yes, scenario (14) applies
								# "(14a) Integrate Eq. 1 from ", 0, " to ", int(t12Saturated)
								# "(14b) Integrate Eq. 2 from ", 0, " to ", int(tUpper) - int(t12S)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], 0, int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], fh, k1, k4], 0, (int(tUpper) - int(t12S)), numberOfSegments)					
							
							elif int(tUpper) > int(t12): # Check for scenario (15)
								
								# Yes, scenario (15) applies
								# "(15a) Integrate Eq. 1 from ", 0, " to ", int(t12Saturated)
								# "(15b) Integrate Eq. 2 from ", 0, " to ", int(t2) - int(t12Saturated)
								# "(15c) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								if int(t12Saturated) > 0:
									aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], 0, int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], fh, k1, k4], 0, (int(t2) - int(t12Saturated)), numberOfSegments)					
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
						elif int(t1) <= int(tLower) < int(t12S):
							# Yes, scenario (16), (17) or (18) could apply
							if int(tUpper) <= int(t12S): # Check for scenario (16)
								
								# Yes, scenario (16) applies
								# "(16) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(tUpper) - int(t1)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], (int(tLower) - int(t1)), (int(tUpper) - int(t1)), numberOfSegments)
								
							elif int(t12S) < int(tUpper) <= int(t12): # Check for scenario (17)
								
								# Yes, scenario (17) applies
								# "(17a) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(t12Saturated)
								# "(17b) Integrate Eq. 2 from ", 0, " to ", int(tUpper) - int(t12S)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], (int(tLower) - int(t1)), int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], fh, k1, k4], 0, (int(tUpper) - int(t12S)), numberOfSegments)					
							
							elif int(tUpper) > int(t12): # Check for scenario (18)
								
								# Yes, scenario (18) applies
								# "(18a) Integrate Eq. 1 from ", int(tLower) - int(t1), " to ", int(t12Saturated)
								# "(18b) Integrate Eq. 2 from ", 0, " to ", int(t2) - int(t12Saturated)
								# "(18c) Integrate Eq. 3 from ", 0, " to ", int(tUpper) - int(t12)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_1, [dosingParametersAUC[dose][5], fh, k1, k4], (int(tLower) - int(t1)), int(t12Saturated), numberOfSegments)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], fh, k1, k4], 0, (int(t2) - int(t12Saturated)), numberOfSegments)					
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], 0, (int(tUpper) - int(t12)), numberOfSegments)
								
						elif int(t12S) <= int(tLower) < int(t12):
							# Yes, scenario (19) or (20) could apply
							if int(tUpper) <= int(t12): # Check for scenario (19)
								
								# Yes, scenario (19) applies
								# "(19) Integrate Eq. 2 from ", int(tLower) - int(t12S), " to ", int(tUpper) - int(t12S)
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], fh, k1, k4], (int(tLower) - int(t12S)), (int(tUpper) - int(t12S)), numberOfSegments)	
								
							elif int(tUpper) > int(t12): # Check for scenario (20)
								
								# Yes, scenario (17) applies
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_2, [dosingParametersAUC[dose][5], dosingParametersAUC[dose][6], fh, k1, k4], (int(Lower) - int(t12S)), int(t2), numberOfSegments)	
								aucAmountB += areaUnderCurve.integrateAUC(self.amountB_3, [dosingParametersAUC[dose][7], k4], 0, (int(tUpper) - int(t12)), numberOfSegments)
	
			# Return output
			return aucAmountB
			
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
			k4 = constants[3]
			
			a = (float(a0) * float(k1) * float(fh)) / float(k4)
			b = 1 - math.exp(-1 * float(k4) * float(t))
			
			bt = float(a) * float(b)
			
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


	# Amount in B at t: absorption under unsaturated conditions and elimination
	def amountB_2(self, t, constants):
		try:
			import math
			
			a0 = constants[0]
			b0 = constants[1]
			fh = constants[2]
			k1 = constants[3]
			k4 = constants[4]
			
			a = (float(a0) * float(k1) * float(fh)) / (float(k4) - float(k1)) 
			b = math.exp(-1 * float(k1) * float(t)) - math.exp(-1 * float(k4) * float(t))
			c = float(b0) * math.exp(-1 * float(k4) * float(t))
					
			bt = (float(a) * float(b)) + float(c)
			
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
			

	# Amount in B at t: no absorption just elimination
	def amountB_3(self, t, constants):
		try:
			import math
			
			b0 = constants[0]
			k4 = constants[1]
			
			a = float(b0)
			b = math.exp(-1 * float(k4) * float(t))
			
			bt = float(a) * float(b)
				
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

