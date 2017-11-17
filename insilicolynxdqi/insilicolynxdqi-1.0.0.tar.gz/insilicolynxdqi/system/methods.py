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

description = "The insilicolynxdqi.system folder methods.py module"

class Methods:
	# Class variables


	# __init__	
	def __init__(self):
		pass


	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi Methods class"
		
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


	# Additional parameter calculations
	def additionalParameterCalculations(self, calculationAdditionalParameterOrder, calculationAdditionalParameter, calculationAdditionalParameterUnits, settings):
		try:
			from insilicolynxdqi.system.csv_tools import CsvTools
			csvTools = CsvTools(settings)	
			
			for item in calculationAdditionalParameterOrder:
				for parameter in calculationAdditionalParameter:
					if item == parameter:
						if parameter == settings["fractionNeutral6P5Text"]:
							from insilicolynxdqi.calculations.fraction_neutral import FractionNeutral
							fractionNeutral = FractionNeutral(settings)
							parameterValues, parameterUnits = fractionNeutral.processFile(calculationAdditionalParameter[parameter], calculationAdditionalParameterUnits[parameter + settings["unitsSuffix"]], 6.5)

						if parameter == settings["fractionNeutral7P4Text"]:
							from insilicolynxdqi.calculations.fraction_neutral import FractionNeutral
							fractionNeutral = FractionNeutral(settings)
							parameterValues, parameterUnits = fractionNeutral.processFile(calculationAdditionalParameter[parameter], calculationAdditionalParameterUnits[parameter + settings["unitsSuffix"]], 7.4)

						if parameter == settings["intrinsicSolubilityText"]:
							from insilicolynxdqi.calculations.intrinsic_solubility import IntrinsicSolubility
							intrinsicSolubility = IntrinsicSolubility(settings)
							parameterValues, parameterUnits = intrinsicSolubility.processFile(calculationAdditionalParameter[parameter], calculationAdditionalParameterUnits[parameter + settings["unitsSuffix"]])

						if parameter == settings["solubility6P5Text"]:
							from insilicolynxdqi.calculations.solubility_6p5 import Solubility6P5
							solubility6P5 = Solubility6P5(settings)
							parameterValues, parameterUnits = solubility6P5.processFile(calculationAdditionalParameter[parameter], calculationAdditionalParameterUnits[parameter + settings["unitsSuffix"]])
							
						if parameter == settings["absorptionRateConstantText"] + settings["speciesName"]:
							from insilicolynxdqi.calculations.absorption_rate_constant import AbsorptionRateConstant
							absorptionRateConstant = AbsorptionRateConstant(settings)
							parameterValues, parameterUnits = absorptionRateConstant.processFile(calculationAdditionalParameter[parameter], calculationAdditionalParameterUnits[parameter + settings["unitsSuffix"]])
	
						csvTools.addDataColumn(parameter, parameterValues)	# Add parameter and units (if necessary) to file
						if calculationAdditionalParameterUnits[parameter + settings["unitsSuffix"]] != "na":
							csvTools.addDataColumn(parameter + settings["unitsSuffix"], parameterUnits)
		
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


	# Dose quantity calculations
	def doseQuantityCalculations(self, settings):
		try:
			import shutil
			from insilicolynxdqi.system.csv_tools import CsvTools
			csvTools = CsvTools(settings)
			
			# Create a copy of the data file
			shutil.copy(settings["dataFile"], settings["dataFileOriginal"])		
			
			settings.update({"numberRows":csvTools.dataRowsInCSV()})
			
			if settings["methodName"] == "po_1c_total" + "_" + settings["speciesName"]:
				from insilicolynxdqi.calculations.po_1c_total import Po1CTotal
				po1CTotal = Po1CTotal()
				allNames, allValues1, columnHeaderSuffix = po1CTotal.processFile(settings)		
			
			elif settings["methodName"] == "po_1c_free" + "_" + settings["speciesName"]:
				from insilicolynxdqi.calculations.po_1c_free import Po1CFree
				po1CFree = Po1CFree()
				allNames, allValues1, columnHeaderSuffix = po1CFree.processFile(settings)
			
			elif settings["methodName"] == "po_2c_total" + "_" + settings["speciesName"]:
				from insilicolynxdqi.calculations.po_2c_total import Po2CTotal
				po2CTotal = Po2CTotal()
				allNames, allValues1, allValues2, allValues3, allValues4, allValues5, columnHeaderSuffix = po2CTotal.processFile(settings)
			
			elif settings["methodName"] == "po_2c_free" + "_" + settings["speciesName"]:
				from insilicolynxdqi.calculations.po_2c_free import Po2CFree
				po2CFree = Po2CFree()
				allNames, allValues1, allValues2, allValues3, allValues4, allValues5, columnHeaderSuffix = po2CFree.processFile(settings)	
			
			elif settings["methodName"] == "iv_2c_total" + "_" + settings["speciesName"]:
				from insilicolynxdqi.calculations.iv_2c_total import Iv2CTotal
				iv2CTotal = Iv2CTotal()
				allNames, allValues1, allValues2, allValues3, allValues4, allValues5, columnHeaderSuffix = iv2CTotal.processFile(settings)
			
			elif settings["methodName"] == "iv_2c_free" + "_" + settings["speciesName"]:
				from insilicolynxdqi.calculations.iv_2c_free import Iv2CFree
				iv2CFree = Iv2CFree()
				allNames, allValues1, allValues2, allValues3, allValues4, allValues5, columnHeaderSuffix = iv2CFree.processFile(settings)	
			
			
			# Add generic parameters from allValues1, allValues2 (if necessary), allValues3 (if necessary), allValues4 (if necessary) and allValues5 (if necessary)
			listParameters = self.defineGenericParameters(settings)			
			includeUnits = "yes"
			for parameter in listParameters:
				for index, item in enumerate(columnHeaderSuffix):
					if index == 0:
						self.addParameter(allNames, allValues1, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
					elif index == 1:
						self.addParameter(allNames, allValues2, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
					elif index == 2:
						self.addParameter(allNames, allValues3, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
					elif index == 3:
						self.addParameter(allNames, allValues4, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
					elif index == 4:
						self.addParameter(allNames, allValues5, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
		
			# Add quantity parameters from allValues1, allValues2 (if necessary), allValues3 (if necessary), allValues4 (if necessary) and allValues5 (if necessary)
			listParameters = self.defineQuantityParameters(settings)			
			includeUnits = "no"
			for parameter in listParameters:
				for index, item in enumerate(columnHeaderSuffix):
					if index == 0:
						self.addParameter(allNames, allValues1, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
					elif index == 1:
						self.addParameter(allNames, allValues2, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
					elif index == 2:
						self.addParameter(allNames, allValues3, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)
					elif index == 3:
						self.addParameter(allNames, allValues4, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)		
					elif index == 4:
						self.addParameter(allNames, allValues5, parameter + settings["speciesName"] + columnHeaderSuffix[index], parameter + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix[index], settings, includeUnits)		
				
			# Tidy up files
			shutil.move(settings["dataFile"], settings["dataFileNew"])
			shutil.move(settings["dataFileOriginal"], settings["dataFile"])
			
			# Return output
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


	# Define generic parameters to report
	def defineGenericParameters(self, settings):
		try:
			if settings["method"] in [1, 2]:
				listParameters = [
									settings["firstPassFractionHepaticMetabolisedText"],
									settings["eliminationRateConstantText"],
									settings["absorptionDelayText"],
									settings["intestinalTransitTimeText"],
									settings["doseIntervalText"],
									settings["simulationLengthText"],									
								]
			elif settings["method"] in [3, 4]:
				listParameters = [
									settings["firstPassFractionHepaticMetabolisedText"],
									settings["centralToPeripheralCompartmentRateConstantText"],
									settings["peripheralToCentralCompartmentRateConstantText"],
									settings["eliminationRateConstantText"],
									settings["absorptionDelayText"],
									settings["intestinalTransitTimeText"],
									settings["doseIntervalText"],
									settings["simulationLengthText"],									
								]	
	
			elif settings["method"] in [5, 6]:
				listParameters = [
									settings["centralToPeripheralCompartmentRateConstantText"],
									settings["peripheralToCentralCompartmentRateConstantText"],
									settings["eliminationRateConstantText"],
									settings["doseText"],
									settings["doseIntervalText"],
									settings["simulationLengthText"]
								]

			# Return output
			return listParameters
			
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


	# Define quantity parameters to report
	def defineQuantityParameters(self, settings):
		try:
			if settings["ivOrPo"] == "iv":
				
				if settings["compartment"] == "central":
					listParameters = [
										settings["amountBPrefix"] + settings["quantityMaxText"],					
										settings["amountBPrefix"] + settings["quantityMidText"],
										settings["amountBPrefix"] + settings["quantityMinText"],								
										settings["aucAmountBPrefix"] + settings["quantityAucText"],								
										settings["concentrationBPrefix"] + settings["quantityMaxText"],	
										settings["concentrationBPrefix"] + settings["quantityMidText"],							
										settings["concentrationBPrefix"] + settings["quantityMinText"],																		
										settings["aucConcentrationBPrefix"] + settings["quantityAucText"]
									]
				elif settings["compartment"] == "peripheral":
					listParameters = [
										settings["amountCPrefix"] + settings["quantityMaxText"],
										settings["amountCPrefix"] + settings["quantityMidText"],				
										settings["amountCPrefix"] + settings["quantityMinText"],														
										settings["aucAmountCPrefix"] + settings["quantityAucText"],																			
										settings["aucConcentrationCPrefix"] + settings["quantityAucText"]
									]
				elif settings["compartment"] == "central_peripheral":
					listParameters = [
										settings["amountBCPrefix"] + settings["quantityMaxText"],					
										settings["amountBCPrefix"] + settings["quantityMidText"],								
										settings["amountBCPrefix"] + settings["quantityMinText"],												
										settings["aucAmountBCPrefix"] + settings["quantityAucText"],																					
										settings["aucConcentrationBCPrefix"] + settings["quantityAucText"]
									]
				elif settings["compartment"] == "all":
					listParameters = [
										settings["amountBPrefix"] + settings["quantityMaxText"],
										settings["amountBPrefix"] + settings["quantityMidText"],				
										settings["amountBPrefix"] + settings["quantityMinText"],													
										settings["aucAmountBPrefix"] + settings["quantityAucText"],								
										settings["concentrationBPrefix"] + settings["quantityMaxText"],	
										settings["concentrationBPrefix"] + settings["quantityMidText"],						
										settings["concentrationBPrefix"] + settings["quantityMinText"],									
										settings["aucConcentrationBPrefix"] + settings["quantityAucText"],
										settings["amountCPrefix"] + settings["quantityMaxText"],
										settings["amountCPrefix"] + settings["quantityMidText"],			
										settings["amountCPrefix"] + settings["quantityMinText"],								
										settings["aucAmountCPrefix"] + settings["quantityAucText"],																
										settings["aucConcentrationCPrefix"] + settings["quantityAucText"],
										settings["amountBCPrefix"] + settings["quantityMaxText"],					
										settings["amountBCPrefix"] + settings["quantityMidText"],
										settings["amountBCPrefix"] + settings["quantityMinText"],										
										settings["aucAmountBCPrefix"] + settings["quantityAucText"],																					
										settings["aucConcentrationBCPrefix"] + settings["quantityAucText"]
									]
									
			elif settings["ivOrPo"] == "po":
				
				if settings["compartment"] == "plasma" or settings["compartment"] == "central":
					listParameters = [										
										settings["amountBPrefix"] + settings["interceptMaxText"],
										settings["amountBPrefix"] + settings["doseMaxText"],
										settings["amountBPrefix"] + settings["quantityMaxText"],
										settings["amountBPrefix"] + settings["highestLinearDoseMaxText"],
										settings["amountBPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["amountBPrefix"] + settings["interceptMidText"],
										settings["amountBPrefix"] + settings["doseMidText"],
										settings["amountBPrefix"] + settings["quantityMidText"],
										settings["amountBPrefix"] + settings["highestLinearDoseMidText"],
										settings["amountBPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["amountBPrefix"] + settings["interceptMinText"],
										settings["amountBPrefix"] + settings["doseMinText"],
										settings["amountBPrefix"] + settings["quantityMinText"],
										settings["amountBPrefix"] + settings["highestLinearDoseMinText"],
										settings["amountBPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucAmountBPrefix"] + settings["interceptAucText"],
										settings["aucAmountBPrefix"] + settings["doseAucText"],
										settings["aucAmountBPrefix"] + settings["quantityAucText"],
										settings["aucAmountBPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucAmountBPrefix"] + settings["lowestFlatRegionDoseAucText"],														
																
										settings["concentrationBPrefix"] + settings["interceptMaxText"],
										settings["concentrationBPrefix"] + settings["doseMaxText"],
										settings["concentrationBPrefix"] + settings["quantityMaxText"],
										settings["concentrationBPrefix"] + settings["highestLinearDoseMaxText"],
										settings["concentrationBPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["concentrationBPrefix"] + settings["interceptMidText"],
										settings["concentrationBPrefix"] + settings["doseMidText"],
										settings["concentrationBPrefix"] + settings["quantityMidText"],
										settings["concentrationBPrefix"] + settings["highestLinearDoseMidText"],
										settings["concentrationBPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["concentrationBPrefix"] + settings["interceptMinText"],
										settings["concentrationBPrefix"] + settings["doseMinText"],
										settings["concentrationBPrefix"] + settings["quantityMinText"],
										settings["concentrationBPrefix"] + settings["highestLinearDoseMinText"],
										settings["concentrationBPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucConcentrationBPrefix"] + settings["interceptAucText"],
										settings["aucConcentrationBPrefix"] + settings["doseAucText"],
										settings["aucConcentrationBPrefix"] + settings["quantityAucText"],
										settings["aucConcentrationBPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucConcentrationBPrefix"] + settings["lowestFlatRegionDoseAucText"]
									]
				elif settings["compartment"] == "peripheral":
					listParameters = [
										settings["amountCPrefix"] + settings["interceptMaxText"],
										settings["amountCPrefix"] + settings["doseMaxText"],
										settings["amountCPrefix"] + settings["quantityMaxText"],
										settings["amountCPrefix"] + settings["highestLinearDoseMaxText"],
										settings["amountCPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["amountCPrefix"] + settings["interceptMidText"],
										settings["amountCPrefix"] + settings["doseMidText"],
										settings["amountCPrefix"] + settings["quantityMidText"],
										settings["amountCPrefix"] + settings["highestLinearDoseMidText"],
										settings["amountCPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["amountCPrefix"] + settings["interceptMinText"],
										settings["amountCPrefix"] + settings["doseMinText"],
										settings["amountCPrefix"] + settings["quantityMinText"],
										settings["amountCPrefix"] + settings["highestLinearDoseMinText"],
										settings["amountCPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucAmountCPrefix"] + settings["interceptAucText"],
										settings["aucAmountCPrefix"] + settings["doseAucText"],
										settings["aucAmountCPrefix"] + settings["quantityAucText"],
										settings["aucAmountCPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucAmountCPrefix"] + settings["lowestFlatRegionDoseAucText"]
									]
				elif settings["compartment"] == "central_peripheral":
					listParameters = [
										settings["amountBCPrefix"] + settings["interceptMaxText"],
										settings["amountBCPrefix"] + settings["doseMaxText"],
										settings["amountBCPrefix"] + settings["quantityMaxText"],
										settings["amountBCPrefix"] + settings["highestLinearDoseMaxText"],
										settings["amountBCPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["amountBCPrefix"] + settings["interceptMidText"],
										settings["amountBCPrefix"] + settings["doseMidText"],
										settings["amountBCPrefix"] + settings["quantityMidText"],
										settings["amountBCPrefix"] + settings["highestLinearDoseMidText"],
										settings["amountBCPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["amountBCPrefix"] + settings["interceptMinText"],
										settings["amountBCPrefix"] + settings["doseMinText"],
										settings["amountBCPrefix"] + settings["quantityMinText"],
										settings["amountBCPrefix"] + settings["highestLinearDoseMinText"],
										settings["amountBCPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucAmountBCPrefix"] + settings["interceptAucText"],
										settings["aucAmountBCPrefix"] + settings["doseAucText"],
										settings["aucAmountBCPrefix"] + settings["quantityAucText"],
										settings["aucAmountBCPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucAmountBCPrefix"] + settings["lowestFlatRegionDoseAucText"]
									]
				elif settings["compartment"] == "all":
					listParameters = [
										settings["amountBPrefix"] + settings["interceptMaxText"],
										settings["amountBPrefix"] + settings["doseMaxText"],
										settings["amountBPrefix"] + settings["quantityMaxText"],
										settings["amountBPrefix"] + settings["highestLinearDoseMaxText"],
										settings["amountBPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["amountBPrefix"] + settings["interceptMidText"],
										settings["amountBPrefix"] + settings["doseMidText"],
										settings["amountBPrefix"] + settings["quantityMidText"],
										settings["amountBPrefix"] + settings["highestLinearDoseMidText"],
										settings["amountBPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["amountBPrefix"] + settings["interceptMinText"],
										settings["amountBPrefix"] + settings["doseMinText"],
										settings["amountBPrefix"] + settings["quantityMinText"],
										settings["amountBPrefix"] + settings["highestLinearDoseMinText"],
										settings["amountBPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucAmountBPrefix"] + settings["interceptAucText"],
										settings["aucAmountBPrefix"] + settings["doseAucText"],
										settings["aucAmountBPrefix"] + settings["quantityAucText"],
										settings["aucAmountBPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucAmountBPrefix"] + settings["lowestFlatRegionDoseAucText"],														
																
										settings["concentrationBPrefix"] + settings["interceptMaxText"],
										settings["concentrationBPrefix"] + settings["doseMaxText"],
										settings["concentrationBPrefix"] + settings["quantityMaxText"],
										settings["concentrationBPrefix"] + settings["highestLinearDoseMaxText"],
										settings["concentrationBPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["concentrationBPrefix"] + settings["interceptMidText"],
										settings["concentrationBPrefix"] + settings["doseMidText"],
										settings["concentrationBPrefix"] + settings["quantityMidText"],
										settings["concentrationBPrefix"] + settings["highestLinearDoseMidText"],
										settings["concentrationBPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["concentrationBPrefix"] + settings["interceptMinText"],
										settings["concentrationBPrefix"] + settings["doseMinText"],
										settings["concentrationBPrefix"] + settings["quantityMinText"],
										settings["concentrationBPrefix"] + settings["highestLinearDoseMinText"],
										settings["concentrationBPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucConcentrationBPrefix"] + settings["interceptAucText"],
										settings["aucConcentrationBPrefix"] + settings["doseAucText"],
										settings["aucConcentrationBPrefix"] + settings["quantityAucText"],
										settings["aucConcentrationBPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucConcentrationBPrefix"] + settings["lowestFlatRegionDoseAucText"],
				
										settings["amountCPrefix"] + settings["interceptMaxText"],
										settings["amountCPrefix"] + settings["doseMaxText"],
										settings["amountCPrefix"] + settings["quantityMaxText"],
										settings["amountCPrefix"] + settings["highestLinearDoseMaxText"],
										settings["amountCPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["amountCPrefix"] + settings["interceptMidText"],
										settings["amountCPrefix"] + settings["doseMidText"],
										settings["amountCPrefix"] + settings["quantityMidText"],
										settings["amountCPrefix"] + settings["highestLinearDoseMidText"],
										settings["amountCPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["amountCPrefix"] + settings["interceptMinText"],
										settings["amountCPrefix"] + settings["doseMinText"],
										settings["amountCPrefix"] + settings["quantityMinText"],
										settings["amountCPrefix"] + settings["highestLinearDoseMinText"],
										settings["amountCPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucAmountCPrefix"] + settings["interceptAucText"],
										settings["aucAmountCPrefix"] + settings["doseAucText"],
										settings["aucAmountCPrefix"] + settings["quantityAucText"],
										settings["aucAmountCPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucAmountCPrefix"] + settings["lowestFlatRegionDoseAucText"],
			
										settings["amountBCPrefix"] + settings["interceptMaxText"],
										settings["amountBCPrefix"] + settings["doseMaxText"],
										settings["amountBCPrefix"] + settings["quantityMaxText"],
										settings["amountBCPrefix"] + settings["highestLinearDoseMaxText"],
										settings["amountBCPrefix"] + settings["lowestFlatRegionDoseMaxText"],
										
										settings["amountBCPrefix"] + settings["interceptMidText"],
										settings["amountBCPrefix"] + settings["doseMidText"],
										settings["amountBCPrefix"] + settings["quantityMidText"],
										settings["amountBCPrefix"] + settings["highestLinearDoseMidText"],
										settings["amountBCPrefix"] + settings["lowestFlatRegionDoseMidText"],
																					
										settings["amountBCPrefix"] + settings["interceptMinText"],
										settings["amountBCPrefix"] + settings["doseMinText"],
										settings["amountBCPrefix"] + settings["quantityMinText"],
										settings["amountBCPrefix"] + settings["highestLinearDoseMinText"],
										settings["amountBCPrefix"] + settings["lowestFlatRegionDoseMinText"],

										settings["aucAmountBCPrefix"] + settings["interceptAucText"],
										settings["aucAmountBCPrefix"] + settings["doseAucText"],
										settings["aucAmountBCPrefix"] + settings["quantityAucText"],
										settings["aucAmountBCPrefix"] + settings["highestLinearDoseAucText"],
										settings["aucAmountBCPrefix"] + settings["lowestFlatRegionDoseAucText"]
									]
	
			# Return output
			return listParameters
			
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


	# Add parameter
	def addParameter(self, names, values, parameter, parameterUnits, settings, unitsColumnRequired):
		try:
			from insilicolynxdqi.system.csv_tools import CsvTools
			csvTools = CsvTools(settings)
			
			parameterValues = self.getParameterValues(parameter, names, values)	
			csvTools.addDataColumn(parameter, parameterValues)
			
			if unitsColumnRequired == "yes":
				parameterUnitsValues = self.getParameterValues(parameterUnits, names, values)
				csvTools.addDataColumn(parameterUnits, parameterUnitsValues)
		
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

		
	# Get parameter values
	def getParameterValues(self, parameter, listKeys, dictDictValues):
		try:
			parameterValues = {}
			for key in listKeys:
				parameterValues.update({key:dictDictValues[key][parameter]})
				
			# Return output
			return parameterValues
		
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
			
