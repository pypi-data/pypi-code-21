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

description = "The insilicolynxdqi.system folder add_error_scenarios.py module"

class AddErrorScenarios:
	# Class variables


	# __init__
	def __init__(self):
		pass

	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi AddErrorScenarios class"
		
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


	# Add any columns	
	def addAnyColumns(self, settings, columnHeaders):
		try:
			# Add reference
			if settings["reference"] not in columnHeaders:
				columnHeaders.append(settings["reference"])
			else:
				print("")
				print("\tNote, the output file will contain a revised " + str(settings["reference"]) + " column.")

			# Add group reference
			if settings["groupReference"] not in columnHeaders:
				columnHeaders.append(settings["groupReference"])
			else:
				print("")
				print("\tNote, the output file will contain a revised " + str(settings["groupReference"]) + " column.")
			
			if len(settings["potentialColumnsToAdd"]) > 0:
				for parameter in settings["revisedErrorParameters"]:
					# Add standard deviation columns			
					if settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"] in settings["potentialColumnsToAdd"]:
						columnHeaders.append(settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"])
					
					# Add qualifier columns
					if settings[parameter + settings["prefix"]] + settings["qualifierSuffix"] in settings["potentialColumnsToAdd"]:
						columnHeaders.append(settings[parameter + settings["prefix"]] + settings["qualifierSuffix"])
			
			# Return output
			return columnHeaders
		
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


	# Check data
	def checkData(self, settings, row, someIncorrectData):
		try:
			addRow = True
			for parameter in settings["revisedErrorParameters"]:				
				if addRow == True:
					if parameter == settings["clText"]:
						units = [str.lower(x) for x in settings[settings["clText"] + settings["prefix"] + settings["unitsSuffix"]]]
						if str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) not in units:
							addRow = False
							if someIncorrectData == False:
								print("")
							print("\tThe " + row[settings["name"]] + " data row will not be considered. The units for the in-vivo clearance data are not right; the possible options include: " + str(settings[settings["clText"] + settings["prefix"] + settings["unitsSuffix"]]) + ".")					
						
						elif self.isFloat(row[settings[parameter + settings["prefix"]]]):
							# A lower and upper limit threshold applies to Cl (mL min-1 kg-1)
							lowerValue = float(settings["clLowerLimit"])
							upperValue = float(settings["clUpperLimit"])
							
							if float(row[settings[parameter + settings["prefix"]]]) < lowerValue:
								addRow = False
								if someIncorrectData == False:
									print("")
								print("\tThe " + row[settings["name"]] + " data row will not be considered. The in-vivo clearance value is too low at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " mL min-1 kg-1; the minimum permissable value is " + str(round(float(lowerValue), 5)) + " mL min-1 kg-1.")

							if float(row[settings[parameter + settings["prefix"]]]) > upperValue:
								addRow = False
								if someIncorrectData == False:
									print("")
								print("\tThe " + row[settings["name"]] + " data row will not be considered. The in-vivo clearance value is too high at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " mL min-1 kg-1; the maximum permissable value is " + str(round(float(upperValue), 5)) + " mL min-1 kg-1.")
												
					if parameter == settings["vText"]:
						units = [str.lower(x) for x in settings[settings["vText"] + settings["prefix"] + settings["unitsSuffix"]]]
						if str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) not in units:
							addRow = False
							if someIncorrectData == False:
								print("")
							print("\tThe " + row[settings["name"]] + " data row will not be considered. The units for the volume of distribution at steady state data are not right; the possible options include: " + str(settings[settings["vText"] + settings["prefix"] + settings["unitsSuffix"]]) + ".")		
						
						elif self.isFloat(row[settings[parameter + settings["prefix"]]]):
							# A lower and upper limit threshold applies to Vss (L kg-1)
							lowerValue = float(settings[settings["speciesName"] + settings["plasmaVolumeSuffix"]]) / float(settings[settings["speciesName"] + settings["bodyWeightSuffix"]])
							upperValue = float(settings["vUpperLimit"])
							
							if float(row[settings[parameter + settings["prefix"]]]) < lowerValue:
								addRow = False
								if someIncorrectData == False:
									print("")
								print("\tThe " + row[settings["name"]] + " data row will not be considered. The volume of distribution at steady state value is too low at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " L kg-1; the minimum permissable value is " + str(round(float(lowerValue), 5)) + " L kg-1, which reflects the plasma volume of the species being considered.")

							if float(row[settings[parameter + settings["prefix"]]]) > upperValue:
								addRow = False
								if someIncorrectData == False:
									print("")
								print("\tThe " + row[settings["name"]] + " data row will not be considered. The volume of distribution at steady state value is too high at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " L kg-1; the maximum permissable value is " + str(round(float(upperValue), 5)) + " L kg-1.")	
					
					if settings["levels"] == "free":
						if parameter == settings["ppbText"]:
							units = [str.lower(x) for x in settings[settings["ppbText"] + settings["prefix"] + settings["unitsSuffix"]]]
							if str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) not in units:
								addRow = False
								if someIncorrectData == False:
									print("")
								print("\tThe " + row[settings["name"]] + " data row will not be considered. The units for the plasma protein binding data are not right; the possible options include: " + str(settings[settings["ppbText"] + settings["prefix"] + settings["unitsSuffix"]]) + ".")
							
							elif self.isFloat(row[settings[parameter + settings["prefix"]]]):
								# A lower and upper limit threshold applies to ppb (% bound)
								lowerValue = float(settings["ppbLowerLimit"])
								upperValue = float(settings["ppbUpperLimit"])
								
								if str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) == "% bound":	
									if float(row[settings[parameter + settings["prefix"]]]) < lowerValue:
										addRow = False
										if someIncorrectData == False:
											print("")
										print("\tThe " + row[settings["name"]] + " data row will not be considered. The plasma protein binding value is too low at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " % bound; the minimum permissable value is " + str(round(float(lowerValue), 5)) + " % bound.")

									if float(row[settings[parameter + settings["prefix"]]]) > upperValue:
										addRow = False
										if someIncorrectData == False:
											print("")
										print("\tThe " + row[settings["name"]] + " data row will not be considered. The plasma protein binding value is too high at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " % bound; the maximum permissable value is " + str(round(float(upperValue), 5)) + " % bound.")

								elif str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) == "% free":	
									if 100 - float(row[settings[parameter + settings["prefix"]]]) < lowerValue:
										addRow = False
										if someIncorrectData == False:
											print("")
										print("\tThe " + row[settings["name"]] + " data row will not be considered. The plasma protein binding value is too high at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " % free; the maximum permissable value is " + str(round(100 - float(lowerValue), 5)) + " % free.")

									if 100 - float(row[settings[parameter + settings["prefix"]]]) > upperValue:
										addRow = False
										if someIncorrectData == False:
											print("")
										print("\tThe " + row[settings["name"]] + " data row will not be considered. The plasma protein binding value is too low at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " % free; the minimum permissable value is " + str(round(100 - float(upperValue), 5)) + " % free.")												

					if settings["ivOrPo"] == "po":
						if parameter == settings["caco2Text"]:
							units = [str.lower(x) for x in settings[settings["caco2Text"] + settings["prefix"] + settings["unitsSuffix"]]]
							if str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) not in units:
								addRow = False
								if someIncorrectData == False:
									print("")
								print("\tThe " + row[settings["name"]] + " data row will not be considered. The units for the Caco2 Papp A to B at pH 6.5 data are not right; the possible options include: " + str(settings[settings["caco2Text"] + settings["prefix"] + settings["unitsSuffix"]]) + ".")						
							
							elif self.isFloat(row[settings[parameter + settings["prefix"]]]):
								# A lower and upper limit threshold applies to Caco2_pH6.5_human (cm s-1)
								lowerValue = float(settings["caco2LowerLimit"])
								upperValue = float(settings["caco2UpperLimit"])
								
								if float(row[settings[parameter + settings["prefix"]]]) < lowerValue:
									addRow = False
									if someIncorrectData == False:
										print("")
									print("\tThe " + row[settings["name"]] + " data row will not be considered. The Caco2 Papp A to B at pH 6.5 value is too low at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 12)) + " cm s-1; the minimum permissable value is " + str(round(float(lowerValue), 12)) + " cm s-1.")

								if float(row[settings[parameter + settings["prefix"]]]) > upperValue:
									addRow = False
									if someIncorrectData == False:
										print("")
									print("\tThe " + row[settings["name"]] + " data row will not be considered. The Caco2 Papp A to B at pH 6.5 value is too high at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " cm s-1; the maximum permissable value is " + str(round(float(upperValue), 5)) + " cm s-1.")
													
						if parameter == settings["solubilityText"]:
							units = [str.lower(x) for x in settings[settings["solubilityText"] + settings["prefix"] + settings["unitsSuffix"]]]
							if str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) not in units:
								addRow = False
								if someIncorrectData == False:
									print("")
								print("\tThe " + row[settings["name"]] + " data row will not be considered. The units for the aqueous solubility (pH 7.4) data are not right; the possible options include: " + str(settings[settings["solubilityText"] + settings["prefix"] + settings["unitsSuffix"]]) + ".")									
							
							elif self.isFloat(row[settings[parameter + settings["prefix"]]]):
								# A lower and upper limit threshold applies to aqueous solubility (pH 7.4) (M)
								lowerValue = float(settings["solubilityLowerLimit"])
								upperValue = float(settings["solubilityUpperLimit"])
								
								if float(row[settings[parameter + settings["prefix"]]]) < lowerValue:
									addRow = False
									if someIncorrectData == False:
										print("")
									print("\tThe " + row[settings["name"]] + " data row will not be considered. The aqueous solubility (pH 7.4) value is too low at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 12)) + " M; the minimum permissable value is " + str(round(float(lowerValue), 12)) + " M.")

								if float(row[settings[parameter + settings["prefix"]]]) > upperValue:
									addRow = False
									if someIncorrectData == False:
										print("")
									print("\tThe " + row[settings["name"]] + " data row will not be considered. The aqueous solubility (pH 7.4) value is too high at " + str(round(float(row[settings[parameter + settings["prefix"]]]), 5)) + " M; the maximum permissable value is " + str(round(float(upperValue), 5)) + " M.")
													
			# For diprotic compounds check that pka_a1 >= pka_a2 or that pka_b1 >= pka_b2 
			if addRow == True and settings["ivOrPo"] == "po":
				if row[settings["chargeTypeText"]].lower() == settings["diAcidText"]:
					if row[settings["pKaA2"]] > row[settings["pKaA1"]]:
						addRow = False
						if someIncorrectData == False:
							print("")
						print("\tThe " + row[settings["name"]] + " data row will not be considered. The pKa_A2 value is greater than the pKa_A1 which is not permitted.")
				
				elif row[settings["chargeTypeText"]].lower() == settings["diBaseText"]: 
					if row[settings["pKaB2"]] > row[settings["pKaB1"]]:
						addRow = False
						if someIncorrectData == False:
							print("")
						print("\tThe " + row[settings["name"]] + " data row will not be considered. The pKa_B2 value is greater than the pKa_B1 which is not permitted.")		
					
			# Return output
			return addRow
		
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
	

	# Generate an error scenario row
	def errorScenarioRow(self, settings, row, referenceCount, groupReferenceCount, i):
		try:
			import math
			import random
			import sys

			newRow = row.copy()
			newRow[settings["reference"]] = referenceCount + i
			newRow[settings["groupReference"]] = groupReferenceCount
			newRow[settings["name"]] = row[settings["name"]] + settings["nameSubstring"] + str(i)

			#
			# The script allows one column for the an inputted parameter's value. In the case of error scenarios, the standard deviation to use will depend on how much other data is provided in the input file:
			#
			#	Scenario 1: No standard deviation or similarity columns exist - use default standard deviation
			#
			#	Scenario 2: Standard deviation column exists but no similarity column - if possible use standard deviation value if not use default standard deviation
			#
			#	Scenario 3: No standard deviation column but similarity column exists - estimate standard deviation from similarity - if possible use similarity score to estimate RMSEP if not use default RMSEP
			#
			#	Scenario 4: Both standard deviation or similarity columns exist - prioritise standard deviation values over similarity and where necessary default to standard deviation
			#
			# Note, in the case of scenario 1 and 3, the script add to the row dictionary a standard deviation field set to None.
			#
	
			for parameter in settings["revisedErrorParameters"]:				
				value = float(row[settings[parameter + settings["prefix"]]])
				
				if row[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]] == None and settings[parameter + settings["prefix"]] + settings["similaritySuffix"] not in row:
					# Scenario 1
					predictionStandardDeviation = settings["defaultParameterStandardDeviation"]
					
					# Update existing standard deviation value
					newRow[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]] = predictionStandardDeviation
					
				elif settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"] in row and settings[parameter + settings["prefix"]] + settings["similaritySuffix"] not in row:
					# Scenario 2
					if self.isFloat(row[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]]):
						# Standard deviation value is a valid number
						predictionStandardDeviation = float(row[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]])
						
						# No need to update existing standard deviation value
					
					else:
						# Standard deviation value isn't a valid number - use default standard deviation value
						predictionStandardDeviation = settings["defaultParameterStandardDeviation"]
						
						# Update existing standard deviation value
						newRow[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]] = predictionStandardDeviation
				
				elif row[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]] == None and settings[parameter + settings["prefix"]] + settings["similaritySuffix"] in row:
					# Scenario 3
					if self.isFloat(row[settings[parameter + settings["prefix"]] + settings["similaritySuffix"]]):
						# Similarity value is a valid number - use it
						predictionStandardDeviation = self.similarityErrorConversion(settings, parameter, float(row[settings[parameter + settings["prefix"]] + settings["similaritySuffix"]]))
						
						# No need to update existing similarity value
						
					else:
						# Similarity value isn't a valid number - use default RMSEP value by  setting the similarity value to 0.0
						predictionStandardDeviation = self.similarityErrorConversion(settings, parameter, 0.0)
						
						# To make it clear that the default RMSEP value has been used, set the similarity value to 0.0
						newRow[settings[parameter + settings["prefix"]] + settings["similaritySuffix"]] = 0.0
					
					# Update existing standard deviation value
					newRow[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]] = predictionStandardDeviation
				
				elif settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"] in row and settings[parameter + settings["prefix"]] + settings["similaritySuffix"] in row:
					# Scenario 4
					if self.isFloat(row[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]]):
						# Standard deviation value is a valid number - use it
						predictionStandardDeviation = float(row[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]])
						
						# No need to update existing standard deviation value
						
						# To make it clear that the standard deviation value has been used, set the similarity value to ""
						newRow[settings[parameter + settings["prefix"]] + settings["similaritySuffix"]] = ""
					
					else:
						# Standard deviation value isn't a valid number
						if self.isFloat(row[settings[parameter + settings["prefix"]] + settings["similaritySuffix"]]):
							# Similarity value is a valid number - use it
							predictionStandardDeviation = self.similarityErrorConversion(settings, parameter, float(row[settings[parameter + settings["prefix"]] + settings["similaritySuffix"]]))
							
							# Update existing standard deviation value
							newRow[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]] = predictionStandardDeviation
							
							# No need to update existing similarity value
					
						else:
							# Similarity value isn't a valid number - use default standard deviation value
							predictionStandardDeviation = settings["defaultParameterStandardDeviation"]
							
							# Update existing standard deviation value
							newRow[settings[parameter + settings["prefix"]] + settings["standardDeviationSuffix"]] = predictionStandardDeviation
							
							# To make it clear that the standard deviation value has been used, set the similarity value to ""
							newRow[settings[parameter + settings["prefix"]] + settings["similaritySuffix"]] = ""


				if parameter == settings["clText"]:
					random.seed()	
														
					# Convert to logarithmic base-10, apply permutation and take anti-logarithmic base-10
					newValue = math.pow(10, float(random.gauss(float(math.log10(value)), float(predictionStandardDeviation))))	
				
				elif parameter == settings["vText"]:						
					random.seed()
					
					# Define a lower value based on minimum Vss (L)
					lowerValue = float(settings[settings["speciesName"] + settings["plasmaVolumeSuffix"]]) / float(settings[settings["speciesName"] + settings["bodyWeightSuffix"]])
					
					# Convert to logarithmic base-10, apply permutation and take anti-logarithmic base-10	
					newValue = math.pow(10, float(random.gauss(float(math.log10(value)), float(predictionStandardDeviation))))

					# Check newValue against lowerValue
					if float(newValue) < float(lowerValue):
						newValue = float(lowerValue)

				elif parameter == settings["caco2Text"]:
					random.seed()						
					
					# Convert to logarithmic base-10, apply permutation and take anti-logarithmic base-10	
					newValue = math.pow(10, float(random.gauss(float(math.log10(value)), float(predictionStandardDeviation))))
											
				elif parameter == settings["solubilityText"]:
					random.seed()					
	
					# Convert to logarithmic base-10, apply permutation and take anti-logarithmic base-10
					newValue = math.pow(10, float(random.gauss(float(math.log10(value)), float(predictionStandardDeviation))))

				elif parameter == settings["ppbText"]:
					random.seed()
					
					if str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) == "% bound":	
						# Convert to  log10(%bound/%free), apply permutation and convert back to original units								
						x = float(random.gauss(float(math.log10(value / (100 - value))), float(predictionStandardDeviation)))
						y = float(math.pow(10, x))
						newValue = float((100 * y) / (1 + y))
						
					elif str.lower(row[settings[parameter + settings["prefix"]] + settings["unitsSuffix"]]) == "% free":			
						# Convert to  log10(%bound/%free), apply permutation and convert back to original units
						x = float(random.gauss(float(math.log10((100 - value) / value)), float(predictionStandardDeviation)))
						y = float(math.pow(10, x))
						newValue = float(100 / (1 + y))

				newRow[settings[parameter + settings["prefix"]]] = newValue
	
			return newRow

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
			
		finally:
			del newRow


	# Is float
	def isFloat(self, value):
		try:
			float(value)
			if (value == 'nan') or (value == 'inf') or (value * -1 == 'inf') or (value < 0):
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


	# Similarity error conversion
	def similarityErrorConversion(self, settings, parameter, similarityValue):
		try:
			import math
			
			useDefault = False

			if settings["parameterText"] in settings["rmsepDictionary"]:
				if parameter in settings["rmsepDictionary"][settings["parameterText"]]:
					rmsepValue = settings["rmsepDictionary"][settings["rmsepOverallText"]][settings["rmsepDictionary"][settings["parameterText"]].index(parameter)]
					
					if 0.0 < float(similarityValue) <= 0.5:
						if settings["rmsepSimilarityScore0p5Text"] in settings["rmsepDictionary"]:
							rmsepValue = settings["rmsepDictionary"][settings["rmsepSimilarityScore0p5Text"]][settings["rmsepDictionary"][settings["parameterText"]].index(parameter)]
	
					elif 0.5 < float(similarityValue) <= 0.6:
						if settings["rmsepSimilarityScore0p6Text"] in settings["rmsepDictionary"]:
							rmsepValue = settings["rmsepDictionary"][settings["rmsepSimilarityScore0p6Text"]][settings["rmsepDictionary"][settings["parameterText"]].index(parameter)]
					
					elif 0.6 < float(similarityValue) <= 0.7:
						if settings["rmsepSimilarityScore0p7Text"] in settings["rmsepDictionary"]:
							rmsepValue = settings["rmsepDictionary"][settings["rmsepSimilarityScore0p7Text"]][settings["rmsepDictionary"][settings["parameterText"]].index(parameter)]
					
					elif 0.7 < float(similarityValue) <= 0.8:
						if settings["rmsepSimilarityScore0p8Text"] in settings["rmsepDictionary"]:
							rmsepValue = settings["rmsepDictionary"][settings["rmsepSimilarityScore0p8Text"]][settings["rmsepDictionary"][settings["parameterText"]].index(parameter)]
	
					elif 0.8 < float(similarityValue) <= 0.9:
						if settings["rmsepSimilarityScore0p9Text"] in settings["rmsepDictionary"]:
							rmsepValue = settings["rmsepDictionary"][settings["rmsepSimilarityScore0p9Text"]][settings["rmsepDictionary"][settings["parameterText"]].index(parameter)]
					
					elif 0.9 < float(similarityValue) <= 1.0:
						if settings["rmsepSimilarityScore1p0Text"] in settings["rmsepDictionary"]:
							rmsepValue = settings["rmsepDictionary"][settings["rmsepSimilarityScore1p0Text"]][settings["rmsepDictionary"][settings["parameterText"]].index(parameter)]
									
					if not self.isFloat(rmsepValue):
						useDefault = True
							
				else:
					useDefault = True
			
			else:
				useDefault = True
			
			if useDefault == True:
				rmsepValue = settings["qsarDefaultRmsep"]
				
			# 
			# Relating rmsep to a prediction standard deviation:
			# A rmsep considers the error between the predictions and the observed value and the prediction standard deviation considers the error in the prediction.
			# To simplify, rmsep can be assumed to be a function of the experimental standard deviation and the prediction standard deviation - rearrange following empirical relationship: 
			#
			#		rmsepValue = (experimentalStandardDeviation^2 + predictionStandardDeviation^2)^0.5
			#		
			#		predictionStandardDeviation = (rmsepValue^2 - experimentalStandardDeviation^2)^0.5
			#

			predictionVariance = math.pow(float(rmsepValue), 2) - math.pow(float(settings["qsarExperimentalStandardDeviation"]),2)
			
			predictionStandardDeviation = math.pow(float(predictionVariance), 0.5)

			return predictionStandardDeviation
			
		except ValueError:
			print("The rmsep value is smaller than the assumed generic logarithmic base-10 experimental standard deviation associated to measured data. The standard deviation returned will be based solely on the assumed generic logarithmic base-10 experimental standard deviation.")
			
			predictionStandardDeviation = settings["qsarExperimentalStandardDeviation"]
			return predictionStandardDeviation

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

