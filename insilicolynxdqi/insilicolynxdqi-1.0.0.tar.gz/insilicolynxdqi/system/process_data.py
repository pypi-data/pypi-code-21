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

description = "The insilicolynxdqi.system folder process_data.py module"

class ProcessData:
	# Class variables


	# __init__
	def __init__(self):
		pass


	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi ProcessData class"
		
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
			

	# Process data
	def processData(self, settings):
		try:
			dictDataTotal = {}
			dictDataFree = {}
			for index, dataFile in enumerate(settings["filesToConsider"]):
				# Compartment
				compartments = []	
				if settings["methods"][index] in [1, 2]:
					compartments.append("plasma")
				elif settings["methods"][index] in [3, 4, 5, 6]:				
					if settings["compartment"] != "all":
						if settings["compartment"] in ["c"]:
							compartments.append("central")
						if settings["compartment"] in ["p"]:
							compartments.append("peripheral")
						if settings["compartment"] in ["cp"]:
							compartments.append("central_peripheral")
					else:
						compartments.append("central")
						compartments.append("peripheral")
						compartments.append("central_peripheral")
				
				# Column header suffix text
				columnHeaderSuffix = []
				if settings["methods"][index] in [1, 2]:
					columnHeaderSuffix.append("")
				elif settings["methods"][index] in [3, 4, 5, 6]:				
					for i in range(5):
						columnHeaderSuffix.append("_(" + "scenario" + "_" + str(i + 1) + ")")
			
				# Processing steps
				print("")
				if settings["methods"][index] in [1, 2, 3, 4, 5, 6]:
					print("\tProcessing statistics for " + dataFile + ".")
									
				for scale in settings["scales"]:
					for compartmentValue in compartments:
						prefix = scale + compartmentValue + "_"
						if prefix not in settings["prefixOptions"]:
		
							if settings["methods"][index] in [1, 2, 3, 4]:
								from insilicolynxdqi.system.assemble_data_po import AssembleDataPo
								from insilicolynxdqi.system.polygons import Polygons
								from insilicolynxdqi.system.csv_tools import CsvTools
								csvTools = CsvTools(settings)
								
								if scale.find("auc") == -1:
									#
									# Option 0: intercept vs dose: max
									#
									option = 0
									data = AssembleDataPo(settings, dataFile, prefix, columnHeaderSuffix, option)
									polygon = Polygons(settings, index, dataFile, prefix, option)
										
									if settings["methods"][index] in [1, 3]:
										dictDataTotal, smilesExist, assembledData1, nameOrder = data.assembleData(dictDataTotal)
										dictDataTotal, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataTotal, assembledData1, nameOrder)
									
									elif settings["methods"][index] in [2, 4]:
										dictDataFree, smilesExist, assembledData1, nameOrder = data.assembleData(dictDataFree)
										dictDataFree, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataFree, assembledData1, nameOrder)
									
									#
									# Option 1: intercept vs dose: min
									#
									option = 1
									data = AssembleDataPo(settings, dataFile, prefix, columnHeaderSuffix, option)
									polygon = Polygons(settings, index, dataFile, prefix, option)
									
									if settings["methods"][index] in [1, 3]:
										dictDataTotal, smilesExist, assembledData2, nameOrder = data.assembleData(dictDataTotal)
										dictDataTotal, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataTotal, assembledData2, nameOrder)
									
									elif settings["methods"][index] in [2, 4]:
										dictDataFree, smilesExist, assembledData2, nameOrder = data.assembleData(dictDataFree)
										dictDataFree, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataFree, assembledData2, nameOrder)
									
									#			
									# Option 2: intercept vs dose: mid
									#
									option = 2
									data = AssembleDataPo(settings, dataFile, prefix, columnHeaderSuffix, option)
									polygon = Polygons(settings, index, dataFile, prefix, option)
									
									if settings["methods"][index] in [1, 3]:
										dictDataTotal, smilesExist, assembledData3, nameOrder = data.assembleData(dictDataTotal)
										dictDataTotal, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataTotal, assembledData3, nameOrder)
									
									elif settings["methods"][index] in [2, 4]:
										dictDataFree, smilesExist, assembledData3, nameOrder = data.assembleData(dictDataFree)
										dictDataFree, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataFree, assembledData3, nameOrder)
								
								else:
									#
									# Option 3: intercept vs dose: auc
									#
									option = 3
									data = AssembleDataPo(settings, dataFile, prefix, columnHeaderSuffix, option)
									polygon = Polygons(settings, index, dataFile, prefix, option)
									
									if settings["methods"][index] in [1, 3]:
										dictDataTotal, smilesExist, assembledData4, nameOrder = data.assembleData(dictDataTotal)
										dictDataTotal, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataTotal, assembledData4, nameOrder)
												
									elif settings["methods"][index] in [2, 4]:
										dictDataFree, smilesExist, assembledData4, nameOrder = data.assembleData(dictDataFree)
										dictDataFree, revisedNameOrder, orderedPolygonPointsDictionary, centroids = polygon.processCompoundPolygons(settings, dictDataFree, assembledData4, nameOrder)
							
							elif settings["methods"][index] in [5, 6]:
								from insilicolynxdqi.system.assemble_data_iv import AssembleDataIv
								from insilicolynxdqi.system.statistics import Statistics
								from insilicolynxdqi.system.csv_tools import CsvTools
								csvTools = CsvTools(settings)
								
								if scale.find("auc") == -1:
									#
									# Option 0: quantity: max
									#
									option = 0
									data = AssembleDataIv(settings, dataFile, prefix, columnHeaderSuffix, option)
									statistics = Statistics(settings, index, dataFile, scale, prefix, option)
									
									if settings["methods"][index] in [5]:
										dictDataTotal, assembledData1, nameOrder = data.assembleData(dictDataTotal)
										settings, dictDataTotal = statistics.processCompoundData(settings, dictDataTotal, assembledData1, nameOrder)
									
									elif settings["methods"][index] in [6]:
										dictDataFree, assembledData1, nameOrder = data.assembleData(dictDataFree)
										settings, dictDataFree = statistics.processCompoundData(settings, dictDataFree, assembledData1, nameOrder)
							
									#
									# Option 1: quantity: min
									#
									option = 1
									data = AssembleDataIv(settings, dataFile, prefix, columnHeaderSuffix, option)
									statistics = Statistics(settings, index, dataFile, scale, prefix, option)
									
									if settings["methods"][index] in [5]:
										dictDataTotal, assembledData2, nameOrder = data.assembleData(dictDataTotal)
										settings, dictDataTotal = statistics.processCompoundData(settings, dictDataTotal, assembledData2, nameOrder)
										
									elif settings["methods"][index] in [6]:
										dictDataFree, assembledData2, nameOrder = data.assembleData(dictDataFree)
										settings, dictDataFree = statistics.processCompoundData(settings, dictDataFree, assembledData2, nameOrder)
										
									#			
									# Option 2: quantity: mid
									#
									option = 2
									data = AssembleDataIv(settings, dataFile, prefix, columnHeaderSuffix, option)
									statistics = Statistics(settings, index, dataFile, scale, prefix, option)
									
									if settings["methods"][index] in [5]:
										dictDataTotal, assembledData3, nameOrder = data.assembleData(dictDataTotal)
										settings, dictDataTotal = statistics.processCompoundData(settings, dictDataTotal, assembledData3, nameOrder)
										
									elif settings["methods"][index] in [6]:
										dictDataFree, assembledData3, nameOrder = data.assembleData(dictDataFree)
										settings, dictDataFree = statistics.processCompoundData(settings, dictDataFree, assembledData3, nameOrder)
										
								else:
									#
									# Option 3: quantity: auc
									#
									option = 3
									data = AssembleDataIv(settings, dataFile, prefix, columnHeaderSuffix, option)
									statistics = Statistics(settings, index, dataFile, scale, prefix, option)
									
									if settings["methods"][index] in [5]:
										dictDataTotal, assembledData4, nameOrder = data.assembleData(dictDataTotal)
										settings, dictDataTotal = statistics.processCompoundData(settings, dictDataTotal, assembledData4, nameOrder)
										
									elif settings["methods"][index] in [6]:
										dictDataFree, assembledData4, nameOrder = data.assembleData(dictDataFree)			
										settings, dictDataFree = statistics.processCompoundData(settings, dictDataFree, assembledData4, nameOrder)
												
			# Transfer summary files
			if settings["name"] in dictDataTotal.keys():
				csvTools.transferDictionaryToFile(settings, dictDataTotal, settings["fileNameTotal"], "")
			if settings["name"] in dictDataFree.keys():
				csvTools.transferDictionaryToFile(settings, dictDataFree, settings["fileNameFree"], "")
			
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

