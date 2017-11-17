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

description = "The insilicolynxdqi.system folder area_under_curve.py module"

class AreaUnderCurve:
	# Class variables


	# __init__
	def __init__(self):
		pass
		

	# __str__
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi AreaUnderCurve class"
		
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
			
		
	def integrateAUC(self, functionToIntegrate, constants, lowerIntegral, upperIntegral, numberOfSegments):
		try:
			#
			# Composite Simpson's rule for determining the area under the curve
			#
			# 	areaUnderCurve = (deltax / 3) (y0 + 4(y1 + y3 + ...) + 2(y2 + 2y4 + ...) + yn)
			# 
			# where:
			#
			# 	deltax = (upperIntegral - lowerIntegral) / numberOfSegments (i.e., n which needs to be even)
			# 
			
			# Validate i, j and n and determine deltaX
			i, j = self.setIntegralLimits(lowerIntegral, upperIntegral)
			n = self.setNumberOfSegments(int(numberOfSegments))
			deltaX = (float(j) - float(i)) / n
			
			# Determine y0
			y0 = float(functionToIntegrate(i, constants))
			
			# Determine yOdds
			yOdds = 0
			for p in [(float(i) + (x * deltaX)) for x in range(1, n, 2)]:
				yOdds += float(functionToIntegrate(p, constants))			
			
			# Determine yEvens
			yEvens = 0
			for q in [(float(i) + (x * deltaX)) for x in range(2, n, 2)]:
				yEvens += float(functionToIntegrate(q, constants))			
		
			# Determine yLast
			yLast = float(functionToIntegrate(j, constants))

			# Determine area under curve
			areaUnderCurve = (float(deltaX) / 3) * (float(y0) + (4 * float(yOdds)) + (2 * float(yEvens)) + float(yLast))
			
			# Return output
			return areaUnderCurve
		
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


	def setIntegralLimits(self, lowerIntegral, upperIntegral):
		try:
			if lowerIntegral < upperIntegral:
				i = lowerIntegral
				j = upperIntegral
			elif lowerIntegral > upperIntegral:
				i = upperIntegral
				j = lowerIntegral
			
			# Return output
			return i, j
		
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


	def setNumberOfSegments(self, numberOfSegments):
		try:
			# Check if the remainder of the division of numberOfSegments by 2 is zero
			if numberOfSegments % 2 != 0:
				n = numberOfSegments + 1
			else:
				n= numberOfSegments
			
			# Return output
			return n
		
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

