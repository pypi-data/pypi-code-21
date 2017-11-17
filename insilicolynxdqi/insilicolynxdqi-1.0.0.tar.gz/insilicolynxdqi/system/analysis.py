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

description = "The insilicolynxdqi.system folder analysis.py module"

class Analysis:
	# Class variables


	# __init__	
	def __init__(self, settings):
		try:
			self.IvOrPo = settings["ivOrPo"]
			self.QuantityAucText = settings["quantityAucText"]
			self.QuantityMaxText = settings["quantityMaxText"]
			self.QuantityMidText = settings["quantityMidText"]
			self.QuantityMinText = settings["quantityMinText"]
			self.Species = settings["speciesName"]
			
			if self.IvOrPo == "po":
				self.DoseAucText = settings["doseAucText"]
				self.DoseMaxText = settings["doseMaxText"]
				self.DoseMidText = settings["doseMidText"]
				self.DoseMinText = settings["doseMinText"]
				self.Doses = settings["doses"]			
				self.HighestLinearDoseAucText = settings["highestLinearDoseAucText"]
				self.HighestLinearDoseMaxText = settings["highestLinearDoseMaxText"]
				self.HighestLinearDoseMidText = settings["highestLinearDoseMidText"]
				self.HighestLinearDoseMinText = settings["highestLinearDoseMinText"]	
				self.InterceptAucText = settings["interceptAucText"]
				self.InterceptMaxText = settings["interceptMaxText"]
				self.InterceptMidText = settings["interceptMidText"]
				self.InterceptMinText = settings["interceptMinText"]
				self.IvDoseForQuantityCalculation = settings["defaultIvDose"]	
				self.LowestFlatRegionDoseAucText = settings["lowestFlatRegionDoseAucText"]
				self.LowestFlatRegionDoseMaxText = settings["lowestFlatRegionDoseMaxText"]
				self.LowestFlatRegionDoseMidText = settings["lowestFlatRegionDoseMidText"]	
				self.LowestFlatRegionDoseMinText = settings["lowestFlatRegionDoseMinText"]		
				self.MethodName = settings["methodName"]		
				self.R2AucText = settings["r2AucText"]
				self.R2MaxText = settings["r2MaxText"]
				self.R2MidText = settings["r2MidText"]
				self.R2MinText = settings["r2MinText"]	
				self.SlopeAucText = settings["slopeAucText"]
				self.SlopeMaxText = settings["slopeMaxText"]
				self.SlopeMidText = settings["slopeMidText"]
				self.SlopeMinText = settings["slopeMinText"]
				self.SpeciesBodyWeight = settings[settings["speciesName"] + settings["bodyWeightSuffix"]]
				
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


	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi Analysis class"
		
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


	# Analyse dose ~ quantity dictionaries
	def analyseDoseQuantityDictionaries(self, extrapolatedData, dictValuesRawMax, dictValuesRawMin, prefix, suffix):
		try:
			if self.IvOrPo == "iv":
				# Max quantity
				for key in dictValuesRawMax:			
					extrapolatedData.update({prefix + self.QuantityMaxText + self.Species + suffix:self.isFloat(dictValuesRawMax[key])})

				# Min quantity
				for key in dictValuesRawMin:
					extrapolatedData.update({prefix + self.QuantityMinText + self.Species + suffix:self.isFloat(dictValuesRawMin[key])})

			elif self.IvOrPo == "po":
				# Max quantity
				highestLinearDoseMax, lowestFlatRegionDoseMax, aMax, bMax, r2Max, quantityMax, doseMax = self.linearityDoseRangeAndDose(dictValuesRawMax)
				extrapolatedData.update({prefix + self.HighestLinearDoseMaxText + self.Species + suffix:self.isFloat(highestLinearDoseMax)})
				extrapolatedData.update({prefix + self.LowestFlatRegionDoseMaxText + self.Species + suffix:self.isFloat(lowestFlatRegionDoseMax)})
				extrapolatedData.update({prefix + self.InterceptMaxText + self.Species + suffix:self.isFloat(aMax)})
				extrapolatedData.update({prefix + self.SlopeMaxText + self.Species + suffix:self.isFloat(bMax)})
				extrapolatedData.update({prefix + self.R2MaxText + self.Species + suffix:self.isFloat(r2Max)})
				extrapolatedData.update({prefix + self.QuantityMaxText + self.Species + suffix:self.isFloat(quantityMax)})
				extrapolatedData.update({prefix + self.DoseMaxText + self.Species + suffix:self.isFloat(doseMax)})

				# Min quantity
				highestLinearDoseMin, lowestFlatRegionDoseMin, aMin, bMin, r2Min, quantityMin, doseMin = self.linearityDoseRangeAndDose(dictValuesRawMin)
				extrapolatedData.update({prefix + self.HighestLinearDoseMinText + self.Species + suffix:self.isFloat(highestLinearDoseMin)})
				extrapolatedData.update({prefix + self.LowestFlatRegionDoseMinText + self.Species + suffix:self.isFloat(lowestFlatRegionDoseMin)})			
				extrapolatedData.update({prefix + self.InterceptMinText + self.Species + suffix:self.isFloat(aMin)})
				extrapolatedData.update({prefix + self.SlopeMinText + self.Species + suffix:self.isFloat(bMin)})
				extrapolatedData.update({prefix + self.R2MinText + self.Species + suffix:self.isFloat(r2Min)})
				extrapolatedData.update({prefix + self.QuantityMinText + self.Species + suffix:self.isFloat(quantityMin)})
				extrapolatedData.update({prefix + self.DoseMinText + self.Species + suffix:self.isFloat(doseMin)})
						
			# Return output
			return extrapolatedData		

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


	# Is float
	def isFloat(self, value):
		try:
			float(value)
			if (value == 'nan') or (value == 'inf') or (value * -1 == 'inf'):
				return 'nan'
			else:
				return float(value)
			
		except ValueError:
			return 'nan'
			
		except TypeError:
			return 'nan'

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


	# Analyse dose ~ mid quantity dictionary - convert to log10 scale
	def analyseDoseMidQuantityDictionary(self, extrapolatedData, dictValuesRawMid, prefix, suffix):
		try:
			if self.IvOrPo == "iv":
				# Mid quantity
				for key in dictValuesRawMid:
					extrapolatedData.update({prefix + self.QuantityMidText + self.Species + suffix:self.isFloat(dictValuesRawMid[key])})
			
			elif self.IvOrPo == "po":
				# Mid quantity
				highestLinearDoseMid, lowestFlatRegionDoseMid, aMid, bMid, r2Mid, quantityMid, doseMid = self.linearityDoseRangeAndDose(dictValuesRawMid)
				extrapolatedData.update({prefix + self.HighestLinearDoseMidText + self.Species + suffix:self.isFloat(highestLinearDoseMid)})
				extrapolatedData.update({prefix + self.LowestFlatRegionDoseMidText + self.Species + suffix:self.isFloat(lowestFlatRegionDoseMid)})
				extrapolatedData.update({prefix + self.InterceptMidText + self.Species + suffix:self.isFloat(aMid)})
				extrapolatedData.update({prefix + self.SlopeMidText + self.Species + suffix:self.isFloat(bMid)})
				extrapolatedData.update({prefix + self.R2MidText + self.Species + suffix:self.isFloat(r2Mid)})
				extrapolatedData.update({prefix + self.QuantityMidText + self.Species + suffix:self.isFloat(quantityMid)})
				extrapolatedData.update({prefix + self.DoseMidText + self.Species + suffix:self.isFloat(doseMid)})
		
			# Return output
			return extrapolatedData	

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


	# Analyse dose ~ auc dictionary - convert to log10 scale
	def analyseDoseAucDictionary(self, extrapolatedData, dictValuesRawAuc, prefix, suffix):
		try:		
			if self.IvOrPo == "iv":
				# Auc
				for key in dictValuesRawAuc:
					extrapolatedData.update({prefix + self.QuantityAucText + self.Species + suffix:self.isFloat(dictValuesRawAuc[key])})
			
			elif self.IvOrPo == "po":			
				highestLinearDoseAuc, lowestFlatRegionDoseAuc, aAuc, bAuc, r2Auc, quantityAuc, doseAuc = self.linearityDoseRangeAndDose(dictValuesRawAuc)
				extrapolatedData.update({prefix + self.HighestLinearDoseAucText + self.Species + suffix:self.isFloat(highestLinearDoseAuc)})
				extrapolatedData.update({prefix + self.LowestFlatRegionDoseAucText + self.Species + suffix:self.isFloat(lowestFlatRegionDoseAuc)})
				extrapolatedData.update({prefix + self.InterceptAucText + self.Species + suffix:self.isFloat(aAuc)})
				extrapolatedData.update({prefix + self.SlopeAucText + self.Species + suffix:self.isFloat(bAuc)})
				extrapolatedData.update({prefix + self.R2AucText + self.Species + suffix:self.isFloat(r2Auc)})
				extrapolatedData.update({prefix + self.QuantityAucText + self.Species + suffix:self.isFloat(quantityAuc)})
				extrapolatedData.update({prefix + self.DoseAucText + self.Species + suffix:self.isFloat(doseAuc)})
				
			# Return output
			return extrapolatedData	

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


	# Determine linearity dose range and dose limit
	def linearityDoseRangeAndDose(self, dictValuesRaw):
		try:
			# Check that none of the values in the key-value pairs contains a value of 0.0
			zeroValueFound = False
			for key in dictValuesRaw:
				if not dictValuesRaw[key] > 0.0:
					zeroValueFound = True
					break
			
			if zeroValueFound == False:		
				# Make two copies of the dictValuesRaw
				quantityValues1 = dictValuesRaw.copy()
				quantityValues2 = {}
				
				#
				# For the list of doses identify a linear region for the lower doses - indicated by a slope of 1 for at least 3 consectutive doses; and a flat region for the upper doses - indicated by slope of 0 for 
				# at least 2 consectutive doses.
				#
				# Note, e.g., self.Dose = [0.000001, 0.000005, 0.00001, 0.00005, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0, 25.0, 50.0, 75.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0, 10000.0]
				#
				# Set highestLinearDose to the first value in self.Dose, i.e., self.Dose[0] = 0.000001 and set the lowestFlatRegionDose to the last value in self.Dose, i.e., self.Dose[1] = 10000.0
				highestLinearDose = self.Doses[0]
				lowestFlatRegionDose = self.Doses[-1]
				if len(self.Doses) > 3:
					for i, j in reversed(list(enumerate(self.Doses))):	
						b = self.determineSlope(quantityValues1)
						if abs(1 - b) <= 0.0001:
							highestLinearDose = j
							if len(self.Doses) > 3:
								if len(quantityValues2) > 0:
									for k in self.Doses[i+1:]:
										if len(quantityValues2) > 1:
											b = self.determineSlope(quantityValues2)
											if abs(b) <= 0.05:
												# Scenario 1: linear dose range involving 3 or more doses and a flat dose range involving 2 or more doses
												lowestFlatRegionDose = k
												break
											else:
												if k != self.Doses[-1]:
													del quantityValues2[k]
										else:
											# Scenario 2: linear dose range involving 3 or more doses and a flat dose range that involves only 1 dose 
											lowestFlatRegionDose = k
											break
									break
								else:
									# Scenario 3: linear dose range involving 4 or more linear doses but no doses to form a flat dose range - note, that iv scenarios fall into this scenario also (see below)
									# For po scenarios, return the highest dose in the original range for lowestFlatRegionDose (pre-set).
									if self.MethodName.find("iv") != -1:									
										lowestFlatRegionDose = 'nan'
									break
							else:
								# Scenario 4: linear dose range involving 3 doses but no doses to form a flat dose range
								lowestFlatRegionDose = 'nan'
								break
						else:
							if len(quantityValues1) > 3:
								quantityValues2.update({j:quantityValues1[j]})
								del quantityValues1[j]
							else:
								# Scenario 5: 3 doses unavailable to form a linear dose range
								highestLinearDose = 'nan'
								lowestFlatRegionDose = 'nan'
								break
				else:
					# Scenario 6: less than 3 doses available to consider
					highestLinearDose = 'nan'
					lowestFlatRegionDose = 'nan'	
			else:
				# Scenario 7: one of the values in the key-value pairs within dictValuesRaw equals zero
				highestLinearDose = 'nan'
				lowestFlatRegionDose = 'nan'
			
			if highestLinearDose != 'nan':
				# Determine intercept, slope and r2 for the linear dose range
				a, b, r2 = self.linearStatistics(quantityValues1)				
			else:
				a = 'nan'
				b = 'nan'
				r2 = 'nan'
			
			if lowestFlatRegionDose != 'nan':
				# Determine the quantity limit (i.e., the quantity associated to the zero response region with respect to the dose) 
				quantity = dictValuesRaw[lowestFlatRegionDose]
			else:
				# For iv scenarios, return the dose corresponding to the defaultIvDose parameter (units of mg kg-1).
				if self.MethodName.find("iv") != -1:
					if a != 'nan' and b != 'nan':
						quantity = self.quantity(a, b, float(self.IvDoseForQuantityCalculation) * float(self.SpeciesBodyWeight))
					else:
						quantity = 'nan'
				else:
					quantity = 'nan'
			
			if highestLinearDose != 'nan' and lowestFlatRegionDose != 'nan':
				# Determine the dose limit (i.e., the dose corresponding to the quantity) 
				dose = self.dose(a, b, quantity)
			else:
				dose = 'nan'
			 		
			# Return output
			return highestLinearDose, lowestFlatRegionDose, a, b, r2, quantity, dose

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


	# Determine slope
	def determineSlope(self, dictValues):
		try:
			meanX, meanY = self.calculateMeans(dictValues)
			sumXY, sumX2, sumY2 = self.sumTerms(dictValues, meanX, meanY)
			b = float(sumXY) / float(sumX2) 			
			
			# Return output
			return b

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
			
		
	# Calculate mean X and Y values
	def calculateMeans(self, dictValues):
		try:
			import math
			
			n = 0
			sumX = 0
			sumY = 0
			for key in dictValues:
				n += 1
				sumX = sumX + math.log10(float(key))
				sumY = sumY + math.log10(float(dictValues[key]))
			meanX = float(sumX) / float(n)
			meanY = float(sumY) / float(n)
			
			# Return output
			return meanX, meanY

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
			
		
	# Calculate sum terms
	def sumTerms(self, dictValues, meanX, meanY):
		try:
			import math
			
			sumXY = 0
			sumX2 = 0
			sumY2 = 0
			for key in dictValues:
				sumXY = sumXY + ((math.log10(float(key)) - float(meanX)) * (math.log10(float(dictValues[key])) - float(meanY)))
				sumX2 = sumX2 + math.pow((math.log10(float(key)) - float(meanX)),2)
				sumY2 = sumY2 + math.pow((math.log10(float(dictValues[key])) - float(meanY)),2)
		
			# Return output
			return sumXY, sumX2, sumY2		

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


	# Calculate linear statistics
	def linearStatistics(self, dictValues):
		try:
			meanX, meanY = self.calculateMeans(dictValues)
			sumXY, sumX2, sumY2 = self.sumTerms(dictValues, meanX, meanY)

			b = float(sumXY) / float(sumX2) 
			a = float(meanY) - (float(b) * float(meanX))
			regressionSS, residualSS = self.sumSquares(dictValues, meanY, a, b)
			r2 = float(regressionSS) / (float(regressionSS) + float(residualSS))			
		
			# Return output
			return a, b, r2

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


	# Calculate sum of squares terms
	def sumSquares(self, dictValues, meanY, a, b):
		try:
			import math
			
			sumYHatYMean = 0
			sumYYHat = 0
			for key in dictValues:
				YHat = (float(b) * math.log10(float(key))) + float(a)
				sumYHatYMean = sumYHatYMean + math.pow((float(YHat) - float(meanY)),2)
				sumYYHat = sumYYHat + math.pow((math.log10(float(dictValues[key])) - float(YHat)),2)
			
			# Return output
			return sumYHatYMean, sumYYHat	

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
			

	# Determine quantity
	def quantity(self, a, b, dose):
		try:
			import math
			
			quantity = math.pow(10, float(a) + (math.log10(float(dose)) * float(b)))

			# Return output
			return quantity

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
			

	# Determine dose limit
	def dose(self, a, b, quantity):
		try:
			import math
			
			dose = (math.log10(float(quantity)) - float(a)) / float(b)

			# Return output
			return dose

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

