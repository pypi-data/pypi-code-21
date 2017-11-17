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

description = "The insilicolynxdqi.calculations folder absorption_rate_constant.py module"

class AbsorptionRateConstant:
	# Class variables


	# __init__
	def __init__(self, settings):
		try:	
			self.AbsorptionRateConstantCalculationMethodText = settings["absorptionRateConstantCalculationMethodText"]
			self.Caco26P5HumanText = settings["caco26P5HumanText"]
			self.Caco2Ph6P5ToPablCaco2Ph6P5Ratio = settings["caco2Ph6P5ToPablCaco2Ph6P5Ratio"]	
			self.File = settings["dataFile"]
			self.FractionNeutral6P5Text = settings["fractionNeutral6P5Text"]
			self.NameIndex = settings["name"]
			self.PablCaco2Ph6P5 = settings["pablCaco2Ph6P5"]
			self.PablPeffPh6P5 = settings["pablPeffPh6P5"]
			self.PeffPh6P5MaxValue = settings["peffPh6P5MaxValue"]
			self.PmIntercept = settings["pmIntercept"]
			self.PmSlope = settings["pmSlope"]
			self.Species = settings["speciesName"]
			
			self.AbsorptionAmplificationFactor = settings[self.Species + settings["absorptionAmplificationFactorSuffix"]]
			self.AbsorptionCompartmentVolume = settings[self.Species + settings["intestinalFluidVolumeSuffix"]]
			self.IntestinalRadius = settings[self.Species + settings["intestinalRadiusSuffix"]]
		
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
		

	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi AbsorptionRateConstant class"
		
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
	def processFile(self, approach, units):
		try:
			import csv
			parameterValues = {}
			parameterUnits = {}
			fileToRead = open(self.File, 'r')
			with fileToRead:
				reader = csv.DictReader(fileToRead, delimiter="\t")
				for row in reader:
					if approach == self.AbsorptionRateConstantCalculationMethodText:
						parameterValues.update({row[self.NameIndex]:self.absorptionRateConstant(row)})
						parameterUnits.update({row[self.NameIndex]:units})
			
			# Return output
			return parameterValues, parameterUnits	
		
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

					
	# Absorption rate constant
	def absorptionRateConstant(self, rowData):
		try:
			import math
			# (1) Set caco2Ph6P5 (cm s-1)
			caco2Ph6P5 = float(rowData[self.Caco26P5HumanText])
			if caco2Ph6P5 >= self.PablCaco2Ph6P5:
				caco2Ph6P5 = float(self.PablCaco2Ph6P5) * self.Caco2Ph6P5ToPablCaco2Ph6P5Ratio
			
			# (2) Calculate pmCaco2Ph6P5
			pmCaco2Ph6P5 = 1 / ((1 / float(caco2Ph6P5)) - (1 / float(self.PablCaco2Ph6P5)))
			
			# (3) Calculate pmFnCaco2
			pmFnCaco2 = float(pmCaco2Ph6P5) / float(rowData[self.FractionNeutral6P5Text])
			
			# (4) Calculate log10PmFnCaco2
			log10PmFnCaco2 = math.log10(float(pmFnCaco2))
			
			# (5) Apply bespoke linear regression
			log10PmFnPeff = (float(self.PmSlope) * float(log10PmFnCaco2)) + float(self.PmIntercept)
			
			# (6) Calculate pmFnPeff
			pmFnPeff = math.pow(10,float(log10PmFnPeff))
			
			# (7) Calculate pmPeffPh6P5
			pmPeffPh6P5 = float(pmFnPeff) * float(rowData[self.FractionNeutral6P5Text])
			
			# (8) Calculate peffPh6P5 (cm s-1)		
			peffPh6P5  = (1 / ((1 / float(pmPeffPh6P5)) + (1 / float(self.PablPeffPh6P5))))
			if float(peffPh6P5) > self.PeffPh6P5MaxValue:
				peffPh6P5 = self.PeffPh6P5MaxValue
			
			# (9) Calculate the geometric length of an ideal cylinder that corresponds to the absorption compartment volume and intestinal radius
			cylinderLength = float(self.AbsorptionCompartmentVolume) / (math.pi * math.pow(float(self.IntestinalRadius),2))
			
			# (10) Calculate the geometric absorption area for given cylinder length
			geometricSurfaceArea = 2 * math.pi * float(self.IntestinalRadius) * float(cylinderLength)
			
			# (11) Multiply geometric surface area by an absorption amplification factor
			effectiveSurfaceArea =  float(geometricSurfaceArea) * float(self.AbsorptionAmplificationFactor) 
			
			# (12) Calculate absorption rate constant (k1) (s-1)
			k1 = (float(effectiveSurfaceArea) / float(self.AbsorptionCompartmentVolume)) * float(peffPh6P5)
			
			# Return output
			return k1		
		
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

