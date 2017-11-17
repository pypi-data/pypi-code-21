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

description = "The insilicolynxdqi.system folder statistics.py module"

class Statistics:
	# Class variables


	# __init__
	def __init__(self, settings, index, dataFile, scale, prefix, option):
		try:
			import os
	
			self.ConcentrationScales = settings["concentrationScales"]
			if scale in self.ConcentrationScales:			
				self.ExportRescaledUnitsText = settings["exportRescaledUnitsText"][scale]
			self.ExportUnitsText = settings["exportUnitsText"][scale]
			if settings["methods"][index] == 5:
				self.MethodText = "iv_2c_total_"
			elif settings["methods"][index] == 6:
				self.MethodText = "iv_2c_free_"
			self.Prefix = prefix
			self.Scale = scale
			self.YAxisTitleSubString = settings["quantityLabels"][option]

			# Create self.PlotDataFile
			if os.path.dirname(dataFile) == "":
				newPath = settings["analysisPrefix"] + os.path.splitext(os.path.basename(dataFile))[0] + settings["summarySuffix"] + os.sep 
			else:
				newPath = os.path.dirname(dataFile) + os.sep + settings["analysisPrefix"] + os.path.splitext(os.path.basename(dataFile))[0] + settings["summarySuffix"] + os.sep 
			if not os.path.isdir(newPath): os.makedirs(newPath)
			self.PlotDataFile = newPath + prefix + settings["ivTitlesText"][option] + settings["textFileExtension"]

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
			return "The insilicolynxdqi Statistics class"
		
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
			

	# Process compound data
	def processCompoundData(self, settings, dictData, assembledData, nameOrder):
		try:
			from insilicolynxdqi.system.t_distribution import TDistribution
			tDistribution = TDistribution()
			
			meanList = []
			lowerDistributionIntervalList = []
			upperDistributionIntervalList = []
			standardDeviationList = []
			lowerConfidenceIntervalOfTheMeanList = []
			upperConfidenceIntervalOfTheMeanList = []
			
			if self.Scale in self.ConcentrationScales:
				meanRescaledList = []
				lowerDistributionIntervalRescaledList = []
				upperDistributionIntervalRescaledList = []
				lowerConfidenceIntervalOfTheMeanRescaledList = []
				upperConfidenceIntervalOfTheMeanRescaledList = []
			
			revisedNameOrder = []
			compoundStatistics = {}	
			
			for key in nameOrder:
				if len(assembledData[key][0]) > 0:	
					mean = self.mean(assembledData[key][0])
					
					lowerDistributionInterval, upperDistributionInterval = self.distributionIntervals(settings["intervalLevelDistribution"], assembledData[key][0])
					
					if mean != 'nan':
						standardDeviation = self.standardDeviation(assembledData[key][0], mean)
					
					i = len(assembledData[key][0])
					if i >= 3 and mean != 'nan' and standardDeviation != 'nan':
						if i - 1 != settings["currentTCriticalValueDegreesOfFreedom"]:
							# Determine t critical value by integration of the relevant Student's t-distribution probability density function - note, degrees of freedom is the sample size - 1.
							tCriticalValue = tDistribution.integrate(tDistribution.generatePDF, i - 1, settings["oneSidedProbabilityLevel"])
							settings.update({"currentTCriticalValueDegreesOfFreedom":i - 1})
							settings.update({"currentTCriticalValue":float(tCriticalValue)})
						lowerConfidenceIntervalOfTheMean, upperConfidenceIntervalOfTheMean = self.confidenceIntervalsOfTheMean(mean, standardDeviation, i, settings["currentTCriticalValue"])
						
					else:
						lowerConfidenceIntervalOfTheMean = mean
						upperConfidenceIntervalOfTheMean = mean
					
					meanList.append(mean)
					lowerDistributionIntervalList.append(lowerDistributionInterval)
					upperDistributionIntervalList.append(upperDistributionInterval)		
					standardDeviationList.append(standardDeviation)
					lowerConfidenceIntervalOfTheMeanList.append(lowerConfidenceIntervalOfTheMean)
					upperConfidenceIntervalOfTheMeanList.append(upperConfidenceIntervalOfTheMean)
					
					if self.Scale in self.ConcentrationScales:
						# If scale refers to a mg L-1 concentration add rescaled to M data - check molecular weight is available
						if assembledData[key][1] != 'nan':
							if mean != 'nan':
								meanRescaled = self.rescaleConcentrations(mean, assembledData[key][1])		
							else:
								meanRescaled = 'nan'
						
							if lowerDistributionInterval != 'nan':
								lowerDistributionIntervalRescaled = self.rescaleConcentrations(lowerDistributionInterval, assembledData[key][1])		
							else:
								lowerDistributionIntervalRescaled = 'nan'						
							
							if upperDistributionInterval != 'nan':
								upperDistributionIntervalRescaled = self.rescaleConcentrations(upperDistributionInterval, assembledData[key][1])
							else:
								upperDistributionIntervalRescaled = 'nan'
							
							if lowerConfidenceIntervalOfTheMean != 'nan':
								lowerConfidenceIntervalOfTheMeanRescaled = self.rescaleConcentrations(lowerConfidenceIntervalOfTheMean, assembledData[key][1])
							else:
								lowerConfidenceIntervalOfTheMeanRescaled = 'nan'
							
							if upperConfidenceIntervalOfTheMean != 'nan':
								upperConfidenceIntervalOfTheMeanRescaled = self.rescaleConcentrations(upperConfidenceIntervalOfTheMean, assembledData[key][1])
							else:
								upperConfidenceIntervalOfTheMeanRescaled = 'nan'						
							
							meanRescaledList.append(meanRescaled)
							lowerDistributionIntervalRescaledList.append(lowerDistributionIntervalRescaled)
							upperDistributionIntervalRescaledList.append(upperDistributionIntervalRescaled)
							lowerConfidenceIntervalOfTheMeanRescaledList.append(lowerConfidenceIntervalOfTheMeanRescaled)
							upperConfidenceIntervalOfTheMeanRescaledList.append(upperConfidenceIntervalOfTheMeanRescaled)
												
							compoundStatistics.update({key:[assembledData[key][1], lowerDistributionInterval, mean, upperDistributionInterval, lowerDistributionIntervalRescaled, meanRescaled, upperDistributionIntervalRescaled]})

						else:
							meanRescaledList.append("")
							lowerDistributionIntervalRescaledList.append("")
							upperDistributionIntervalRescaledList.append("")		
							lowerConfidenceIntervalOfTheMeanRescaledList.append("")
							upperConfidenceIntervalOfTheMeanRescaledList.append("")
							
							compoundStatistics.update({key: [assembledData[key][1], lowerDistributionInterval, mean, upperDistributionInterval, "", "", ""]})
					
					else:
						compoundStatistics.update({key: [assembledData[key][1], lowerDistributionInterval, mean, upperDistributionInterval]})
					
					revisedNameOrder.append(key)						

				else:
					meanList.append("")
					lowerDistributionIntervalList.append("")
					upperDistributionIntervalList.append("")		
					standardDeviationList.append("")
					lowerConfidenceIntervalOfTheMeanList.append("")
					upperConfidenceIntervalOfTheMeanList.append("")
					if self.Scale in self.ConcentrationScales:
						meanRescaledList.append("")
						lowerDistributionIntervalRescaledList.append("")
						upperDistributionIntervalRescaledList.append("")		
						lowerConfidenceIntervalOfTheMeanRescaledList.append("")
						upperConfidenceIntervalOfTheMeanRescaledList.append("")
						
			if self.Scale in self.ConcentrationScales:
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + settings["meanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: meanList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["lowerDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: lowerDistributionIntervalList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["upperDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: upperDistributionIntervalList})	
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + settings["stDevText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: standardDeviationList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + str(float('%.4g' % settings["confidenceMeanLevel"])) + settings["spaceText"] + settings["lowerConfidenceIntervalOfTheMeanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: lowerConfidenceIntervalOfTheMeanList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + str(float('%.4g' % settings["confidenceMeanLevel"])) + settings["spaceText"] + settings["upperConfidenceIntervalOfTheMeanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: upperConfidenceIntervalOfTheMeanList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["spaceText"] + settings["meanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: meanRescaledList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["lowerDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: lowerDistributionIntervalRescaledList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["upperDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: upperDistributionIntervalRescaledList})	
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["spaceText"] + str(float('%.4g' % settings["confidenceMeanLevel"])) + settings["spaceText"] + settings["lowerConfidenceIntervalOfTheMeanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: lowerConfidenceIntervalOfTheMeanRescaledList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["spaceText"] + str(float('%.4g' % settings["confidenceMeanLevel"])) + settings["spaceText"] + settings["upperConfidenceIntervalOfTheMeanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: upperConfidenceIntervalOfTheMeanRescaledList})

				columnHeaders = [
								settings["name"],
								settings["molecularWeightText"], 
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["lowerDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"],
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + settings["meanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"],
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["upperDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"],		
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["lowerDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"],
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["spaceText"] + settings["meanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"],
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportRescaledUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["upperDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]
								]
											
			else:
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + settings["meanText"] + settings["spaceText"] + settings["speciesName"]: meanList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["lowerDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: lowerDistributionIntervalList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["upperDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: upperDistributionIntervalList})	
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + settings["stDevText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: standardDeviationList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + str(float('%.4g' % settings["confidenceMeanLevel"])) + settings["spaceText"] + settings["lowerConfidenceIntervalOfTheMeanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: lowerConfidenceIntervalOfTheMeanList})
				dictData.update({settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + str(float('%.4g' % settings["confidenceMeanLevel"])) + settings["spaceText"] + settings["upperConfidenceIntervalOfTheMeanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]: upperConfidenceIntervalOfTheMeanList})
						
				columnHeaders = [
								settings["name"],
								settings["molecularWeightText"], 
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["lowerDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"],
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["spaceText"] + settings["meanText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"],
								settings["log10Text"] + self.MethodText + self.Prefix + self.YAxisTitleSubString + self.ExportUnitsText + settings["approximateText"] + str(float('%.4g' % settings["intervalLevelDistribution"])) + settings["spaceText"] + settings["upperDistributionIntervalText"] + settings["spaceText"] + settings["speciesName"] + settings["parenthesisText"]
								]
							
			# Export plot data to file
			if len(compoundStatistics) > 0:
				self.exportPlotDataToFile(settings, revisedNameOrder, compoundStatistics, columnHeaders)
			
			return settings, dictData
			
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
			

	# Mean
	def mean(self, data):
		try:
			sumData = 0
			
			for i in data:
				sumData = float(sumData) + float(i)
			
			mean = float(sumData / len(data))
			
			if self.isFloat(mean) != True:
				mean = 'nan'
			
			return mean
			
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
				return False
			else:
				return True
			
		except ValueError:
			return False
			
		except TypeError:
			return False

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


	# Standard deviation
	def standardDeviation(self, data, mean):
		try:
			import math
			
			if len(data) > 1:
				standardDeviation = math.pow(sum([math.pow(x - float(mean), 2) for x in data]) / (len(data) - 1), 0.5)
			
				if self.isFloat(standardDeviation) != True or float(standardDeviation) <= 0:
					standardDeviation = 'nan'
					
			else:
				standardDeviation = 'nan'			
			
			return standardDeviation
			
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
			

	# Distribution intervals
	def distributionIntervals(self, intervalLevelDistribution, data):
		try:		
			# Determine the integer (two-sided) number of outliers to ignore
			twoSidedNumberOfOutliersToIgnore = int(round(((float(100) - float(intervalLevelDistribution)) / float(100)) * len(data)))

			# There needs to be, in total, two or more outliers to ignore
			if twoSidedNumberOfOutliersToIgnore >= 2:
				
				# There needs to be an even number of outliers to ignore
				if twoSidedNumberOfOutliersToIgnore % 2 == 1:
					twoSidedNumberOfOutliersToIgnore = twoSidedNumberOfOutliersToIgnore + 1
			
			else:
				twoSidedNumberOfOutliersToIgnore = 0
					
			# Create an asscending list of the contents of the the data list
			sortedData = sorted(data)
	
			# Determine the one-sided number of outliers to ignore
			oneSidedNumberOfOutliersToIgnore = int(round(twoSidedNumberOfOutliersToIgnore / 2))
						
			# From the left hand side of the sortedData, determine the next value after ignoring the one sided number of outliers to ignore - as the first item in any list has the index 0 this is given by sortedData[oneSidedNumberOfOutliersToIgnore]
			lowerDistributionInterval = sortedData[oneSidedNumberOfOutliersToIgnore]
			if self.isFloat(lowerDistributionInterval) != True:
				lowerDistributionInterval = 'nan'

			# From the right hand side of the sortedData, determine the next value after ignoring the one sided number of outliers to ignore - as the right hand side of a list can be accessed using a minus sign this is given by sortedData[-(oneSidedNumberOfOutliersToIgnore + 1)], (note list[-1] returns the last list item)
			upperDistributionInterval = sortedData[-(oneSidedNumberOfOutliersToIgnore + 1)]
			if self.isFloat(upperDistributionInterval) != True:
				upperDistributionInterval = 'nan'
			
			return lowerDistributionInterval, upperDistributionInterval
			
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


	# Confidence intervals of the mean
	def confidenceIntervalsOfTheMean(self, mean, standardDeviation, n, tCriticalValue):
		try:
			import math
			
			lowerConfidenceInterval = float(mean) - ((float(tCriticalValue) * float(standardDeviation)) / math.pow(n, 0.5))
			if self.isFloat(lowerConfidenceInterval) != True:
				lowerConfidenceInterval = 'nan'
			
			upperConfidenceInterval = float(mean) + ((float(tCriticalValue) * float(standardDeviation)) / math.pow(n, 0.5))
			if self.isFloat(upperConfidenceInterval) != True:
				upperConfidenceInterval = 'nan'
				
			return lowerConfidenceInterval, upperConfidenceInterval
			
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
			

	# rescaleConcentrations
	def rescaleConcentrations(self, value, mol_wt):
		try:
			import math
			
			rescaledValue = math.log10(math.pow(10, float(value)) / (1000 * float(mol_wt)))
	
			return rescaledValue
			
		except ValueError:
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


	# Export plot data to file
	def exportPlotDataToFile(self, settings, revisedNameOrder, compoundStatistics, columnHeaders):
		try:
			from insilicolynxdqi.system.csv_tools import CsvTools
			csvTools = CsvTools(settings)
			#
			# Note, concentrations are in mg L-1.
			#
			# Note, the unique names stored in revisedNameOrder and used as keys in compoundStatistics take the form: name + settings[nameSubstring] + groupReference.
			# For the purpose of exporting to file - need to remove the "+ settings[nameSubstring] + groupReference" suffix.
			# This can be done using name.split(settings["nameSubstring"])[0]
			#
			
			# Create a list of lists containing a column header as the first element in each list
			listOfLists = [[columnHeader] for columnHeader in columnHeaders]
			
			# Loop through each name in revisedNameOrder
			for name in revisedNameOrder:
				# Add refined name to first list in listOfLists
				listOfLists[0].append(name.split(settings["nameSubstring"])[0])
				
				# Loop through each item in each compoundStatistics' key-value list: [lowerDistributionInterval, mean, upperDistributionInterval]
				for i, j in enumerate(compoundStatistics[name]):
					# Add first item to second list in listOfLists, add second item to third list in listOfLists and add third item to fourth list in listOfLists
					listOfLists[i + 1].append(j)
					
			# Dictionary comprehension: parse the list of lists into a dictionary by setting the first element in each list (i.e.; the column header) as the "key" and the rest of the list as the "value" for each "key:value" pair of the dictionary
			plotDictionary = {listX[0]:listX[1:] for listX in listOfLists}						

			# Transfer plotDictionary to file			
			csvTools.transferDictionaryToFile(settings, plotDictionary, self.PlotDataFile, columnHeaders)

			return ""
			
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
			
