#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

import sqlite3

from .DBColDef import *





#
# This class represents a definition of a table. Objects of this type are used to define a table.
#
class DBTableDef(object):

	def __init__(self, tableName, columnDefs):
		assert isinstance(tableName, str)

		self.__name = tableName
		self.__columnDefs = []
		self.__columnDefsByName = {}
		self.__columnDefsNameToIndex = {}

		if columnDefs != None:
			assert isinstance(columnDefs, (tuple, list))
			i = 0
			for colDef in columnDefs:
				assert isinstance(colDef, DBColDef)
				self.__columnDefs.append(colDef)
				self.__columnDefsByName[colDef.name] = colDef
				self.__columnDefsNameToIndex[colDef.name] = i
				i += 1

		self.__cachedColumnNames = None
	#

	# ----------------------------------------------------------------

	@property
	def name(self):
		return self.__name
	#

	@property
	def columns(self):
		return tuple(self.__columnDefs)
	#

	@property
	def columnNames(self):
		if self.__cachedColumnNames is None:
			self.__cachedColumnNames = []
			for colDef in self.__columnDefs:
				self.__cachedColumnNames.append(colDef.name)
		return self.__cachedColumnNames
	#

	# ----------------------------------------------------------------

	def clone(self, newName = None):
		assert isinstance(newName, str)

		if newName is None:
			newName = self.__name

		colDefs = []
		for c in self.__columnDefs:
			colDefs.append(c.__copy__())

		return DBTableDef(newName, colDefs)
	#

	def addColumn(self, colDef):
		assert isinstance(colDef, DBColDef)
		if colDef.name in self.__columnDefsByName:
			raise Exception("Column already defined: " * str(colDef))
		count = len(self.__columnDefs)
		self.__columnDefs.append(colDef)
		self.__columnDefsByName[colDef.name] = colDef
		self.__columnDefsNameToIndex[colDef.name] = count

		if self.__cachedColumnNames != None:
			self.__cachedColumnNames.append(colDef.name)
	#

	# ----------------------------------------------------------------

	def __copy__(self):
		colDefs = []
		for c in self.__columnDefs:
			colDefs.append(c.__copy__())

		return DBTableDef(self.__name, colDefs)
	#

	def __deepcopy__(self, memo):
		colDefs = []
		for c in self.__columnDefs:
			colDefs.append(c.__copy__())

		return DBTableDef(self.__name, colDefs)
	#

	def __cmp__(self, other):
		return (self.__name == other.__name) \
			and (self.__columnDefs == other.__columnDefs)
	#

	def __str__(self):
		s = "table: " + self.__name + " [ "
		bRequiresComma = False
		for col in self.__columnDefs:
			if bRequiresComma:
				s += ", "
			s += col.name + " " + col.type
			bRequiresComma = True
		s += " ]"
		return s
	#

	def __repr__(self):
		return self.__str__()
	#

#











