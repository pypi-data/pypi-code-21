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

description = "The insilicolynxdqi.system folder data_folders.py module"

class DataFolders:
	# Class variables


	# __init__
	def __init__(self):
		pass
		

	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi DataFolders class"
		
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


	# Create data folders
	def createDataFolders(self, settings):
		try:
			import os
			from insilicolynxdqi.system.file_path import FilePath
			newPath = FilePath()
			
			# Create main folder
			pathMain = newPath.setPath(settings["dataFile"], 'dir', settings["mainFolderText"])
			if not os.path.isdir(pathMain): os.makedirs(pathMain)
			settings.update({"pathMain":pathMain})
			
			# Create sub folder 1
			pathSub1 = newPath.setPath(settings["dataFile"], 'dir', settings["subFolderText1"])
			if not os.path.isdir(pathSub1): os.makedirs(pathSub1)
			settings.update({"pathSub1":pathSub1})
			
			# Create sub sub folder 1
			pathSubSub1 = newPath.setPath(settings["dataFile"], 'dir', settings["subSubFolderText1"])
			if not os.path.isdir(pathSubSub1): os.makedirs(pathSubSub1)
			settings.update({"pathSubSub1":pathSubSub1})
			
			# Create sub sub sub folder 1
			pathSubSubSub1 = newPath.setPath(settings["dataFile"], 'dir', settings["subSubSubFolderText1"])
			if not os.path.isdir(pathSubSubSub1): os.makedirs(pathSubSubSub1)
			settings.update({"pathSubSubSub1":pathSubSubSub1})
		
			# Create sub sub sub folder 2
			pathSubSubSub2 = newPath.setPath(settings["dataFile"], 'dir', settings["subSubSubFolderText2"])
			if not os.path.isdir(pathSubSubSub2): os.makedirs(pathSubSubSub2)
			settings.update({"pathSubSubSub2":pathSubSubSub2})
			
			# Create sub sub sub folder 3
			pathSubSubSub3 = newPath.setPath(settings["dataFile"], 'dir', settings["subSubSubFolderText3"])
			if not os.path.isdir(pathSubSubSub3): os.makedirs(pathSubSubSub3)
			settings.update({"pathSubSubSub3":pathSubSubSub3})		

			# Create sub sub sub folder 4
			pathSubSubSub4 = newPath.setPath(settings["dataFile"], 'dir', settings["subSubSubFolderText4"])
			if not os.path.isdir(pathSubSubSub4): os.makedirs(pathSubSubSub4)
			settings.update({"pathSubSubSub4":pathSubSubSub4})
			
			# Return output
			return settings
		
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

