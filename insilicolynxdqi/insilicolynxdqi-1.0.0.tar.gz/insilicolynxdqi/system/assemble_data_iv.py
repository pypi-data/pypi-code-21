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

description = "The insilicolynxdqi.system folder assemble_data_iv.py module"

class AssembleDataIv:
	# Class variables


	# __init__
	def __init__(self, settings, dataFile, prefix, columnHeaderSuffix, option):
		try:
			self.ColumnHeaderSuffix = columnHeaderSuffix
			self.FileDataSet = dataFile
			self.GroupReference = settings["groupReference"]
			self.MolecularWeight = settings["molecularWeightText"]
			self.Name = settings["name"]
			self.NameSubstring = settings["nameSubstring"]
			self.Prefix = prefix
			self.Reference = settings["reference"]
			self.Smiles = settings["smiles"]
			self.Species = settings["speciesName"]
			self.YAxisTitleSubString = settings["quantityLabels"][option]
			
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
			return "The insilicolynxdqi AssembleDataIv class"
		
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
			
			
	# Assemble data
	def assembleData(self, dictData):
		try:
			import csv
			import sys
			
			# Open data file
			fileToRead = open(self.FileDataSet, 'r')
						
			referenceList = []
			nameList = []
			smilesExist = False
			molecularWeightExist = False
			assembledData = {}
			nameOrder = []
			with fileToRead:
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.	
				reader = csv.DictReader(fileToRead, delimiter="\t")	
				
				# Check if a self.Name column exists
				if self.Name not in reader.fieldnames:
					print("\n\tThe data file does not contain the correct column headers - please check before re-running.\n\tExiting.\n")
					raise sys.exit(0)
				
				# Check if a smiles string column exists
				if self.Smiles in reader.fieldnames:
					smilesList = []					
					smilesExist = True
				
				# Check if a molecular weight column exists
				if self.MolecularWeight in reader.fieldnames:
					molecularWeightList = []				
					molecularWeightExist = True
				
				for row in reader:
					#
					# Note, a data file can contain multiple row for the same compound.
					# In the first instance the name will be as entered and for subsequent occurences the name will have a suffix in the form: self.NameSubstring + number 
					# Check if the row is a unique compound or another instance of a compound that has already got some processed data associated to it
					#
					if str(row[self.Name].split(self.NameSubstring)[0]) + str(self.NameSubstring) + str(row[self.GroupReference]) in nameOrder:
						# Compound already got some processed data associated to it - append new data to the stored list within the assembledData dictionary
						cpd = assembledData[str(row[self.Name].split(self.NameSubstring)[0]) + str(self.NameSubstring) + str(row[self.GroupReference])][0]
						molecularWeight = assembledData[str(row[self.Name].split(self.NameSubstring)[0]) + str(self.NameSubstring) + str(row[self.GroupReference])][1]
						for index, item in enumerate(self.ColumnHeaderSuffix):
							if self.isFloat(row[self.Prefix + self.YAxisTitleSubString + self.Species + item]) == True:
								logValue = self.logValue(row[self.Prefix + self.YAxisTitleSubString + self.Species + item])
								if logValue != 'nan':
									cpd.append(float(logValue))	
						
						assembledData.update({str(row[self.Name].split(self.NameSubstring)[0]) + str(self.NameSubstring) + str(row[self.GroupReference]):[cpd, molecularWeight]})
					
					else:
						# New compound
						referenceList.append(row[self.GroupReference])
						nameList.append(str(row[self.Name]) + str(self.NameSubstring) + str(row[self.GroupReference]))
						if smilesExist == True:
							smilesList.append(row[self.Smiles])
						
						if molecularWeightExist == True:
							if self.isFloat(row[self.MolecularWeight]) == True:
								molecularWeight = row[self.MolecularWeight]
							else:
								molecularWeight = 'nan'
							molecularWeightList.append(molecularWeight)
						else:
							molecularWeight = 'nan'
								
						cpd = []
						for index, item in enumerate(self.ColumnHeaderSuffix):
							if self.isFloat(row[self.Prefix + self.YAxisTitleSubString + self.Species + item]) == True:
								logValue = self.logValue(row[self.Prefix + self.YAxisTitleSubString + self.Species + item])
								if logValue != 'nan':
									cpd.append(float(logValue))	
									
						assembledData.update({str(row[self.Name]) + str(self.NameSubstring) + str(row[self.GroupReference]):[cpd, molecularWeight]})
						nameOrder.append(str(row[self.Name]) + str(self.NameSubstring) + str(row[self.GroupReference]))

			dictData.update({self.Reference:referenceList})	
			dictData.update({self.Name:nameList})	
			if smilesExist == True:
				dictData.update({self.Smiles:smilesList})
			
			if molecularWeightExist == True:
				dictData.update({self.MolecularWeight:molecularWeightList})
				
			return dictData, assembledData, nameOrder
			
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
			fileToRead.close()


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
			

	# Log value
	def logValue(self, value):
		try:
			import math
			
			if float(value) != 'nan' and float(value) > 0:
				logValue = math.log10(float(value))
			
			else:
				logValue = 'nan'
			
			return logValue
			
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

