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

description = "The insilicolynxdqi.system folder calculation_inputs.py module"

class CalculationInputs:
	# Class variables


	# __init__
	def __init__(self, settings):
		try:
			self.ClText = settings["clText"]
			self.DoseIntervalText = settings["doseIntervalText"]
			self.IvOrPo = settings["ivOrPo"]
			self.Levels = settings["levels"]
			self.MolecularWeightText = settings["molecularWeightText"]
			self.NameParameter = settings["name"]
			self.QualifierSuffix = settings["qualifierSuffix"]
			self.SimulationLengthText = settings["simulationLengthText"]
			self.Species = settings["speciesName"]
			self.UnitsSuffix = settings["unitsSuffix"]
			self.VssText = settings["vssText"]

			if self.IvOrPo == "po":
				self.AbsorptionRateConstantCalculationMethodText = settings["absorptionRateConstantCalculationMethodText"]
				self.AbsorptionRateText = settings["absorptionRateConstantText"]	
				self.Caco26P5HumanText = settings["caco26P5HumanText"]
				self.ChargeTypeText = settings["chargeTypeText"]
				self.CmSMinus1UnitsText = settings["cmSMinus1UnitsText"]
				self.DefaultCalculationMethodText = settings["defaultCalculationMethodText"]
				self.FractionNeutral6P5Text = settings["fractionNeutral6P5Text"]
				self.FractionNeutral7P4Text = settings["fractionNeutral7P4Text"]
				self.IntrinsicSolubilityText = settings["intrinsicSolubilityText"]				
				self.MUnitsText = settings["mUnitsText"]
				self.NaUnitsText = settings["naUnitsText"]
				self.PKaA1Text = settings["pKaA1Text"]
				self.PKaB1Text = settings["pKaB1Text"]
				self.PKaA2Text = settings["pKaA2Text"]
				self.PKaB2Text = settings["pKaB2Text"]
				self.Solubility6P5Text = settings["solubility6P5Text"]
				self.Solubility7P4Text = settings["solubility7P4Text"]
				self.SMinus1UnitsText = settings["sMinus1UnitsText"]
			
			if settings["levels"] == "free":
				self.PpbText = settings["ppbText"]
						
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
			return "The insilicolynxdqi CalculationInputs class"
		
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


	# Prerequisite data	
	def calculationInputData(self, method):
		try:
			calculationInputData = []
			calculationInputDataUnits = []
			headerParameterComparisonRemoveList = []
			headerParameterUnitsComparisonRemoveList = []
					
			# Common requirements
			calculationInputData.append(self.NameParameter)				

			calculationInputData.append(self.DoseIntervalText + self.Species)
			calculationInputDataUnits.append(self.DoseIntervalText  + self.Species + self.UnitsSuffix)
			headerParameterComparisonRemoveList.append(self.DoseIntervalText + self.Species)
			headerParameterUnitsComparisonRemoveList.append(self.DoseIntervalText + self.Species + self.UnitsSuffix)

			calculationInputData.append(self.SimulationLengthText + self.Species)
			calculationInputDataUnits.append(self.SimulationLengthText + self.Species + self.UnitsSuffix)
			headerParameterComparisonRemoveList.append(self.SimulationLengthText + self.Species)
			headerParameterUnitsComparisonRemoveList.append(self.SimulationLengthText  + self.Species + self.UnitsSuffix)
			
			calculationInputData.append(self.MolecularWeightText)

			calculationInputData.append(self.ClText + self.Species)
			calculationInputDataUnits.append(self.ClText + self.Species + self.UnitsSuffix)
			calculationInputData.append(self.ClText + self.Species + self.QualifierSuffix)

			calculationInputData.append(self.VssText + self.Species)
			calculationInputDataUnits.append(self.VssText + self.Species + self.UnitsSuffix)
			calculationInputData.append(self.VssText + self.Species + self.QualifierSuffix)			
			
			if self.IvOrPo == "po":
				calculationInputData.append(self.Caco26P5HumanText)
				calculationInputDataUnits.append(self.Caco26P5HumanText + self.UnitsSuffix)
				calculationInputData.append(self.Caco26P5HumanText + self.QualifierSuffix)
				
				calculationInputData.append(self.ChargeTypeText)
				
				calculationInputData.append(self.PKaA1Text)
				
				calculationInputData.append(self.PKaB1Text)
				
				calculationInputData.append(self.PKaA2Text)
				
				calculationInputData.append(self.PKaB2Text)
				
				calculationInputData.append(self.Solubility7P4Text)
				calculationInputDataUnits.append(self.Solubility7P4Text + self.UnitsSuffix)
				calculationInputData.append(self.Solubility7P4Text + self.QualifierSuffix)

			if self.Levels == "free":
				calculationInputData.append(self.PpbText + self.Species)
				calculationInputDataUnits.append(self.PpbText + self.Species + self.UnitsSuffix)
				calculationInputData.append(self.PpbText + self.Species + self.QualifierSuffix)
			
			# Return output	
			return calculationInputData, calculationInputDataUnits, headerParameterComparisonRemoveList, headerParameterUnitsComparisonRemoveList
		
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


	# Calculate additional input parameters
	def calculationAdditionalParameter(self, method):
		try:
			calculationAdditionalParameterOrder = []
			calculationAdditionalParameterUnits = {}
			calculationAdditionalParameter = {}
		
			# Order: 1
			calculationAdditionalParameterOrder.append(self.FractionNeutral6P5Text)
			self.addToDictionary(self.FractionNeutral6P5Text, self.DefaultCalculationMethodText, calculationAdditionalParameter)
			self.addToDictionary(self.FractionNeutral6P5Text + self.UnitsSuffix, self.NaUnitsText, calculationAdditionalParameterUnits)
			
			# Order: 2
			calculationAdditionalParameterOrder.append(self.FractionNeutral7P4Text)
			self.addToDictionary(self.FractionNeutral7P4Text, self.DefaultCalculationMethodText, calculationAdditionalParameter)	
			self.addToDictionary(self.FractionNeutral7P4Text + self.UnitsSuffix, self.NaUnitsText, calculationAdditionalParameterUnits)
			
			# Order: 3
			calculationAdditionalParameterOrder.append(self.IntrinsicSolubilityText)
			self.addToDictionary(self.IntrinsicSolubilityText, self.DefaultCalculationMethodText, calculationAdditionalParameter)
			self.addToDictionary(self.IntrinsicSolubilityText + self.UnitsSuffix, self.MUnitsText, calculationAdditionalParameterUnits)
			
			# Order: 4
			calculationAdditionalParameterOrder.append(self.Solubility6P5Text)
			self.addToDictionary(self.Solubility6P5Text, self.DefaultCalculationMethodText, calculationAdditionalParameter)
			self.addToDictionary(self.Solubility6P5Text + self.UnitsSuffix, self.MUnitsText, calculationAdditionalParameterUnits)

			# Order: 5
			calculationAdditionalParameterOrder.append(self.AbsorptionRateText + self.Species)
			self.addToDictionary(self.AbsorptionRateText + self.Species, self.AbsorptionRateConstantCalculationMethodText, calculationAdditionalParameter)
			self.addToDictionary(self.AbsorptionRateText + self.Species + self.UnitsSuffix, self.SMinus1UnitsText, calculationAdditionalParameterUnits)
			
			# Return output
			return calculationAdditionalParameterOrder, calculationAdditionalParameter, calculationAdditionalParameterUnits
		
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


	# Add to dictionary	
	def addToDictionary(self, parameterName, parameterValue, dict1):
		try:
			dict1.update({parameterName:parameterValue})
		
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

