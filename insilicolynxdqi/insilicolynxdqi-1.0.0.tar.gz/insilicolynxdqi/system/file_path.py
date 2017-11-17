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

description = "The insilicolynxdqi.system folder file_path.py module"

class FilePath:
	# Class variables


	# __init__
	def __init__(self):
		pass


	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi FilePath class"
		
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
			

	# Set path
	def setPath(self, inputFilePath, fileOrDirectory, text1):
		try:
			import os
			import sys
		
			inputFileDirectory = os.path.dirname(inputFilePath)
			base = os.path.splitext(os.path.basename(inputFilePath))[0]
			extension = os.path.splitext(os.path.basename(inputFilePath))[1]
			
			if fileOrDirectory == "file":				
				if sys.platform.startswith('win') == True:
					# This deals with the situation on this operating system where if the inputFilePath is in the same folder as the script then a os.sep is added to the beginning on the string, resulting in inputFileDirectory equalling os.sep.
					if inputFileDirectory == "" or inputFileDirectory == os.sep:
						newPath = os.getcwd() + os.sep + base + text1 + extension
				
					else:
						newPath = inputFileDirectory + os.sep + base + text1 + extension
				
				else:
					if inputFileDirectory == "":
						newPath = os.getcwd() + os.sep + base + text1 + extension
				
					else:
						newPath = inputFileDirectory + os.sep + base + text1 + extension			
				
			elif fileOrDirectory == "dir":
				if sys.platform.startswith('win') == True:
					# This deals with the situation on this operating system where if the inputFilePath is in the same folder as the script then a os.sep is added to the beginning on the string, resulting in inputFileDirectory equalling os.sep.
					if inputFileDirectory == "" or inputFileDirectory == os.sep:
						newPath = os.getcwd() + os.sep + text1 + os.sep
					
					else:
						newPath = inputFileDirectory + os.sep + text1 + os.sep
				
				else:
					if inputFileDirectory == "":
						newPath = os.getcwd() + os.sep + text1 + os.sep
			
					else:
						newPath = inputFileDirectory + os.sep + text1 + os.sep
			
			# Return output
			return newPath
		
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
			
