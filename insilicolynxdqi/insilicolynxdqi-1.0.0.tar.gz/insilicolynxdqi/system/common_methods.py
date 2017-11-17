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

description = "The insilicolynxdqi.system folder common_methods.py module"

class CommonMethods:
	# Class variables


	# __init__
	def __init__(self):
		pass


	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi CommonMethods class"
		
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


	# Add parameters to the dictionary of values
	def addParameters1C(self, settings, constants, dictValues, columnHeaderSuffix):
		try:
			if settings["ivOrPo"] == "iv":
				molecularWeight = constants[0]
				k4 = constants[1]
				t3 = constants[2]
				t4 = constants[3]
				dose = constants[4]		
			elif settings["ivOrPo"] == "po":
				molecularWeight = constants[0]
				k4 = constants[1]
				t1 = constants[2]
				t2 = constants[3]
				t3 = constants[4]
				t4 = constants[5]
				fh = constants[6]	
			
			# Add molecularWeight
			dictValues.update({settings["molecularWeightText"] + columnHeaderSuffix: float(molecularWeight)})
							
			# Add k4 rate in s-1 - passed in min-1
			dictValues.update({settings["eliminationRateConstantText"] + settings["speciesName"] + columnHeaderSuffix: float(k4) / 60})
			dictValues.update({settings["eliminationRateConstantText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["sMinus1UnitsText"]})		

			# Add t3 in hours - passed in min
			dictValues.update({settings["doseIntervalText"] + settings["speciesName"] + columnHeaderSuffix: float(t3) / 60})
			dictValues.update({settings["doseIntervalText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})
			
			# Add t4 in hours - passed in min
			dictValues.update({settings["simulationLengthText"] + settings["speciesName"] + columnHeaderSuffix: float(t4) / 60})
			dictValues.update({settings["simulationLengthText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})
			
			if settings["ivOrPo"] == "iv":
				# Add dose in mg - passed in mg
				dictValues.update({settings["doseText"] + settings["speciesName"] + columnHeaderSuffix: float(dose)})
				dictValues.update({settings["doseText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["mgUnitsText"]})
			elif settings["ivOrPo"] == "po":
				# Add t1 in hours - passed in min
				dictValues.update({settings["absorptionDelayText"] + settings["speciesName"] + columnHeaderSuffix: float(t1) / 60})
				dictValues.update({settings["absorptionDelayText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})
				
				# Add t2 in hours - passed in min
				dictValues.update({settings["intestinalTransitTimeText"] + settings["speciesName"] + columnHeaderSuffix: float(t2) / 60})
				dictValues.update({settings["intestinalTransitTimeText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})
								
				# Add fh
				dictValues.update({settings["firstPassFractionHepaticMetabolisedText"] + settings["speciesName"] + columnHeaderSuffix:float(fh)})
				dictValues.update({settings["firstPassFractionHepaticMetabolisedText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["naUnitsText"]})
			
			# Return output	
			return dictValues

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


	# Add additional parameters to the dictionary of values
	def addParameters2C(self, settings, constants, dictValues, columnHeaderSuffix):
		try:
			if settings["ivOrPo"] == "iv":
				molecularWeight = constants[0]
				k2 = constants[1]
				k3 = constants[2]
				k4 = constants[3]
				t3 = constants[4]
				t4 = constants[5]
				dose = constants[6]
			elif settings["ivOrPo"] == "po":
				molecularWeight = constants[0]
				k2 = constants[1]
				k3 = constants[2]
				k4 = constants[3]
				t1 = constants[4]
				t2 = constants[5]
				t3 = constants[6]
				t4 = constants[7]
				fh = constants[8]

			# Add molecularWeight
			dictValues.update({settings["molecularWeightText"] + columnHeaderSuffix: float(molecularWeight)})
			
			# Add k2 rate in s-1 - passed in min-1
			dictValues.update({settings["centralToPeripheralCompartmentRateConstantText"] + settings["speciesName"] + columnHeaderSuffix: float(k2) / 60})
			dictValues.update({settings["centralToPeripheralCompartmentRateConstantText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["sMinus1UnitsText"]})
			
			# Add k3 rate in s-1 - passed in min-1
			dictValues.update({settings["peripheralToCentralCompartmentRateConstantText"] + settings["speciesName"] + columnHeaderSuffix: float(k3) / 60})
			dictValues.update({settings["peripheralToCentralCompartmentRateConstantText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["sMinus1UnitsText"]})
			
			# Add k4 rate in s-1 - passed in min-1
			dictValues.update({settings["eliminationRateConstantText"] + settings["speciesName"] + columnHeaderSuffix: float(k4) / 60})
			dictValues.update({settings["eliminationRateConstantText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["sMinus1UnitsText"]})
			
			# Add t3 in hours - passed in min
			dictValues.update({settings["doseIntervalText"] + settings["speciesName"] + columnHeaderSuffix: float(t3) / 60})
			dictValues.update({settings["doseIntervalText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})
			
			# Add t4 in hours - passed in min
			dictValues.update({settings["simulationLengthText"] + settings["speciesName"] + columnHeaderSuffix: float(t4) / 60})
			dictValues.update({settings["simulationLengthText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})

			if settings["ivOrPo"] == "iv":
				# Add dose in mg - passed in mg
				dictValues.update({settings["doseText"] + settings["speciesName"] + columnHeaderSuffix: float(dose)})
				dictValues.update({settings["doseText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["mgUnitsText"]})
			elif settings["ivOrPo"] == "po":
				# Add t1 in hours - passed in min
				dictValues.update({settings["absorptionDelayText"] + settings["speciesName"] + columnHeaderSuffix: float(t1) / 60})
				dictValues.update({settings["absorptionDelayText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})
				
				# Add t2 in hours - passed in min
				dictValues.update({settings["intestinalTransitTimeText"] + settings["speciesName"] + columnHeaderSuffix: float(t2) / 60})
				dictValues.update({settings["intestinalTransitTimeText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["hUnitsText"]})
								
				# Add fh
				dictValues.update({settings["firstPassFractionHepaticMetabolisedText"] + settings["speciesName"] + columnHeaderSuffix:float(fh)})
				dictValues.update({settings["firstPassFractionHepaticMetabolisedText"] + settings["speciesName"] + settings["unitsSuffix"] + columnHeaderSuffix:settings["naUnitsText"]})

			# Return output
			return dictValues

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
			

	# Add raw parameters to the dictionary of values
	def addRawParameters1C(self, settings, constants):
		try:
			if settings["ivOrPo"] == "iv":
				cl = constants[0]
				vss = constants[1]
				k4 = constants[2]
				t3 = constants[3]
				t4 = constants[4]
			elif settings["ivOrPo"] == "po":
				cl = constants[0]
				vss = constants[1]
				k4 = constants[2]
				t1 = constants[3]
				t2 = constants[4]
				t3 = constants[5]
				t4 = constants[6]
				fh = constants[7]
				solubility6P5Saturated = constants[8]
				k1 = constants[9]
				t12Condition = constants[10]
				t12Saturated = constants[11]
				bt12Saturated = constants[12]
				bt2 = constants[13]			
					
			rawValues = {}		
			# Add cl - passed in L min-1
			rawValues.update({settings["clearanceText"] + settings["speciesName"] + "_(" + settings["lMinMinus1UnitsText"].replace(" ","_") + ")":float(cl)})
			
			# Add vss - passed in L
			rawValues.update({settings["vssText"] + settings["speciesName"] + "_(" + settings["lUnitsText"].replace(" ","_") + ")":float(vss)})
		
			# Add k4 rate in s-1 - passed in min-1
			rawValues.update({settings["eliminationRateConstantText"] + settings["speciesName"] + "_(" + settings["sMinus1UnitsText"].replace(" ","_") + ")":float(k4) / 60})
			
			# Add t3 in hours - passed in min
			rawValues.update({settings["doseIntervalText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")": float(t3) / 60})
			
			# Add t4 in hours - passed in min
			rawValues.update({settings["simulationLengthText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")": float(t4) / 60})

			if settings["ivOrPo"] == "po":
				# Add t1 in hours - passed in min
				rawValues.update({settings["absorptionDelayText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")":float(t1) / 60})
				
				# Add t2 in hours - passed in min
				rawValues.update({settings["intestinalTransitTimeText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")":float(t2) / 60})

				# Add fh
				rawValues.update({settings["firstPassFractionHepaticMetabolisedText"] + settings["speciesName"]:float(fh)})	

				# Add solubility6P5Saturated in mg - passed in mg
				rawValues.update({settings["solubility6P5saturatedText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(solubility6P5Saturated)})
	
				# Add k1 rate in s-1 - passed in min-1
				rawValues.update({settings["absorptionRateConstantText"] + settings["speciesName"] + "_(" + settings["sMinus1UnitsText"].replace(" ","_") + ")":float(k1) / 60})
			
				# Add t12Condition
				rawValues.update({settings["absorptionSaturationConditionText"] + settings["speciesName"]:t12Condition})
			
				# Add t12Saturated in hours - passed in min
				rawValues.update({settings["absorptionSaturatedTimeText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")": float(t12Saturated) / 60})
				
				# Add bt12Saturated in mg - passed in mg
				rawValues.update({settings["amountTransferredToBodyUnderSaturatedConditionsText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(bt12Saturated)})
				
				# Add bt2 in mg - passed in mg
				rawValues.update({settings["amountTransferredToBodyUnderAbsorptionConditionsText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(bt2)})
			
			# Return output
			return rawValues

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


	# Add raw parameters to the dictionary of values
	def addRawParameters2C(self, settings, constants):
		try:
			if settings["ivOrPo"] == "iv":
				cl = constants[0]
				vss = constants[1]
				vcentral = constants[2]
				k2 = constants[3]
				k3 = constants[4]
				k4 = constants[5]
				vterminal = constants[6]
				alpha = constants[7]
				beta = constants[8]
				t3 = constants[9]
				t4 = constants[10]
			elif settings["ivOrPo"] == "po":
				cl = constants[0]
				vss = constants[1]
				vcentral = constants[2]
				k2 = constants[3]
				k3 = constants[4]
				k4 = constants[5]
				vterminal = constants[6]
				alpha = constants[7]
				beta = constants[8]
				t1 = constants[9]
				t2 = constants[10]
				t3 = constants[11]
				t4 = constants[12]
				fh = constants[13]
				solubility6P5Saturated = constants[14]
				k1 = constants[15]
				t12Condition = constants[16]
				t12Saturated = constants[17]
				bt12Saturated = constants[18]
				bt2 = constants[19]
				ct12Saturated = constants[20]
				ct2 = constants[21]
	
			rawValues = {}			
			# Add cl - passed in L min-1
			rawValues.update({settings["clearanceText"] + settings["speciesName"] + "_(" + settings["lMinMinus1UnitsText"].replace(" ","_") + ")":float(cl)})
			
			# Add vss - passed in L
			rawValues.update({settings["vssText"] + settings["speciesName"] + "_(" + settings["lUnitsText"].replace(" ","_") + ")":float(vss)})
			
			# Add vcentral - passed in L
			rawValues.update({settings["vcentralText"] + settings["speciesName"] + "_(" + settings["lUnitsText"].replace(" ","_") + ")":float(vcentral)})
					
			# Add k2 rate in s-1 - passed in min-1
			rawValues.update({settings["centralToPeripheralCompartmentRateConstantText"] + settings["speciesName"] + "_(" + settings["sMinus1UnitsText"].replace(" ","_") + ")":float(k2) / 60})
			
			# Add k3 rate in s-1 - passed in min-1
			rawValues.update({settings["peripheralToCentralCompartmentRateConstantText"] + settings["speciesName"] + "_(" + settings["sMinus1UnitsText"].replace(" ","_") + ")":float(k3) / 60})
			
			# Add k4 rate in s-1 - passed in min-1
			rawValues.update({settings["eliminationRateConstantText"] + settings["speciesName"] + "_(" + settings["sMinus1UnitsText"].replace(" ","_") + ")":float(k4) / 60})
			
			# Add vterminal - passed in L
			rawValues.update({settings["vterminalText"] + settings["speciesName"] + "_(" + settings["lUnitsText"].replace(" ","_") + ")":float(vterminal)})
			
			# Add alpha
			rawValues.update({settings["alphaText"] + settings["speciesName"]:float(alpha)})
				
			# Add beta
			rawValues.update({settings["betaText"] + settings["speciesName"]:float(beta)})
			
			# Add t3 in hours - passed in min
			rawValues.update({settings["doseIntervalText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")": float(t3) / 60})
			
			# Add t4 in hours - passed in min
			rawValues.update({settings["simulationLengthText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")": float(t4) / 60})
			
			if settings["ivOrPo"] == "po":
				# Add t1 in hours - passed in min
				rawValues.update({settings["absorptionDelayText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")":float(t1) / 60})
				
				# Add t2 in hours - passed in min
				rawValues.update({settings["intestinalTransitTimeText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")":float(t2) / 60})

				# Add fh
				rawValues.update({settings["firstPassFractionHepaticMetabolisedText"] + settings["speciesName"]:float(fh)})
				
				# Add solubility6P5Saturated in mg - passed in mg
				rawValues.update({settings["solubility6P5saturatedText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(solubility6P5Saturated)})

				# Add k1 rate in s-1 - passed in min-1
				rawValues.update({settings["absorptionRateConstantText"] + settings["speciesName"] + "_(" + settings["sMinus1UnitsText"].replace(" ","_") + ")":float(k1) / 60})
			
				# Add t12Condition
				rawValues.update({settings["absorptionSaturationConditionText"] + settings["speciesName"]:t12Condition})
			
				# Add t12Saturated in hours - passed in min
				rawValues.update({settings["absorptionSaturatedTimeText"] + settings["speciesName"] + "_(" + settings["hUnitsText"].replace(" ","_") + ")": float(t12Saturated) / 60})
				
				# Add bt12Saturated in mg - passed in mg
				rawValues.update({settings["amountTransferredToCentralCompartmentUnderSaturatedConditionsText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(bt12Saturated)})
				
				# Add bt2 in mg - passed in mg
				rawValues.update({settings["amountTransferredToCentralCompartmentUnderAbsorptionConditionsText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(bt2)})

				# Add ct12Saturated in mg - passed in mg
				rawValues.update({settings["amountTransferredToPeripheralCompartmentUnderSaturatedConditionsText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(ct12Saturated)})
				
				# Add ct2 in mg - passed in mg
				rawValues.update({settings["amountTransferredToPeripheralCompartmentUnderAbsorptionConditionsText"] + settings["speciesName"] + "_(" + settings["mgUnitsText"].replace(" ","_") + ")":float(ct2)})			
			
			# Return output
			return rawValues

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
	
	
	# Check value
	def checkValue(self, value):
		try:
			if float(value) > 0:
				return "fine"

			else:
				return 'nan'
			
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
			
			
	# Create time vector
	def createTimeVector(self, t1, t2, t3, t4, settings):
		try:
			import random
		
			if int(t4) < int(settings["timeInterval"]):
				import sys
				print("\nThe simulation length (i.e., " + str(int(t4)) + " minutes) is less than the time interval of " + str(int(settings["timeInterval"])) + " minutes.\nExiting.\n")
				raise sys.exit(0)
			
			# Specifiy dose times for the simulation
			doseTimes = range(int(0), int(t4), int(t3))
			
			# Specifiy t1 times for the simulation
			t1Times = range(int(t1), int(t4), int(t3))
			
			# Specifiy t2 times for the simulation
			t2Times = range(int(t2), int(t4), int(t3))

			# Specifiy "t1 + t2" times for the simulation
			t12Times = range(int(t1+t2), int(t4), int(t3))
			
			# Create a list of time points regularly spaced
			timePoints1 = range(int(1), int(t4), int(settings["timeInterval"]))
			
			# Create a list, half the size to timePoints1 of time points randomly spaced
			timePoints2 = random.sample(range(int(1), int(t4), int(1)),int(int(t4)/(2 * int(settings["timeInterval"]))))
			
			combinedTimes = list(doseTimes) + list(t1Times) + list(t2Times) + list(t12Times) + list(timePoints1) + list(timePoints2)
			combinedTimes.append(int(t4))
			
			timeVector = []
			[timeVector.append(x) if x not in timeVector else '' for x in combinedTimes]
			timeVector.sort(key=int)
			
			# Determine times for a AUC calculations - interested in AUC in between two doses when steady state conditions can be approximated
			timesAUC = {}
			if len(doseTimes) > 1:
				# The simulation has at least one full dose
				if int(t4) - int(doseTimes[-1]) < int(t3):
					# The last dose does not run for a full interval - use times for the previous dose
					for i in range(0,len(doseTimes)-1,1):
						timesAUC.update({i:[int(doseTimes[-2 - i]), int(doseTimes[-1 - i])]})
				elif int(t4) - int(doseTimes[-1]) == int(t3):
					for i in range(0,len(doseTimes),1):
						timesAUC.update({i:[int(doseTimes[-1 - i]), int(t4) - (i * int(t3))]})
			else:
				timesAUC.update({0:[int(doseTimes[-1]), int(t4)]})
			
			# Return output				
			return doseTimes, timeVector, timesAUC

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


	# Determine extreme values
	def extremeValues(self, timeVector, t1, valuesVector, doseTimes):
		try:
			i = 0
			for index, t in enumerate(timeVector):
				if t <= int(t1):
					i += 1
			revisedValuesVector = valuesVector[i:]
			revisedTimeVector = timeVector[i:]
						
			if len(doseTimes) >= 3:
				# Create a revised vector (list): since the last two doses
				selectedRevisedValuesVector = revisedValuesVector[revisedTimeVector.index(doseTimes[len(doseTimes)-2]):]
				
			else:
				# Create a revised vector (list): include all data
				selectedRevisedValuesVector = revisedValuesVector
			
			# Remove any 0 values
			selectedRevisedValuesVectorMinusZeros = [x for x in selectedRevisedValuesVector if x > 0]
			
			if len(selectedRevisedValuesVectorMinusZeros) > 0:
				# Determine highest and lowest amounts achieved
				maxValue = max(selectedRevisedValuesVectorMinusZeros)
				minValue = min(selectedRevisedValuesVectorMinusZeros)
			
			else:
				maxValue = 'nan'
				minValue = 'nan'
				
			# Return output		
			return maxValue, minValue

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
			
	# Determine alpha and beta values
	def setAlphaBeta(self, k2, k3, k4):
		try:
			import math
			
			alphaPlusBeta = float(k2) + float(k3) + float(k4)
			alphaTimesBeta = float(k3) * float(k4)
			a = 1
			b = -1 * float(alphaPlusBeta)
			c = float(alphaTimesBeta)
			alpha =((-1 * float(b)) + math.pow((math.pow(float(b),2) - (4 * float(a) * float(c))),0.5)) / (2 * float(a))
			beta =((-1 * float(b)) - math.pow((math.pow(float(b),2) - (4 * float(a) * float(c))),0.5)) / (2 * float(a))
			
			# Return output
			return alpha, beta

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


	# Set fraction removed due to first past hepatic metabolism	
	def setFh(self, cl, settings):
		try:
			# Units for cl are L min-1, units for hepatic blood flow are ml min-1
			fh = 1 - ((float(cl) * 1000)/ (float(settings[settings["speciesName"] + settings["hepaticBloodFlowSuffix"]])))
			
			if fh <= settings["firstPassHepaticClearanceFractionLimit"]:
				fh = settings["firstPassHepaticClearanceFractionLimit"]
			
			# Return output	
			return fh
		
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


	# Set fu	
	def setFu(self, ppb, ppbUnits, settings):		
		try:
			if self.checkValue(ppb) == 'nan':
				import sys
				print("\t\tThe plasma protein binding value for this compound is an incompatible number (" + str(ppb) + "). The number needs to be a positive real number.\n\t\tExiting.\n")
				raise sys.exit(0)
			
			if ppbUnits.lower() == settings["percentBoundUnitsText"].lower():
				fu = (100 - float(ppb)) / 100
	
			elif ppbUnits.lower() == settings["percentFreeUnitsText"].lower():
				fu = float(ppb) / 100
	
			else:
				import sys
				print("\nThe units associated to plasma protein binding are not % bound or % free.\nExiting.\n")
				raise sys.exit(0)
						
			# Return output
			return fu
		
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
		

	# Set k1
	def setK1(self, k1, k1Units, settings):
		try:
			# Return k1 in units of min-1
			if k1Units.lower() == settings["sMinus1UnitsText"].lower():
				k1Revised = float(k1) * 60
			
			# Return output
			return k1Revised

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
			

	# Set k4	
	def setK4Rate(self, clRaw, clRawUnits, vssRaw, vssRawUnits, settings):
		try:
			if self.checkValue(clRaw) == 'nan':
				import sys
				print("\t\tThe in-vivo clearance value for this compound is an incompatible number (" + str(clRaw) + "). The number needs to be a positive real number.\n\t\tExiting.\n")
				raise sys.exit(0)
			
			if self.checkValue(vssRaw) == 'nan':
				import sys
				print("\t\tThe volume of distribution at steady state value for this compound is an incompatible number (" + str(vssRaw) + "). The number needs to be a positive real number.\n\t\tExiting.\n")
				raise sys.exit(0)
			
			# Return k4 in units of min-1
			if clRawUnits.lower() == settings["mLMinMinus1KgMinus1UnitsText"].lower() and vssRawUnits.lower() == settings["lKgMinus1UnitsText"].lower():
				# Determine cl in units L min-1
				cl = (float(clRaw) * float(settings[settings["speciesName"] + settings["bodyWeightSuffix"]])) / 1000
				
				# Determine vss in units of L
				vss = float(vssRaw) * float(settings[settings["speciesName"] + settings["bodyWeightSuffix"]])
				
				# Determine k4 in units min-1
				k4 = float(cl) / float(vss)
				
			else:
				import sys
				print("\nThe units associated to in vivo clearance are not ml min-1 kg-1 and/or the units associated to steady state volume of distribution are not l kg-1.\nExiting.\n")
				raise sys.exit(0)
						
			# Return output	
			return cl, vss, k4			
		
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
			

	# Set k2Rates, k3Rates, k4Rates
	def setK2K3K4Rates(self, clRaw, clRawUnits, vssRaw, vssRawUnits, settings):
		try:
			import math
			
			if self.checkValue(clRaw) == 'nan':
				import sys
				print("\t\tThe in-vivo clearance value for this compound is an incompatible number (" + str(clRaw) + "). The number needs to be a positive real number.\n\t\tExiting.\n")
				raise sys.exit(0)
			
			if self.checkValue(vssRaw) == 'nan':
				import sys
				print("\t\tThe volume of distribution at steady state value for this compound is an incompatible number (" + str(vssRaw) + "). The number needs to be a positive real number.\n\t\tExiting.\n")
				raise sys.exit(0)
				
			if clRawUnits.lower() == settings["mLMinMinus1KgMinus1UnitsText"].lower() and vssRawUnits.lower() == settings["lKgMinus1UnitsText"].lower():				
				# Determine cl in units L min-1
				cl = (float(clRaw) * float(settings[settings["speciesName"] + settings["bodyWeightSuffix"]])) / 1000
			
				# Determine vss in units of L
				vss = float(vssRaw) * float(settings[settings["speciesName"] + settings["bodyWeightSuffix"]])

				# Set the plasma volume
				plasmaVolume = float(settings[settings["speciesName"] + settings["plasmaVolumeSuffix"]])

				#
				# Create a list of possible vcentral values in units of L. Note, due to vss/vcentral - 1 = k2/k3, vcentral must be less than vss (i.e., vcentral < vss).
				#
				# Check that vss is greater than or equal to the plasma volume 	
				if float(vss) >= float(plasmaVolume):
					# Establish vcentral ranges based on vss
					vcentralLower = float(plasmaVolume)
					vcentralUpper = float(plasmaVolume) + ((float(vss) - float(plasmaVolume)) * float(settings["upperVcentralToVssRatio"]))
					vcentralMid = float(vcentralLower) + ((float(vcentralUpper) - float(vcentralLower)) / 2)
					
				else:
					# The vss is less than the available plasma volume and cannot continue
					import sys
					print("\nThis compound has a volume of distribution at steady state less than the plasma volume (i.e., less than " + str(float(plasmaVolume)) + " L).\nExiting.\n")
					raise sys.exit(0)	
				
				# Create vcentralList which looks like this: [vcentralLower, vcentralUpper, vcentralLower, vcentralUpper, vcentralMid].
				vcentralList = [float(vcentralLower), float(vcentralUpper), float(vcentralLower), float(vcentralUpper), float(vcentralMid)]
				
				k2K3RatioList = []
				k2List = []
				k3List = []
				k4List = []
				vterminalList = []
				
				for index, vcentral in enumerate(vcentralList):
					# Determine k2/k3 ratio
					k2K3 = (float(vss) / float(vcentral)) - 1
					
					# Estimate k4 = cl / vcentral
					k4 = float(cl) / float(vcentral)
					
					if index == 0 or index == 1:
						#
						# Determine the maximum value that lambda2 can be based on the lower vterminal / vss ratio
						#
						lambda2Max = float(cl) / (float(vss) * float(settings["vterminalToVssRatioLower"]))

						# Estimate k3 based on lambda2Max
						k3 = (float(lambda2Max) - (math.pow(float(lambda2Max),2) / float(k4))) / (1 - ((float(lambda2Max) / float(k4)) * (1 + float(k2K3))))
						
						# Determine k2 based on k3
						k2 = float(k3) * float(k2K3)
					
					elif index == 2 or index == 3:
						#
						# Determine the minimum value that lambda2 can be, based on the upper vterminal / vss ratio
						#
						lambda2Min = float(cl) / (float(vss) * float(settings["vterminalToVssRatioUpper"]))

						# Estimate k3 based on lambda2Min
						k3 = (float(lambda2Min) - (math.pow(float(lambda2Min),2) / float(k4))) / (1 - ((float(lambda2Min) / float(k4)) * (1 + float(k2K3))))
						
						# Determine k2 based on k3
						k2 = float(k3) * float(k2K3)

					elif index == 4:
						#
						# Determine the mid value that lambda2 can be, based on the mid value between the lower and upper vterminal / vss ratios
						#
						vterminalToVssRatioMid = float(settings["vterminalToVssRatioLower"]) + ((float(settings["vterminalToVssRatioUpper"]) - float(settings["vterminalToVssRatioLower"])) / 2)
						
						lambda2Min = float(cl) / (float(vss) * float(vterminalToVssRatioMid))

						# Estimate k3 based on lambda2Min
						k3 = (float(lambda2Min) - (math.pow(float(lambda2Min),2) / float(k4))) / (1 - ((float(lambda2Min) / float(k4)) * (1 + float(k2K3))))
						
						# Determine k2 based on k3
						k2 = float(k3) * float(k2K3)
					
					# Calculate vterminal
					i = float(k2) + float(k3) + float(k4)
					j = math.pow(float(i),2) - (4 * float(k3) * float(k4))
					lambda2 = 0.5 * (float(i) - math.sqrt(float(j)))
					vterminal = float(cl) / float(lambda2)
					
					k2K3RatioList.append(float(k2K3))
					# Rate units are min-1
					k2List.append(float(k2))
					k3List.append(float(k3))
					k4List.append(float(k4))
					# vterminal units are l
					vterminalList.append(float(vterminal))
					
			else:
				import sys
				print("\nThe units associated to in vivo clearance are not ml min-1 kg-1 and/or the units associated to steady state volume of distribution are not l kg-1.\nExiting.\n")	
				raise sys.exit(0)
						
			# Return output	
			return cl, vss, vcentralList, k2K3RatioList, k2List, k3List, k4List, vterminalList

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


	# Set solubility pH 6.5 (mg ml-1)
	def setSolubility6P5MgPerML(self, molWt, solubility6P5):
		try:
			solubility6P5MgPerML = float(solubility6P5) * float(molWt)
					
			# Return output
			return solubility6P5MgPerML
		
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
			
	
	# Set saturated solubility pH 6.5 (mg)
	def setSolubility6P5Saturated(self, solubility6P5MgPerML, settings):	
		try:
			solubility6P5Saturated = float(solubility6P5MgPerML) * float(settings[settings["speciesName"] + settings["intestinalFluidVolumeSuffix"]])
			
			# Return output
			return solubility6P5Saturated
		
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

	
	# Set t3 and t4
	def setT3T4(self, rowData, settings):
		try:
			doseIntervalSupplied = False
			doseIntervalUnitsSupplied = False
			simulationLengthSupplied = False
			simulationLengthUnitsSupplied = False
			for key in rowData:
				if key == settings["doseIntervalText"]:
					doseIntervalSupplied = True
				if key == settings["doseIntervalText"] + settings["unitsSuffix"]:
					doseIntervalUnitsSupplied = True
				if key == settings["simulationLengthText"]:
					simulationLengthSupplied = True
				if key == settings["simulationLengthText"]+ settings["unitsSuffix"]:
					simulationLengthUnitsSupplied= True
			
			if doseIntervalSupplied == True and doseIntervalUnitsSupplied == True:
				if rowData[settings["doseIntervalText"] + settings["unitsSuffix"]] == settings["sUnitsText"]:
					# dose interval in s
					t3 = rowData[settings["doseIntervalText"]] / 60	# Convert to min
				if rowData[settings["doseIntervalText"] + settings["unitsSuffix"]] == settings["minUnitsText"]:
					# dose interval in min
					t3 = rowData[settings["doseIntervalText"]]	# Already in min
				if rowData[settings["doseIntervalText"] + settings["unitsSuffix"]] == settings["hUnitsText"]:
					# dose interval in h
					t3 = rowData[settings["doseIntervalText"]] * 60	# Convert to min
			else:
				# Default value in h
				t3 = settings["doseInterval"] * 60	# Convert to min
			
			
			if simulationLengthSupplied == True and simulationLengthUnitsSupplied == True:
				if rowData[settings["simulationLengthText"] + settings["unitsSuffix"]] == settings["sUnitsText"]:
					# simulation length in s
					t4 = rowData[settings["simulationLengthText"]] / 60	# Convert to min
				if rowData[settings["simulationLengthText"] + settings["unitsSuffix"]] == settings["minUnitsText"]:
					# simulation length in min
					t4 = rowData[settings["simulationLengthText"]]	# Already in min
				if rowData[settings["simulationLengthText"] + settings["unitsSuffix"]] == settings["hUnitsText"]:
					# simulation length in h
					t4 = rowData[settings["simulationLengthText"]] * 60	# Convert to min
			else:
				# Default value in h
				t4 = settings["simulationLength"] * 60	# Convert to min
						
			# Return output
			return t3, t4		
		
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
			
