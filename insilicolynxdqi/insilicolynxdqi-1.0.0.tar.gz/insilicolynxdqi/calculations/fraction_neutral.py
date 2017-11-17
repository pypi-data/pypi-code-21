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

description = "The insilicolynxdqi.calculations folder fraction_neutral.py module"

class FractionNeutral:	
	# Class variables


	# __init__	
	def __init__(self, settings):
		try:
			self.DefaultCalculationMethodText = settings["defaultCalculationMethodText"]
			self.ChargeTypeText = settings["chargeTypeText"]
			self.DiAcidText = settings["diAcidText"]
			self.DiBaseText = settings["diBaseText"]
			self.File = settings["dataFile"]
			self.MonoAcidText = settings["monoAcidText"]
			self.MonoBaseText = settings["monoBaseText"]
			self.NameIndex = settings["name"]
			self.NeutralText = settings["neutralText"]
			self.PKaA1Text = settings["pKaA1Text"]
			self.PKaA2Text = settings["pKaA2Text"]
			self.PKaB1Text = settings["pKaB1Text"]
			self.PKaB2Text = settings["pKaB2Text"]		
			self.ZwitterionText = settings["zwitterionText"]
		
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
			return "The insilicolynxdqi FractionNeutral class"
		
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
	def processFile(self, approach, units, pH):
		try:
			import csv

			parameterValues = {}
			parameterUnits = {}
			fileToRead = open(self.File, 'r')
			with fileToRead:
				reader = csv.DictReader(fileToRead, delimiter="\t")
				for row in reader:
					if approach == self.DefaultCalculationMethodText:
						parameterValues.update({row[self.NameIndex]:self.fractionNeutral(pH, row)})
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
	
					
	# Fraction neutral
	def fractionNeutral(self, pH, rowData):
		try:
			import math
			
			if rowData[self.ChargeTypeText] == self.NeutralText:
				# Return output
				return 1
			
			if rowData[self.ChargeTypeText] == self.MonoAcidText:
				# Return output
				return (1 / (1 + math.pow(10,(float(pH) - float(rowData[self.PKaA1Text])))))
			
			if rowData[self.ChargeTypeText] == self.MonoBaseText:
				# Return output
				return (1 / (1 + math.pow(10,(float(rowData[self.PKaB1Text]) - float(pH)))))
			
			if rowData[self.ChargeTypeText] == self.ZwitterionText:
				# Return output
				return (1 / (1 + math.pow(10,(float(rowData[self.PKaB1Text]) - float(rowData[self.PKaA1Text]))) + math.pow(10,(float(rowData[self.PKaB1Text]) - float(pH))) + math.pow(10,(float(pH) - float(rowData[self.PKaA1Text])))))
			
			if rowData[self.ChargeTypeText] == self.DiAcidText:
				# Return output
				return (1 / (1 + math.pow(10,(float(pH) - float(rowData[self.PKaA1Text]))) + math.pow(10,((2 * float(pH)) - float(rowData[self.PKaA1Text]) - float(rowData[self.PKaA2Text])))))
			
			if rowData[self.ChargeTypeText] == self.DiBaseText:
				# Return output
				return (1 / (1 + math.pow(10,(float(rowData[self.PKaB1Text]) - float(pH))) + math.pow(10,(float(rowData[self.PKaB1Text]) + float(rowData[self.PKaB2Text]) - (2 * float(pH))))))
		
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
			
