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

description = "The insilicolynxdqi.system folder csv_tools.py module"

class CsvTools:
	# Class variables


	# __init__
	def __init__(self, settings):
		try:
			if settings != None:
				self.File = settings["dataFile"]
				if "name" in settings:
					self.Name = settings["name"]
		
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
			return "The insilicolynxdqi CsvTools class"
		
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


	# Add data column
	def addDataColumn(self, columnName, columnValues):
		try:
			import csv
			import os
			import shutil
			import sys
			from insilicolynxdqi.system.file_path import FilePath
			newPath = FilePath()
		
			dataFileNew = newPath.setPath(self.File, "file", "_temp")		
			
			# Open data file
			fileToRead = open(self.File, 'r')
			
			if sys.version_info[0] == 2:
				# Note, dataFileNew is a file object, so must be opened with the "b" flag on platforms where that makes a difference (does not make a difference for Linux systems)
				fileToWrite = open(dataFileNew, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileNew is a file object, so open with newline=''
				fileToWrite = open(dataFileNew, 'w', newline='')
				
			with fileToRead:
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.
				reader = csv.DictReader(fileToRead, delimiter="\t")
				
				# Add the new column header to list of fieldnames		
				reader.fieldnames.append(columnName)
				
				with fileToWrite:
					writer = csv.DictWriter(fileToWrite, delimiter="\t", fieldnames=reader.fieldnames)
					# Add column headers by creating a dictionary where both the key:value pairs are the fieldnames
					writer.writerow(dict((x, x) for x in reader.fieldnames))
					for row in reader:
						# Add the new column value as a key:value pair to the dictionary for the row
						row.update({columnName:columnValues[row[self.Name]]})
						writer.writerow(row)
		
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
			fileToWrite.close()
			shutil.move(dataFileNew, self.File)
			if os.path.isdir(dataFileNew):
				os.remove(dataFileNew)
		
	
	# Check division
	def checkDivision(self, value1, value2):			
		try:
			if value1 != 0 and value2 != 0:
				valueToReturn = float(value1) / float(value2)
			else:
				valueToReturn = float('nan')
		
			return valueToReturn
		
		except ValueError:
			valueToReturn = float('nan')

			return valueToReturn	
		
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


	# Check log10 value
	def checkLog10Value(self, value):			
		try:
			import math
			
			if value != 0:
				valueToReturn = math.log10(float(value))
			else:
				valueToReturn = float('nan')
		
			return valueToReturn
		
		except ValueError:
			valueToReturn = float('nan')

			return valueToReturn
		
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


	# Check pKa value
	def checkPKaValue(self, value):
		try:
			if 0 < float(value) < 14:
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


	# Compare column headers	
	def compareColumnHeaders(self, settings):
		try:
			import copy
			import csv
			import shutil
						
			if settings["mappingsFile"] != "":
				# Create a dictionary of possible mappings terms
				mappings = self.createDictionaryFromFile(settings["mappingsFile"])
				
				# Determine a list of possible mappings
				possibleMappings = [x for x in mappings["column header to map"] if x != ""]
				
				# Check if any mappings need to be applied (regardless of speciesName or levels")
				if len(possibleMappings) > 0:
					
					# Check for duplicates
					if len(set(possibleMappings)) != len(possibleMappings):
						print("\nThe mapping file should contain unique entries for each column header to map row value. Please check and correct the mapping file and then rerun the script.\nExiting.\n")
						raise sys.exit(0)
					
					# Create a dictionary of the dataFile file
					dictData = self.createDictionaryFromFile(self.File)

					# Create a copy of the dictData to work upon
					dictDataCopy = copy.deepcopy(dictData)

					# Find the mappings["column header to map"] index of each item in the possibleMappings list
					for item in possibleMappings:
						for index, value in enumerate(mappings["column header to map"]):
							if item == value:
								# Check that the value appears in the dictData
								for key in dictData:
									if value == key:
										if key != mappings["expected column header"][index]:
											dictDataCopy[mappings["expected column header"][index]] = dictDataCopy[key]
											del dictDataCopy[key]
					
					# Remove superfluous columns
					for key in dictData:
						if key not in possibleMappings:
							if key not in mappings["expected column header"]:
								del dictDataCopy[key]
					
					# Export revised dictData to (temp) file
					self.exportDictionaryToFile(settings, dictDataCopy, settings["dataFileTemp"])
					
				else:
					shutil.copy(self.File, settings["dataFileTemp"])
					
			else:
				shutil.copy(self.File, settings["dataFileTemp"])
			
			# Generate a list of expected column headers based on speciesName and dosing method
			requiredColumnHeaders = []
			for i, j in enumerate(settings["columnHeaderMappings"]["comment"]):
				if settings["levels"] == "total":
					if str.lower(j) == "always" or str.lower(j) == settings["ivOrPo"] or str.lower(j) == settings["speciesName"]:
						requiredColumnHeaders.append(settings["columnHeaderMappings"]["expected column header"][i])
				elif settings["levels"] == "free":
					if str.lower(j) == "always" or str.lower(j) == settings["ivOrPo"] or str.lower(j) == settings["speciesName"] or str.lower(j) == settings["speciesName"] + " " + settings["levels"]:
						requiredColumnHeaders.append(settings["columnHeaderMappings"]["expected column header"][i])
			
			# Open dataFileTemp
			fileToRead = open(settings["dataFileTemp"], 'r')
			
			# Import csv file as a dictionary
			with fileToRead:
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.				
				reader = csv.DictReader(fileToRead, delimiter="\t")
				
				columnHeaders = reader.fieldnames	
			
				# Columns found and not found in the input data file
				# Create a list of found columns
				columnHeadersFound = [requiredColumnHeaders[i] for i,j in enumerate([x in columnHeaders for x in requiredColumnHeaders]) if j == True]
				
				# Check to see if the requiredColumnHeaders list is a set of the columnHeaders lists
				result = set(requiredColumnHeaders).issubset(set(columnHeaders))
				
				# If result is false, determine the column headers that can not be found
				missingColumnHeaders = []
				potentialColumnsToAdd = []
				if result == False:
					columnHeadersNotFound = [requiredColumnHeaders[i] for i,j in enumerate([x in columnHeaders for x in requiredColumnHeaders]) if j == False]
					#
					# Notes on required data:
					# Name and molwt are always needed along with the parameter (data) and, where appropriate, the parameter units columns; if any are missing then the script needs to end.
					# If free levels are being considered, if the ppb (data) and/or ppb units column are missing then the script needs to end. 
					# The qualifier, similarity and standard deviation parameter columns are not critical.
					# If neither a similarity or standard deviation columns exist for a particular parameter then the latter may need to be created and populated with the settings["defaultParameterStandardDeviation"].
					# Note, whether error scenarios are considered depends on args.errorScenarios > 0 and if the parameter in question (i.e., args.errorParameter) is set to be considered. 
					# Store whether a parameter may need a standard deviation column in potentialColumnsToAdd list which will be passed to the add_error_scenario module.
					# Note, if both the similarity or standard deviation column exists then the standard deviation column takes priority.
					#
					for column in columnHeadersNotFound:
						if column[-len(settings["similaritySuffix"]):] == settings["similaritySuffix"]:
							pass
								
						elif column[-len(settings["standardDeviationSuffix"]):] == settings["standardDeviationSuffix"]:
							potentialColumnsToAdd.append(column)
						
						elif column[-len(settings["qualifierSuffix"]):] == settings["qualifierSuffix"]:
							potentialColumnsToAdd.append(column)
							
						else:
							missingColumnHeaders.append(column)
				
			# Return output	
			return columnHeadersFound, missingColumnHeaders, potentialColumnsToAdd
			
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
		
		finally:
			fileToRead.close()


	# Compare CSV headers	
	def compareCSVHeaders(self, settings, headerList, removeHeaderList):
		try:
			import csv
			import sys
				
			for header in removeHeaderList:
				headerList.remove(header)		
			
			# Open data file
			fileToRead = open(self.File, 'r')
			
			# Import csv file as a dictionary
			with fileToRead:
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.
				reader = csv.DictReader(fileToRead, delimiter="\t")

				headers = reader.fieldnames	
			
				continueScript = set(headerList).issubset(set(headers))
				if continueScript == False:
					print("\nThe input file (" + str(self.File) + ") does not contain the following prerequisite input data column headers to run the calculation method " + str(int(settings["method"])) + ":")
					for x in set(headerList).difference(set(headers)):
						print("\t" + str(x))
					print("Please check before re-running.\nExiting.\n")
					raise sys.exit(0)
			
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


	# Create dictionary from file
	def createDictionaryFromFile(self, fileName):
		try:
			import csv
			
			# Note: this method will generate lists of data that mirror the order in the csv file
			
			# Open data file 
			fileToRead = open(fileName, 'r')
			
			# Import csv file as a dictionary	
			with fileToRead:
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.
				reader = csv.DictReader(fileToRead, delimiter="\t")
				
				# Create a list of lists containing the column headers (i.e., reader.fieldnames) as the first element in each list.
				listOfLists = [[columnHeader] for columnHeader in reader.fieldnames]
				
				# Loop through each row of the reader and then each key of the row - append the value (i.e., row[key]) from the key-value pair to the appropriate list within a list, mapping using the reader.fieldnames.index(key)
				for row in reader:
					for key in row:
						listOfLists[reader.fieldnames.index(key)].append(row[key])

			# Dictionary comprehension: parse the list of lists into a dictionary by setting the first element in each list (i.e.; the column header) as the "key" and the rest of the list as the "value" for each "key:value" pair of the dictionary
			data = {listX[0]:listX[1:] for listX in listOfLists}
			
			return data
			
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

		finally:
			fileToRead.close()
		

	# Create revised scenario dictionary from file
	def createRevisedScenarioDictionaryFromFile(self, settings):
		try:
			import csv
			import os
			from insilicolynxdqi.system.add_error_scenarios import AddErrorScenarios
			addErrorScenarios = AddErrorScenarios()
			
			# Open data file
			fileToRead = open(settings["dataFileTemp"], 'r')

			# Import csv file as a dictionary
			with fileToRead:
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.
				reader = csv.DictReader(fileToRead, delimiter="\t")
				
				# Generate a list of column headers
				columnHeaders = reader.fieldnames
	
				# Add any columns
				columnHeaders = addErrorScenarios.addAnyColumns(settings, columnHeaders)
				
				#
				# Note reader object will have additional fields for each additional column added - the value set to None
				#
							
				# Create a list of lists containing the column headers as the first element in each list.
				listOfLists = [[columnHeader] for columnHeader in columnHeaders]
				
				# Initialise a referenceCount and groupReferenceCount
				referenceCount = 1
				groupReferenceCount = 1
				
				# Loop through each row of the reader and then each key of the row - append the value (i.e., row[key]) from the key-value pair to the appropriate list within a list, mapping using the reader.fieldnames.index(key)
				someIncorrectData = False
				for row in reader:
					for key in row:
						
						addRow = True
						
						# Check if certain key values are blank 
						if key[-len(settings["qualifierSuffix"]):] != settings["qualifierSuffix"] and key[-len(settings["standardDeviationSuffix"]):] != settings["standardDeviationSuffix"] and key[-len(settings["similaritySuffix"]):] != settings["similaritySuffix"]:	
							if key in settings["columnHeadersFound"] and row[key] == "":
								valueNeeded = True
								
								# For po scenarios, it is possible that some or all of the pKa columns are not required to have a value and this needs to be handled
								if settings["ivOrPo"] == "po" and key[:len(settings["pKaPrefix"])] == settings["pKaPrefix"]:
									# Determine valueNeeded based on the charge type:
									if row[settings["chargeTypeText"]].lower() in [settings["diAcidText"], settings["diBaseText"], settings["monoAcidText"], settings["monoBaseText"], settings["neutralText"], settings["zwitterionText"]]:
										if key == settings["pKaA1"] and row[settings["chargeTypeText"]].lower() in [settings["diBaseText"], settings["monoBaseText"], settings["neutralText"]]:
											valueNeeded = False
										elif key == settings["pKaA2"] and row[settings["chargeTypeText"]].lower() != settings["diAcidText"]:
											valueNeeded = False
										elif key == settings["pKaB1"] and row[settings["chargeTypeText"]].lower() in [settings["diAcidText"], settings["monoAcidText"], settings["neutralText"]]:
											valueNeeded = False
										elif key == settings["pKaB2"] and row[settings["chargeTypeText"]].lower() != settings["diBaseText"]:
											valueNeeded = False
									else:
										# The row[settings["chargeTypeText"]] is blank or contains an value that can not be handled.  This row will fail on the charge type, if the code has reached this point then its because the code hasn't processed the charge type information yet - by setting the valueNeeded to False will allow the code to continue and assess the charge type in due course 
										valueNeeded = False
				
								if valueNeeded == True:
									if someIncorrectData == False:
										print("")
										someIncorrectData = True
									print("\tThe " + str(row[settings["name"]]) + " data row has critical missing data (see " + str(key) + ") and will not be considered!")
									addRow = False
									break

						# Check if the value or magnitude of pKa data is unacceptable (only for po scenario)
						if settings["ivOrPo"] == "po" and key[:len(settings["pKaPrefix"])] == settings["pKaPrefix"] and row[key] == "":
							pKaValueFine = ''
							if key == settings["pKaA1"] and row[settings["chargeTypeText"]].lower() in [settings["diAcidText"], settings["monoAcidText"], settings["zwitterionText"]]:
								pKaValue = self.checkPKaValue(row[key])
							elif key == settings["pKaA2"] and row[settings["chargeTypeText"]].lower() == settings["diAcidText"]:
								pKaValue = self.checkPKaValue(row[key])
							elif key == settings["pKaB1"] and row[settings["chargeTypeText"]].lower() in [settings["diBaseText"], settings["monoBaseText"], settings["zwitterionText"]]:
								pKaValue = self.checkPKaValue(row[key])
							elif key == settings["pKaB2"] and row[settings["chargeTypeText"]].lower() == settings["diBaseText"]:
								pKaValue = self.checkPKaValue(row[key])
							if pKaValueFine == 'nan':
								if someIncorrectData == False:
									print("")
									someIncorrectData = True
								print("\tThe " + str(row[settings["name"]]) + " data row has an incompatible number for " + str(key) + " (" + str(row[key]) + ") and will not be considered! A pKa number needs to be a positive real number that is greater than 0 and less than 14.")
								addRow = False
								break						
						
						# Check if the charge type value is unacceptable (only for po scenario)
						if settings["ivOrPo"] == "po" and key == settings["chargeTypeText"]:
							if row[key].lower() not in [settings["diAcidText"], settings["diBaseText"], settings["monoAcidText"], settings["monoBaseText"], settings["neutralText"], settings["zwitterionText"]]:
								if someIncorrectData == False:
										print("")
										someIncorrectData = True
								print("\tThe " + str(row[settings["name"]]) + " data row has an incompatible charge type (" + str(row[key]) + ") and will not be considered! Acceptable entries include diacid, dibase, monoacid, monobase, neutral or zwitterion.")
								addRow = False
								break
						
						# Check if certain key values are 'nan' 
						if settings["ivOrPo"] == "iv":						
							if key in [settings[settings["clText"] + settings["prefix"]], settings[settings["vText"] + settings["prefix"]]]:
								if self.checkValue(row[key]) == 'nan':
									if someIncorrectData == False:
										print("")
										someIncorrectData = True
									print("\tThe " + str(row[settings["name"]]) + " data row has an incompatible number for " + str(key) + " (" + str(row[key]) + ") and will not be considered! The number needs to be a positive real number.")
									addRow = False
									break
									
						elif settings["ivOrPo"] == "po":
							if key in [settings[settings["clText"] + settings["prefix"]], settings[settings["vText"] + settings["prefix"]], settings[settings["caco2Text"] + settings["prefix"]], settings[settings["solubilityText"] + settings["prefix"]]]:
								if self.checkValue(row[key]) == 'nan':
									if someIncorrectData == False:
										print("")
										someIncorrectData = True
									print("\tThe " + str(row[settings["name"]]) + " data row has an incompatible number for " + str(key) + " (" + str(row[key]) + ") and will not be considered! The number needs to be a positive real number.")
									addRow = False
									break	
						
						# Check if free levels being considered and if the ppb value is 'nan' 
						if settings["levels"] == "free" and key == settings[settings["ppbText"] + settings["prefix"]]:
							if self.checkValue(row[key]) == 'nan':
								if someIncorrectData == False:
									print("")
									someIncorrectData = True
								print("\tThe " + str(row[settings["name"]]) + " data row has an incompatible number for " + str(key) + " (" + str(row[key]) + ") and will not be considered! The number needs to be a positive real number.")
								addRow = False
								break
		
					# Check that data units are correct and that the data value is permitted
					if addRow == True:
						addRow = addErrorScenarios.checkData(settings, row, someIncorrectData)
					
					# Add row data
					if addRow == True:
						for key in row:
							if key == settings["reference"]:
								listOfLists[columnHeaders.index(key)].append(referenceCount)
							elif key == settings["groupReference"]:
								listOfLists[columnHeaders.index(key)].append(groupReferenceCount)
							else:
								if row[key] != None:
									listOfLists[columnHeaders.index(key)].append(row[key])
								else:
									listOfLists[columnHeaders.index(key)].append("")
						i = 0
						if settings["errorScenarios"] > 0:
							# Add error permutation rows
							for errorScenario in range(settings["errorScenarios"]):
								i += 1
								newRow = addErrorScenarios.errorScenarioRow(settings, row, referenceCount, groupReferenceCount, i)
								for item in columnHeaders:
									listOfLists[columnHeaders.index(item)].append(newRow[item])
						referenceCount = referenceCount + i + 1
						groupReferenceCount = groupReferenceCount + 1			
	
			# Dictionary comprehension: parse the list of lists into a dictionary by setting the first element in each list (i.e.; the column header) as the "key" and the rest of the list as the "value" for each "key:value" pair of the dictionary
			dictData = {listX[0]:listX[1:] for listX in listOfLists}
			
			# Export revised scenario dictionary to file
			self.exportDictionaryToFile(settings, dictData, settings["dataFileNew"])
			 
			# Remove temporary file
			os.remove(settings["dataFileTemp"])
			
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
		
		finally:
			fileToRead.close()


	# Data rows in CSV
	def dataRowsInCSV(self):
		try:
			import csv
			
			# Open data file
			fileToRead = open(self.File, 'r')
			
			# Import csv file as a dictionary
			with fileToRead:
				# Note, csv.DictReader does not return empty lines - which is different to the basic reader. Read the data file one row at a time as a series of dictionaries where the "key" in the "key:value" pair is the column header and the "value" in the "key:value" pair is the row value for the appropriate column.
				reader = csv.DictReader(fileToRead, delimiter="\t")
				
				i=0
				for row in reader:
					i += 1
				
			# Return output
			return i
			
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
		
		finally:
			fileToRead.close()


	# Export AUC dictionaries to CSV file
	def exportAucDictionariesToCSV(self, dataFileToWrite, dict1, dict2, dict3, dict4, settings):			
		try:
			import csv
			import sys
			
			if settings["ivOrPo"] == "iv":
				listKeys = settings["dose"]
			elif settings["ivOrPo"] == "po":
				listKeys = settings["doses"]
			
			columnHeader1 = settings["csvFileColumnHeaderDoseText"]
			columnHeader2 = settings["csvFileColumnHeaderAucAmountBText1"]
			columnHeader3 = settings["csvFileColumnHeaderAucConcentrationBText1"]	
			prefix = settings["csvFileColumnHeaderLog10Text"]
			
			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			if dict3 != "" and dict4 != "":
				columnHeader4 = settings["csvFileColumnHeaderAucAmountCText1"]
				columnHeader5 = settings["csvFileColumnHeaderAucAmountBCText1"]
				
				with fileToWrite:					
					writer = csv.writer(fileToWrite, delimiter='\t')
					writer.writerow([columnHeader1, columnHeader2, columnHeader3, columnHeader4, columnHeader5, prefix + "(" + columnHeader1 + ")", prefix + "(" + columnHeader2 + ")", prefix + "(" + columnHeader3 + ")", prefix + "(" + columnHeader4 + ")", prefix + "(" + columnHeader5 + ")"])		
					for key in listKeys:
						writer.writerow([key, dict1[key], dict2[key], dict3[key], dict4[key], self.checkLog10Value(key), self.checkLog10Value(dict1[key]), self.checkLog10Value(dict2[key]), self.checkLog10Value(dict3[key]), self.checkLog10Value(dict4[key])])
			
			else:
				with fileToWrite:		
					writer = csv.writer(fileToWrite, delimiter='\t')
					writer.writerow([columnHeader1, columnHeader2, columnHeader3, prefix + "(" + columnHeader1 + ")", prefix + "(" + columnHeader2 + ")", prefix + "(" + columnHeader3 + ")"])		
					for key in listKeys:
						writer.writerow([key, dict1[key], dict2[key], self.checkLog10Value(key), self.checkLog10Value(dict1[key]), self.checkLog10Value(dict2[key])])

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
			fileToWrite.close()


	# Export dictionary to file
	def exportDictionaryToFile(self, settings, dictData, dataFileToWrite):
		try:
			import csv	
			import sys

			columnHeaders = sorted(list(dictData))		
			if settings["groupReference"] in columnHeaders:
				columnHeaders.remove(settings["groupReference"])
				columnHeaders.remove(settings["name"])
				columnHeaders.remove(settings["reference"])
				columnHeaders.insert(0, settings["groupReference"])
				columnHeaders.insert(0, settings["name"])	
				columnHeaders.insert(0, settings["reference"])
			else:
				columnHeaders.remove(settings["name"])
				columnHeaders.insert(0, settings["name"])		

			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			with fileToWrite:
				writer = csv.writer(fileToWrite, delimiter="\t")
				writer.writerow(columnHeaders)
				writer.writerows(zip(*[dictData[columnHeader] for columnHeader in columnHeaders]))

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
			fileToWrite.close()


	# Export five lists to CSV file
	def exportFiveListsToCSV(self, dataFileToWrite, list1, list2, list3, list4, list5, dict1, columnHeader1, columnHeader2, columnHeader3, columnHeader4, columnHeader5, columnHeader6, columnHeader7):
		try:
			import csv
			import sys
			
			list6 = []
			for key in dict1:
				list6.append(key)
			list6.sort()
			
			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			with fileToWrite:				
				writer = csv.writer(fileToWrite, delimiter='\t')
				writer.writerow([columnHeader1, columnHeader2, columnHeader3, columnHeader4, columnHeader5, "", columnHeader6, columnHeader7])
				for index, item in enumerate(list1):
					if index <= len(dict1) - 1:
						writer.writerow([list1[index], list2[index], list3[index], list4[index], list5[index], "", list6[index], dict1[list6[index]]])
					else:
						writer.writerow([list1[index], list2[index], list3[index], list4[index], list5[index]])
						
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
			fileToWrite.close()
	

	# Export nine dictionaries to CSV file
	def exportNineDictionariesToCSV(self, dataFileToWrite, dict1, dict2, dict3, dict4, dict5, dict6, dict7, dict8, dict9, settings):			
		try:
			import csv
			import sys
			
			if settings["ivOrPo"] == "iv":
				listKeys = settings["dose"]
			elif settings["ivOrPo"] == "po":
				listKeys = settings["doses"]
			
			columnHeader1 = settings["csvFileColumnHeaderDoseText"]		
			columnHeader2 = settings["csvFileColumnHeaderMaxAmountText1"]
			columnHeader3 = settings["csvFileColumnHeaderMinAmountText1"]
			columnHeader4 = settings["csvFileColumnHeaderMidAmountText1"]		
			columnHeader5 = settings["csvFileColumnHeaderMaxToMinRatioText1"]		
			columnHeader6 = settings["csvFileColumnHeaderMaxAmountText2"]
			columnHeader7 = settings["csvFileColumnHeaderMinAmountText2"]
			columnHeader8 = settings["csvFileColumnHeaderMidAmountText2"]
			columnHeader9 = settings["csvFileColumnHeaderMaxToMinRatioText2"]		
			columnHeader10 = settings["csvFileColumnHeaderMaxAmountText3"]
			columnHeader11 = settings["csvFileColumnHeaderMinAmountText3"]
			columnHeader12 = settings["csvFileColumnHeaderMidAmountText2"]
			columnHeader13 = settings["csvFileColumnHeaderMaxToMinRatioText3"]				
			prefix = settings["csvFileColumnHeaderLog10Text"]

			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			with fileToWrite:
				writer = csv.writer(fileToWrite, delimiter='\t')		
				writer.writerow([columnHeader1, columnHeader2, columnHeader3, columnHeader4, columnHeader5, columnHeader6, columnHeader7, columnHeader8, columnHeader9, columnHeader10, columnHeader11, columnHeader12, columnHeader13, prefix + "(" + columnHeader1 + ")", prefix + "(" + columnHeader2 + ")", prefix + "(" + columnHeader3 + ")", prefix + "(" + columnHeader4 + ")", prefix + "(" + columnHeader6 + ")", prefix + "(" + columnHeader7 + ")", prefix + "(" + columnHeader8 + ")", prefix + "(" + columnHeader10 + ")", prefix + "(" + columnHeader11 + ")", prefix + "(" + columnHeader12 + ")"])							
				for key in listKeys:
					writer.writerow([key, dict1[key], dict2[key], dict3[key], self.checkDivision(dict1[key], dict2[key]), dict4[key], dict5[key], dict6[key], self.checkDivision(dict4[key], dict5[key]), dict7[key], dict8[key], dict9[key], self.checkDivision(dict7[key], dict8[key]), self.checkLog10Value(key), self.checkLog10Value(dict1[key]), self.checkLog10Value(dict2[key]), self.checkLog10Value(dict3[key]), self.checkLog10Value(dict4[key]), self.checkLog10Value(dict5[key]), self.checkLog10Value(dict6[key]), self.checkLog10Value(dict7[key]), self.checkLog10Value(dict8[key]), self.checkLog10Value(dict9[key])])		
		
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
			fileToWrite.close()
			

	# Export three dictionaries to CSV file
	def exportThreeDictionariesToCSV(self, dataFileToWrite, dict1, dict2, dict3, settings, amountsOrConcentrations):			
		try:
			import csv
			import sys
			
			if settings["ivOrPo"] == "iv":
				listKeys = settings["dose"]
			elif settings["ivOrPo"] == "po":
				listKeys = settings["doses"]
				
			columnHeader1 = settings["csvFileColumnHeaderDoseText"]
			if amountsOrConcentrations == "amounts":
				columnHeader2 = settings["csvFileColumnHeaderMaxAmountText1"]
				columnHeader3 = settings["csvFileColumnHeaderMinAmountText1"]
				columnHeader4 = settings["csvFileColumnHeaderMidAmountText1"]
			elif amountsOrConcentrations == "concentrations":
				columnHeader2 = settings["csvFileColumnHeaderMaxConcentrationText1"]
				columnHeader3 = settings["csvFileColumnHeaderMinConcentrationText1"]
				columnHeader4 = settings["csvFileColumnHeaderMidConcentrationText1"]
			columnHeader5 = settings["csvFileColumnHeaderMaxToMinRatioText1"]
			prefix = settings["csvFileColumnHeaderLog10Text"]			

			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			with fileToWrite:
				writer = csv.writer(fileToWrite, delimiter='\t')
				writer.writerow([columnHeader1, columnHeader2, columnHeader3, columnHeader4, columnHeader5, prefix + "(" + columnHeader1 + ")", prefix + "(" + columnHeader2 + ")", prefix + "(" + columnHeader3 + ")", prefix + "(" + columnHeader4 + ")"])		
				for key in listKeys:
					writer.writerow([key, dict1[key], dict2[key], dict3[key], self.checkDivision(dict1[key], dict2[key]), self.checkLog10Value(key), self.checkLog10Value(dict1[key]), self.checkLog10Value(dict2[key]), self.checkLog10Value(dict3[key])])
			
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
			fileToWrite.close()
			

	# Export three lists to CSV file
	def exportThreeListsToCSV(self, dataFileToWrite, list1, list2, list3, dict1, columnHeader1, columnHeader2, columnHeader3, columnHeader4, columnHeader5):
		try:
			import csv
			import sys
			
			list4 = []
			for key in dict1:
				list4.append(key)
			list4.sort()
			
			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			with fileToWrite:
				writer = csv.writer(fileToWrite, delimiter='\t')
				writer.writerow([columnHeader1, columnHeader2, columnHeader3, "", columnHeader4, columnHeader5])			
				for index, item in enumerate(list1):
					if index <= len(dict1) - 1:
						writer.writerow([list1[index], list2[index], list3[index], "", list4[index], dict1[list4[index]]])
					else:
						writer.writerow([list1[index], list2[index], list3[index]])		
		
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
			fileToWrite.close()


	# Export values to CSV file
	def exportValuesToCSV(self, dataFileToWrite, allNames, allValues):
		try:
			import csv
			import sys

			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			with fileToWrite:
				writer = csv.writer(fileToWrite, delimiter='\t')
				columnHeaders = ["name"]
				i = 0
				for name in allNames:
					if i == 0:
						keys = allValues[name].keys()
						columnHeaders.extend(keys)
						writer.writerow(columnHeaders)
						i += 1
					rowText = [name]
					for key in keys:
						rowText.append(allValues[name][key])
					writer.writerow(rowText)
		
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
			fileToWrite.close()

		
	# Transfer dictionary to file
	def transferDictionaryToFile(self, settings, dictData, dataFileToWrite, variable):
		try:
			import csv
			import sys
			#
			# Note, the unique names stored in revisedNameOrder and used as keys in dictData take the form: name + settings[nameSubstring] + groupReference.
			# For the purpose of exporting to file - need to remove the "+ settings[nameSubstring] + groupReference" suffix.
			# This can be done using name.split(settings["nameSubstring"])[0]
			#

			# Check if dictData has a settings["name"] key
			if settings["name"] in dictData:
				dictData[settings["name"]] = [x.split(settings["nameSubstring"])[0] for x in dictData[settings["name"]]]
						
			columnHeaders = sorted(list(dictData))		
			if variable == "":
				columnHeaders.remove(settings["reference"])
				columnHeaders.remove(settings["name"])
				if settings["molecularWeightText"] in columnHeaders:
					columnHeaders.remove(settings["molecularWeightText"])
					columnHeaders.insert(0, settings["molecularWeightText"])
				
				if settings["smiles"] in columnHeaders:
					columnHeaders.remove(settings["smiles"])
					columnHeaders.insert(0, settings["smiles"])
				columnHeaders.insert(0, settings["name"])
				columnHeaders.insert(0, settings["reference"])

			elif type(variable) == list:
				variableReversed = variable[::-1]
				for item in variableReversed:
					columnHeaders.remove(item)
					columnHeaders.insert(0, item)		   

			elif variable == "polygonData":
				if settings["xDataText"] in dictData.keys():
					columnHeaders.remove(settings["xDataText"])
					columnHeaders.insert(0, settings["xDataText"])
	
			if sys.version_info[0] == 2:
				# Note, dataFileToWrite is a file object, so must be opened with the ‘b’ flag on platforms where that makes a difference - doesn't make a difference for Linux systems
				fileToWrite = open(dataFileToWrite, 'wb')
				
			elif sys.version_info[0] == 3:
				# Note, dataFileToWrite is a file object, so open with newline=''
				fileToWrite = open(dataFileToWrite, 'w', newline='')
			
			with fileToWrite:			
				writer = csv.writer(fileToWrite, delimiter="\t")
				writer.writerow(columnHeaders)
				writer.writerows(zip(*[dictData[columnHeader] for columnHeader in columnHeaders]))			  

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
			fileToWrite.close()

