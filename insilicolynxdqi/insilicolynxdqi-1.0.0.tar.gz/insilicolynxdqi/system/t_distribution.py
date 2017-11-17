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

description = "The insilicolynxdqi.system folder t_distribution.py module"

class TDistribution:
	# Class variables


	# __init__
	def __init__(self):
		pass


	# __str__	
	def __str__(self):
		try:
			# Return output
			return "The insilicolynxdqi TDistribution class"
		
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


	def integrate(self, functionToIntegrate, v, cumulativeProbability):
		try:
			# Use rectangular integration method to integrate a given t-distribution probability density function (pdf) to determine the cumulative density function (cdf) value for a given t value. 
			
			# Validate n and determine deltaX
			n = 1000000
			lowerIntegral = 0
			upperIntegral = 100
			widthRectangle = (float(upperIntegral) - float(lowerIntegral)) / n

			area = 0.5
			for i in range(n):
				if area <= cumulativeProbability:
					heightRectangle = functionToIntegrate(lowerIntegral + (i * widthRectangle), v)
					area = area + (widthRectangle * heightRectangle)
				else:
					break
			
			tValue = float(lowerIntegral + (i * widthRectangle))
			
			# Return output
			return tValue
		
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


	def generatePDF(self, x, v):				
		try:
			import math

			# Restrict degrees of freedom to 150
			if v > 150:
				v = 150
				
			# Determine where v is an even or odd integer
			if v % 2 == 0:
				# v is even	
				a = float((float(math.factorial(2 * (v / 2))) / float(math.pow(4, (v / 2)) * math.factorial((v / 2)))) * float(math.pow(math.pi, 0.5)))
				b = float(math.factorial((v / 2) - 1))
			else:
				# v is odd
				a = float(math.factorial((v - 1) / 2))		
				b = float((float(math.factorial(2 * ((v - 1) / 2))) / float(math.pow(4, ((v - 1) / 2)) * math.factorial(((v - 1) / 2)))) * float(math.pow(math.pi, 0.5)))

			c = float(1 / math.pow(v * math.pi, 0.5))			 
			d = float(-1 * ((float(v) + 1) / 2))

			fx = (float(a) / float(b)) * float(c) * math.pow(1 + (math.pow(float(x), 2) / float(v)), float(d))

			return fx

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

