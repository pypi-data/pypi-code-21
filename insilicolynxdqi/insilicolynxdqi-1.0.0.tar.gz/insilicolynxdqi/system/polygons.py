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

description = "The insilicolynxdqi.system folder polygons.py module"

class Polygons:
	# Class variables


	# __init__
	def __init__(self, settings, index, dataFile, prefix, option):
		try:
			import os
			
			# Inputs
			if settings["methods"][index] == 1:
				self.MethodText = "po_1c_total_"
			if settings["methods"][index] == 2:
				self.MethodText = "po_1c_free_"
			if settings["methods"][index] == 3:
				self.MethodText = "po_2c_total_"
			if settings["methods"][index] == 4:
				self.MethodText = "po_2c_free_"
			self.Prefix = prefix
			self.XAxisTitleSubString = settings["doseLabels"][option]
			self.YAxisTitleSubString = settings["interceptLabels"][option]
			
			# Create self.PlotDataFile
			if os.path.dirname(dataFile) == "":
				newPath = settings["analysisPrefix"] + os.path.splitext(os.path.basename(dataFile))[0] + settings["summarySuffix"] + os.sep 
			else:
				newPath = os.path.dirname(dataFile) + os.sep + settings["analysisPrefix"] + os.path.splitext(os.path.basename(dataFile))[0] + settings["summarySuffix"] + os.sep 		
			if not os.path.isdir(newPath): os.makedirs(newPath)	
			self.PlotDataFile = newPath + prefix + settings["poTitlesText"][option] + settings["textFileExtension"]
			
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
			return "The insilicolynxdqi Polygons class"
		
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


	# Process compound polygons
	def processCompoundPolygons(self, settings, dictData, assembledData, nameOrder):
		
		try:
			from insilicolynxdqi.system.csv_tools import CsvTools
			csvTools = CsvTools(settings)
			
			xCentroidList = []
			yCentroidList = []
			polygonAreaList = []
			xSecondMomentOfAreaList = []
			ySecondMomentOfAreaList = []
			revisedNameOrder = []
			orderedPolygonPointsDictionary = {}
			centroids = {}
			for key in nameOrder:
				if len(assembledData[key]) > 0:
					polygonPoints = []
					for i in range(len(assembledData[key])):		
						polygonPoints.append((assembledData[key][i][0], assembledData[key][i][1]))
							
					numberOfOutliersToRemove = self.numberOfOutliersToRemove(len(polygonPoints), settings["removeOutliers"])
					
					errorsInPoints = False
					if numberOfOutliersToRemove > 0:
						# Need to determine distance between point and centroid and remove the required number of the furtherest away points
						orderedPolygonPointsToFilter = self.orderedPolygonPointsList(polygonPoints)
						if orderedPolygonPointsToFilter != False:
							xMean, yMean = self.determineMeans(orderedPolygonPointsToFilter)
							if xMean != 'nan' and yMean != 'nan':
								filteredOrderedPolygonPoints = self.filterOrderedPolygonPoints(orderedPolygonPointsToFilter, numberOfOutliersToRemove, xMean, yMean)
								if filteredOrderedPolygonPoints != False:
									orderedPolygonPoints = self.orderedPolygonPointsList(filteredOrderedPolygonPoints)
									if orderedPolygonPoints == False:
										errorInPoints = True
								else:
									errorInPoints = True
							else:
								errorInPoints = True
						else:
							errorInPoints = True
					else:
						orderedPolygonPoints = self.orderedPolygonPointsList(polygonPoints)
						if orderedPolygonPoints == False:
							errorInPoints = True		
					
					if errorsInPoints == False:
						xCentroid, yCentroid, polygonArea = self.determineCentroidAndArea(orderedPolygonPoints)
						if xCentroid == 'nan' and yCentroid == 'nan' and polygonArea == 'nan':
							errorInPoints = True	
					
					if errorsInPoints == False:	
						# The ordered (anti-clockwise) list of points contains tuples (x, y)
						xSecondMomentOfArea, ySecondMomentOfArea = self.determineSecondMomentsOfArea(orderedPolygonPoints)
						if xSecondMomentOfArea == 'nan' and ySecondMomentOfArea == 'nan':
							errorInPoints = True	
							
					if errorsInPoints == False:	
						xCentroidList.append(xCentroid)
						yCentroidList.append(yCentroid)
						polygonAreaList.append(polygonArea)
						xSecondMomentOfAreaList.append(xSecondMomentOfArea)
						ySecondMomentOfAreaList.append(ySecondMomentOfArea)
						revisedNameOrder.append(key)
						orderedPolygonPointsDictionary.update({key: orderedPolygonPoints})
						centroids.update({key: [(xCentroid, yCentroid)]})
					else:
						xCentroidList.append('nan')
						yCentroidList.append('nan')
						polygonAreaList.append('nan')
						xSecondMomentOfAreaList.append('nan')
						ySecondMomentOfAreaList.append('nan')
						
				else:
					xCentroidList.append('nan')
					yCentroidList.append('nan')
					polygonAreaList.append('nan')
					xSecondMomentOfAreaList.append('nan')
					ySecondMomentOfAreaList.append('nan')
			
			dictData.update({self.MethodText + self.Prefix + self.YAxisTitleSubString + settings["andText"] + settings["spaceText"] + self.XAxisTitleSubString + settings["xCentroidText"] + settings["spaceText"] + settings["speciesName"]: xCentroidList})
			dictData.update({self.MethodText + self.Prefix + self.YAxisTitleSubString + settings["andText"] + settings["spaceText"] + self.XAxisTitleSubString + settings["yCentroidText"] + settings["spaceText"] + settings["speciesName"]: yCentroidList})
			dictData.update({self.MethodText + self.Prefix + self.YAxisTitleSubString + settings["andText"] + settings["spaceText"] + self.XAxisTitleSubString + settings["areaText"] + settings["spaceText"] + settings["speciesName"]: polygonAreaList})
			dictData.update({self.MethodText + self.Prefix + self.YAxisTitleSubString + settings["andText"] + settings["spaceText"] + self.XAxisTitleSubString + settings["iXText"] + settings["spaceText"] + settings["speciesName"]: xSecondMomentOfAreaList})
			dictData.update({self.MethodText + self.Prefix + self.YAxisTitleSubString + settings["andText"] + settings["spaceText"] + self.XAxisTitleSubString + settings["iYText"] + settings["spaceText"] + settings["speciesName"]: ySecondMomentOfAreaList})
			
			# Create plot dictionary
			plotDictionary = self.createPlotDictionary(settings, revisedNameOrder, orderedPolygonPointsDictionary, centroids)
			
			# Transfer plotDictionary to file
			csvTools.transferDictionaryToFile(settings, plotDictionary, self.PlotDataFile, "polygonData")
			
			return dictData, revisedNameOrder, orderedPolygonPointsDictionary, centroids

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


	# Number of outliers to remove
	def numberOfOutliersToRemove(self, numberOfPoints, suggestedNumberToRemove):

		try:
			if numberOfPoints <= 5:
				# Don't remove any points if 5 or less exists
				numberOfOutliersToRemove = 0
				
			elif 5 < numberOfPoints <= 10:
				# Where between 6 and 10 points exists, if the user has indicated outliers to be removed, restrict the number to be remove to 1
				if suggestedNumberToRemove > 0:
					 numberOfOutliersToRemove = 1
				else:
					numberOfOutliersToRemove = 0
			
			elif numberOfPoints > 10:
				# Where more than 10 points exists, if the user has indicated outliers to be removed, restrict the number such that 10 remain
				if suggestedNumberToRemove > 0:
					if suggestedNumberToRemove > (numberOfPoints - 10):
						  numberOfOutliersToRemove = numberOfPoints - 10
					else:
						numberOfOutliersToRemove = suggestedNumberToRemove
				else:
					numberOfOutliersToRemove = 0
					
			return numberOfOutliersToRemove
			
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


	# Create an ordered polygon points list
	def orderedPolygonPointsList(self, points):
		
		try:
			# With respect to the points list, determine the points with the minimum and maximum x values (i.e., minPt, maxPt).
			# Assign the remainder of points into a ascending ordered group that sit below the line defined by minPt and maxPt and a descending ordered group that sit above this line.
			# Create an new list of points starting with minPt, then the ordered lower group, then maxPt and then the ordered upper group.
			# The simple non-self-intersecting closed polygon is completed by connecting back to minPt.
			
			if len(points) == 1:
				# Compound defined by one point
				
				orderedPolygonPoints = points
			
			if len(points) == 2:
				# Compound defined by two points
				
				# Determine minPt
				xCordinates = [float(x[0]) for x in points]
				minPt = points[xCordinates.index(min(xCordinates))]
				points.remove(minPt)
				orderedPolygonPoints = [(minPt[0], minPt[1])]
				orderedPolygonPoints.append((points[0], points[1]))	
			
			if len(points) > 2:
				# Compound defined by three or more points
				
				# Determine minPt
				xCordinates = [float(x[0]) for x in points]
				minPt = points[xCordinates.index(min(xCordinates))]
				points.remove(minPt)
				
				# Determine maxPt
				xCordinates = [float(x[0]) for x in points]
				maxPt = points[xCordinates.index(max(xCordinates))]
				points.remove(maxPt)
												
				# Define the linear algorithm linking minPt and maxPt	
				slope = float(maxPt[1] - minPt[1]) / float(maxPt[0] - minPt[0])
				intercept = float(maxPt[1]) - (float(slope) * float(maxPt[0]))
						
				# Create empty list of points below and above the line
				pointsBelowLine = []
				pointsAboveLine = []
				
				for point in points:
					# For each point calculate y using the algorithm y = slope * x + intercept
					yCalculated = (float(slope) * float(point[0])) + float(intercept)
					
					# Calculate the deltaY = yCalculated - point[1]
					deltaY = float(yCalculated) - float(point[1])
					
					if float(slope) >= 0:
						if deltaY >= 0:
							# Point is below the line
							pointsBelowLine.append(point)
						
						elif deltaY < 0:
							# Point is above the line
							pointsAboveLine.append(point)
							
					elif float(slope) < 0:				
						if deltaY >= 0:
							# Point is below the line
							pointsBelowLine.append(point)
							
						elif deltaY < 0:
							# Point is above the line
							pointsAboveLine.append(point)

				pointsBelowLineSorted =  sorted(pointsBelowLine, key=lambda x: (x[0],x[1]))
				pointsAboveLineSorted =  sorted(pointsAboveLine, key=lambda x: (x[0],x[1]), reverse=True)
			
				orderedPolygonPoints = [(minPt[0], minPt[1])]		
				if len(pointsBelowLineSorted) > 0:
					# A point or points exist below the line
					for point in pointsBelowLineSorted:
						orderedPolygonPoints.append((point[0], point[1]))	
					orderedPolygonPoints.append((maxPt[0], maxPt[1]))
				else:
					# No points exist below the line
					orderedPolygonPoints.append((maxPt[0], maxPt[1]))
				
				if len(pointsAboveLineSorted) > 0:
					# A point or points exist above the line
					for point in pointsAboveLineSorted:
						orderedPolygonPoints.append((point[0], point[1]))
					orderedPolygonPoints.append((minPt[0], minPt[1]))
				else:
					# No points exist above the line
					orderedPolygonPoints.append((minPt[0], minPt[1]))
	
			return orderedPolygonPoints
		
		except ValueError:
			return False
			
		except ZeroDivisionError:
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
	

	# Determine means for x and y values
	def determineMeans(self, points):
		
		try:
			sumX = sum(float(x) for x,y in points)
			sumY = sum(float(y) for x,y in points)
			xMean = float(sumX / len(points))
			yMean = float(sumY / len(points))
			
			if self.isFloat(xMean) != True:
				xMean = 'nan'
			
			if self.isFloat(yMean) != True:
				yMean = 'nan'
			
			return xMean, yMean
			
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


	# Filter ordered polygon points list to remove the required number of the furtherest away points
	def filterOrderedPolygonPoints(self, points, numberOfOutliersToRemove, xMean, yMean):

		try:
			pointToMeanDistances = {}
			for point in points:
				distance = self.calculatePointToMeanDistance(point[0], point[1], xMean, yMean)
				if distance != 'nan':
					pointToMeanDistances.update({point:distance})
		
			if len(pointToMeanDistances) > numberOfOutliersToRemove + 4:
				for i in range(numberOfOutliersToRemove):
					maxDistanceKey = max(pointToMeanDistances, key=pointToMeanDistances.get)
					for j, value in enumerate(points):
						if value == maxDistanceKey:
							del points[j]					
					del pointToMeanDistances[maxDistanceKey]
				
				filteredOrderedPolygonPoints = points
						
				return filteredOrderedPolygonPoints
			else:
				return False

		except ValueError:
			return False
			
		except ZeroDivisionError:
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


	# Calculate point to centroid distance
	def calculatePointToMeanDistance(self, xI, yI, xMean, yMean):

		try:
			import math
			
			if xI == xMean and yI == yMean:
				# This should not occur
				distance = 0
			
			elif xI == xMean and yI != yMean:
				# Straight line in y axis
				distance = abs(yI - yMean)
			
			elif xI != xMean and yI == yMean:
				# Straight line in x axis
				distance = abs(xI - xMean)
			
			elif xI != xMean and yI != yMean:
				# Use Pythagoras theorem
				xDistanceSquared = math.pow(abs(xI - xMean), 2)
				yDistanceSquared = math.pow(abs(yI - yMean), 2)
				distance = math.pow((xDistanceSquared + yDistanceSquared), 0.5)
				
			return distance

		except ValueError:
			return 'nan'
			
		except ZeroDivisionError:
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
			
				
	# Determine a polygon's centroid and area
	def determineCentroidAndArea(self, points):
		# Apply Gauss's area formula for a simple non-self-intersecting closed polygon - vertices are described by the Cartesian coordinates in the plane
			
		try:
			if len(points) == 1:
				# Compound defined by one point
				
				xCentroid = float(points[0][0])
				yCentroid = float(points[0][1])
				polygonArea = float('NaN')
			
			elif len(points) == 2:
				# Compound defined by two points
				
				xCentroid = float((float(points[0][0]) + float(points[1][0])) / 2)
				yCentroid = float((float(points[0][1]) + float(points[1][1])) / 2)
				polygonArea = float('NaN')
		
			elif len(points) > 2:
				# Compound defined by three or more points
				
				sumX = 0
				sumY = 0
				sumArea = 0
				for i in range(len(points)):
					if i < (len(points) - 1):
						sumX = sumX + ((float(points[i][0]) + float(points[i + 1][0])) * ((float(points[i][0]) * float(points[i + 1][1])) - (float(points[i + 1][0]) * float(points[i][1]))))
						sumY = sumY + ((float(points[i][1]) + float(points[i + 1][1])) * ((float(points[i][0]) * float(points[i + 1][1])) - (float(points[i + 1][0]) * float(points[i][1]))))
						sumArea = sumArea + ((float(points[i][0]) * float(points[i + 1][1])) - (float(points[i + 1][0]) * float(points[i][1])))
					
				polygonArea = 0.5 * float(sumArea)
				xCentroid = float(sumX) / (6 * float(polygonArea))
				yCentroid = float(sumY) / (6 * float(polygonArea))
				
			return xCentroid, yCentroid, polygonArea
		
		except ValueError:
			return 'nan', 'nan', 'nan'
			
		except ZeroDivisionError:
			return 'nan', 'nan', 'nan'
			
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


	# Determine a polygon's second moment of area
	def determineSecondMomentsOfArea(self, points):
		# Reflects the distribution of a simple non-self-intersecting closed polygon's points in the x-axis and y-axis
			
		try:
			if len(points) == 1:
				# Compound defined by one point
				
				xSecondMomentOfArea = float('Nan')
				ySecondMomentOfArea = float('Nan')
			
			elif len(points) == 2:
				# Compound defined by two points
				
				xSecondMomentOfArea = float('Nan')
				ySecondMomentOfArea = float('Nan')
			
			elif len(points) > 2:
				# Compound defined by three or more points
				
				import math
				sumX = 0
				sumY = 0
				for i in range(len(points)):
					if i < (len(points) - 1):
						sumX = sumX + ((math.pow(float(points[i][1]),2) + (float(points[i][1]) * float(points[i + 1][1])) + math.pow(float(points[i + 1][1]),2)) * ((float(points[i][0]) * float(points[i + 1][1])) - (float(points[i + 1][0]) * float(points[i][1]))))
						sumY = sumY + ((math.pow(float(points[i][0]),2) + (float(points[i][0]) * float(points[i + 1][0])) + math.pow(float(points[i + 1][0]),2)) * ((float(points[i][0]) * float(points[i + 1][1])) - (float(points[i + 1][0]) * float(points[i][1]))))

				xSecondMomentOfArea = float(sumX) / 12
				ySecondMomentOfArea = float(sumY) / 12

			return xSecondMomentOfArea, ySecondMomentOfArea
		
		except ValueError:
			return 'nan', 'nan'
		
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


	# Create plot dictionary
	def createPlotDictionary(self, settings, revisedNameOrder, orderedPolygonPointsDictionary, centroids):

		try:
			#
			# Note, the unique names stored in revisedNameOrder and used as keys in orderedPolygonPointsDictionary and centroids take the form: name + settings[nameSubstring] + groupReference.
			# For the purpose of exporting to file - need to remove the "+ settings[nameSubstring] + groupReference" suffix.
			# This can be done using name.split(settings["nameSubstring"])[0]
			#
			
			columnHeaders = [settings["xDataText"]]
			for name in orderedPolygonPointsDictionary:
				columnHeaders.append(name)
				columnHeaders.append(str(name) + str(settings["centroidText"]))
			
			# Create a list of lists containing a column header as the first element in each list.
			listOfLists = [[columnHeader] for columnHeader in columnHeaders]
			
			# Loop through each name in revisedNameOrder
			for name in revisedNameOrder:
				# Loop through list of tuples in each orderedPolygonPointsDictionary's key-value
				for tupleValue in orderedPolygonPointsDictionary[name]:
					# Add the first tuple element to the settings["xDataText"] list and the second tuple element to the approriate list in the listOfLists and "" to all the other lists within the listOfLists
					for columnHeader in columnHeaders:
						if columnHeader == name:
							listOfLists[columnHeaders.index(settings["xDataText"])].append(tupleValue[0]) 
							listOfLists[columnHeaders.index(columnHeader)].append(tupleValue[1])
						elif columnHeader != settings["xDataText"]:
							listOfLists[columnHeaders.index(columnHeader)].append("")

				# Add centroid tuple details for the compound
				for columnHeader in columnHeaders:
					if columnHeader == str(name) + str(settings["centroidText"]):
						listOfLists[columnHeaders.index(settings["xDataText"])].append(centroids[name][0][0]) 
						listOfLists[columnHeaders.index(columnHeader)].append(centroids[name][0][1])
					elif columnHeader != settings["xDataText"]:
						listOfLists[columnHeaders.index(columnHeader)].append("")

			# Dictionary comprehension: parse the list of lists into a dictionary by setting the first element in each list (i.e.; the column columnHeader) as the "key" and the rest of the list as the "value" for each "key:value" pair of the dictionary
			plotDictionary = {listX[0]:listX[1:] for listX in listOfLists}

			return plotDictionary
			
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
			
