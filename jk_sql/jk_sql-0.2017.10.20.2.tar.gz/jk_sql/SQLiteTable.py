#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

import sqlite3

from .AbstractDBTable import *





class SQLiteTable(AbstractDBTable):



	def __init__(self, db, tableName, columnDefs):
		assert db.__class__.__name__ == "SQLiteDB"
		super().__init__(db, tableName, columnDefs)
	#



	@staticmethod
	def loadFromJSON(db, jsonDef):
		colDefs = []
		for jsonColDef in jsonDef["columns"]:
			colDefs.append(DBColDef.loadFromJSON(jsonColDef))
		return SQLiteTable(db, jsonDef["name"], colDefs)
	#



	#
	# Remove a column.
	#
	def removeColumn(self, columnName):
		currentColumns = self.columns
		newColumns = []
		columnMapping = {}
		for col in currentColumns:
			if col.name != columnName:
				newColumns.append(col)
				columnMapping[col.name] = col.name
		if len(currentColumns) == len(newColumns):
			raise Exception("No such column: " + columnName)

		with self._db._dbConnection:
			self._beginTA()

			# rename existing table
			tableName = self.name
			tempTableName = "tmp_" + self.name
			sql = self._db._sqlFactory.sqlStmt_renameTable(tableName, tempTableName)
			self._db._dbConnection.execute(sql)
			self._name = tempTableName

			# create table
			tableDef = DBTableDef(tableName, newColumns)
			sql = self._db._sqlFactory.sqlStmt_createTable(tableDef)
			self._db._dbConnection.execute(sql)
			for colDef in tableDef.columns:
				if colDef.index != EnumDBIndexType.NONE:
					sql = self._db._sqlFactory.sqlStmt_createIndex(tableDef, colDef)
					self._db._dbConnection.execute(sql)
			newTable = SQLiteTable(self._db, tableDef.name, tableDef.columns)

			# copy data
			self.copyToOtherTable(newTable, columnMapping)

			# delete temporary table
			sql = self._db._sqlFactory.sqlStmt_dropTable(self)
			self._db._dbConnection.execute(sql)

		# accept current data
		self._name = tableName
		self._columnDefs = newColumns
		self._reconstructInternalData()
	#



#











