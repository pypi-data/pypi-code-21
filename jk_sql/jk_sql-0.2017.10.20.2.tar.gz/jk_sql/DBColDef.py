#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

import sqlite3

from .EnumDBColType import EnumDBColType
from .EnumDBIndexType import EnumDBIndexType





#
# This class represents a definition of a column. Objects of this type are used to either define a column or get information about a table column.
#
class DBColDef(object):

	def __init__(self, fieldName, fieldType, bIsNullable, indexType):
		assert isinstance(fieldName, str)
		assert isinstance(fieldType, EnumDBColType)
		assert isinstance(bIsNullable, bool)
		assert isinstance(indexType, EnumDBIndexType)

		if fieldType == EnumDBColType.PK:
			bIsNullable = False
			indexType = EnumDBIndexType.NONE

		self.__name = fieldName
		self.__type = fieldType
		self.__bIsNullable = bIsNullable
		self.__indexType = indexType
	#

	@property
	def index(self):
		return self.__indexType
	#

	@property
	def nullable(self):
		return self.__bIsNullable
	#

	@property
	def unique(self):
		return self.__indexType == EnumDBIndexType.UNIQUE_INDEX
	#

	@property
	def type(self):
		return self.__type
	#

	@property
	def name(self):
		return self.__name
	#

	def isEqualWithoutIndex(self, other):
		return (self.__name == other.name) and (self.__type == other.type) and (self.__bIsNullable == other.nullable)
	#

	def __ne__(self, other):
		return (self.__name != other.name) or (self.__type != other.type) or (self.__bIsNullable != other.nullable) or (self.__indexType != other.index)
	#

	def __eq__(self, other):
		return (self.__name == other.name) and (self.__type == other.type) and (self.__bIsNullable == other.nullable) and (self.__indexType == other.index)
	#

	def __str__(self):
		return self.__type + ": " + self.__name
	#

	def __repr__(self):
		return self.__type + ": " + self.__name
	#

	def __copy__(self):
		return DBColDef(self.__name, self.__type, self.__bIsNullable, self.__indexType)
	#

	def __deepcopy__(self, memo):
		return DBColDef(self.__name, self.__type, self.__bIsNullable, self.__indexType)
	#

	@staticmethod
	def loadFromJSON(jsonDef):
		t = jsonDef["type"]
		i = jsonDef["index"]
		return DBColDef(jsonDef["name"], EnumDBColType.parse(t), jsonDef["nullable"], EnumDBIndexType.parse(i))
	#

	def toJSON(self):
		return {
			"name" : self.__name,
			"type" : str(self.__type),
			"nullable" : self.__bIsNullable,
			"index" : str(self.__indexType)
		}
	#



#











