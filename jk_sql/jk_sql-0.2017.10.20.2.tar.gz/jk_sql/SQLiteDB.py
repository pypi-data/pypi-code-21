#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import codecs
import json
import sys

import sqlite3

from .SQLFactorySQLite import *
from .SQLiteTable import *




class SQLiteDB(object):

	def __init__(self, dbConnection, dataModelContainer):
		self.__dbConnection = dbConnection
		self.__sqlFactory = SQLFactorySQLite()
		self.__dataModelContainer = dataModelContainer

		model = dataModelContainer.loadDataModel()
		if model != None:
			self.__loadDataModel(model)
		else:
			self.__tables = []
			self.__tablesByName = {}
	#

	# ----------------------------------------------------------------

	def __loadDataModel(self, jsonRawModel):
		self.__tables = []
		self.__tablesByName = {}

		for jsonTableDef in jsonRawModel["tables"]:
			t = SQLiteTable.loadFromJSON(self, jsonTableDef)
			self.__tables.append(t)
			self.__tablesByName[t.name] = t
	#

	def _storeDataModel(self):
		self.__dataModelContainer.storeDataModel(self.__tables)
	#

	# ----------------------------------------------------------------

	def __str__(self):
		return "SQLiteDB()"
	#

	def __repr__(self):
		return "SQLiteDB()"
	#

	# ----------------------------------------------------------------

	@property
	def _sqlFactory(self):
		return self.__sqlFactory
	#

	@property
	def _dbConnection(self):
		return self.__dbConnection
	#

	# ----------------------------------------------------------------

	def getCreateTable(self, tableDef):
		t = self.__tablesByName.get(tableDef.name, None)
		if t != None:
			return t
		return self.createTable(tableDef)
	#

	def getTable(self, tableName):
		return self.__tablesByName.get(tableName, None)
	#

	def getTableE(self, tableName):
		return self.__tablesByName[tableName]
	#

	def _verifyTableDefinition(self, tableDef):
		supportedDataTypes = self._sqlFactory.supportedDataTypes
		existingNames = set()
		for colDef in tableDef.columns:
			if colDef.name in existingNames:
				raise Exception("Duplicate column name detected: " + colDef.name)
			existingNames.add(colDef.name)
			if colDef.type not in supportedDataTypes:
				raise Exception("Unsupported data type \"" + str(colDef.type) + "\" at column: " + colDef.name)
	#

	def createTable(self, tableDef):
		assert isinstance(tableDef, DBTableDef)

		self._verifyTableDefinition(tableDef)

		if tableDef.name in self.__tablesByName:
			raise Exception("Table already exists!")

		sql = self.__sqlFactory.sqlStmt_createTable(tableDef)
		self.__dbConnection.execute(sql)

		for colDef in tableDef.columns:
			if colDef.index != EnumDBIndexType.NONE:
				sql = self.__sqlFactory.sqlStmt_createIndex(tableDef, colDef)
				self.__dbConnection.execute(sql)

		t = SQLiteTable(self, tableDef.name, tableDef.columns)
		self.__tables.append(t)
		self.__tablesByName[t.name] = t

		self._storeDataModel()
		return t
	#

#











