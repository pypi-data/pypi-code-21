#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

import sqlite3

from .DBColDef import *
from .DBTableDef import *





class AbstractDBTable(object):



	def __init__(self, db, tableName, columnDefs):
		assert isinstance(db, object)
		assert isinstance(tableName, str)
		if isinstance(columnDefs, tuple):
			columnDefs = list(columnDefs)
		else:
			assert isinstance(columnDefs, list)

		self._db = db
		#self._db.isolation_level = None
		self._name = tableName
		self._columnDefs = columnDefs
		self._columnDefsByName = None
		self._columnDefsNameToIndex = None
		self.__cachedColumnNames = None

		self._reconstructInternalData()
	#



	def _reconstructInternalData(self):
		self._columnDefsByName = {}
		self._columnDefsNameToIndex = {}

		count = 0
		for colDef in self._columnDefs:
			assert isinstance(colDef, DBColDef)
			self._columnDefsByName[colDef.name] = colDef
			self._columnDefsNameToIndex[colDef.name] = count
			count += 1

		self.__cachedColumnNames = None
	#



	def toJSON(self):
		columns = []
		for colDef in self._columnDefs:
			columns.append(colDef.toJSON())

		return {
			"name" : self._name,
			"columns" : columns
		}
	#



	# ----------------------------------------------------------------



	@property
	def name(self):
		return self._name
	#



	#
	# Returns the list of columns in this table.
	#
	# @return	DBColDef[]		Returns a list of column definition objects.
	#
	@property
	def columns(self):
		return tuple(self._columnDefs)
	#



	#
	# Get a specific column.
	#
	def getColumn(self, nameOrIndex):
		if isinstance(nameOrIndex, str):
			return self._columnDefsByName.get(nameOrIndex, None)
		elif isinstance(nameOrIndex, int):
			if (nameOrIndex < 0) or (nameOrIndex >= len(self._columnDefs)):
				return None
			else:
				return self._columnDefs[nameOrIndex]
		else:
			raise Exception("Unexpected type: " + str(type(nameOrIndex)))
	#



	#
	# Get a specific column.
	#
	def getColumnE(self, nameOrIndex):
		if isinstance(nameOrIndex, str):
			columnDef = self._columnDefsByName.get(nameOrIndex, None)
		elif isinstance(nameOrIndex, int):
			if (nameOrIndex < 0) or (nameOrIndex > len(self._columnDefs)):
				columnDef = None
			else:
				columnDef = self._columnDefs[nameOrIndex]
		else:
			raise Exception("Unexpected type: " + str(type(nameOrIndex)))
		if columnDef is None:
			raise Exception("No such column: " + nameOrIndex)
		else:
			return columnDef
	#



	#
	# Returns the list of column names in this table.
	#
	# @return	str[]		Returns a string list containing all column names.
	#
	@property
	def columnNames(self):
		if self.__cachedColumnNames is None:
			self.__cachedColumnNames = []
			for colDef in self._columnDefs:
				self.__cachedColumnNames.append(colDef.name)
		return self.__cachedColumnNames
	#



	@property
	def pkColumn(self):
		for c in self._columnDefs:
			if c.type == EnumDBColType.PK:
				return c
		return None
	#



	# ----------------------------------------------------------------



	def _beginTA(self):
		sql = self._db._sqlFactory.sqlStmt_beginTA()
		self._db._dbConnection.execute(sql)
	#



	def modifyColumn(self, columnName, newColDef):
		assert isinstance(columnName, str)
		assert isinstance(newColDef, DBColDef)

		curColDef = self.getColumnE(columnName)

		# determine if we need to drop and recreate the index
		# we need to do this if there is a type change or even if the name of the column has changed
		bDropIndex = False
		bCreateIndex = False
		if curColDef.index == newColDef.index:
			if (curColDef.type != newColDef.type) or (curColDef.name != newColDef.name):
				bDropIndex = True
				bCreateIndex = True
		else:
			if curColDef.index != EnumDBIndexType.NONE:
				bDropIndex = True
			if newColDef.index != EnumDBIndexType.NONE:
				bCreateIndex = True
		bRenameColumn = curColDef.name != newColDef.name
		bRenameByCopy = False
		if bRenameColumn:
			if newColDef.name in self._columnDefsByName:
				raise Exception("Can't rename column because another column of that name already exists: " + newColDef.name + "!")
			if not self._db._sqlFactory.supportsRenameColumn:
				if self._db._sqlFactory.supportsCopyColumn:
					if self._db._sqlFactory.supportsDropColumn:
						bRenameByCopy = True
					else:
						raise Exception("Renaming columns is not supported by databases of type " + self._db._sqlFactory.dbTypeName + "!")
				else:
					raise Exception("Renaming columns is not supported by databases of type " + self._db._sqlFactory.dbTypeName + "!")
		bModifyColumn = (curColDef.type != newColDef.type) or (curColDef.nullable != newColDef.nullable)
		if bModifyColumn:
			if not self._db._sqlFactory.supportsModifyColumn:
				raise Exception("Modifying columns is not supported by databases of type " + self._db._sqlFactory.dbTypeName + "!")
			if (curColDef.type == EnumDBColType.PK) and (newColDef.type != EnumDBColType.PK):
				raise Exception("Primary keys can not be changed!")
			if (newColDef.type == EnumDBColType.PK) and (newColDef.type != EnumDBColType.PK):
				raise Exception("Can't modify column to be primary key!")

		with self._db._dbConnection:
			self._beginTA()

			if bDropIndex:
				# drop index
				sql = self._db._sqlFactory.sqlStmt_dropIndex(self, curColDef)
				self._db._dbConnection.execute(sql)
				curColDef = DBColDef(curColDef.name, curColDef.type, curColDef.nullable, EnumDBIndexType.NONE)

			if bRenameColumn:
				if bRenameByCopy:
					# create new column
					sql = self._db._sqlFactory.sqlStmt_addTableColumn(self, newColDef)
					self._db._dbConnection.execute(sql)
					# copy column
					sql = self._db._sqlFactory.sqlStmt_copyTableColumn(self, curColDef, newColDef)
					self._db._dbConnection.execute(sql)
					# drop old column
					sql = self._db._sqlFactory.sqlStmt_dropTableColumn(self, curColDef)
					self._db._dbConnection.execute(sql)
				else:
					# rename column
					sql = self._db._sqlFactory.sqlStmt_renameTableColumn(self, curColDef, newColDef.name)
					self._db._dbConnection.execute(sql)
				curColDef = DBColDef(newColDef.name, curColDef.type, curColDef.nullable, curColDef.index)

			if bModifyColumn:
				# modify column
				sql = self._db._sqlFactory.sqlStmt_modifyTableColumn(self, curColDef, newColDef)
				self._db._dbConnection.execute(sql)
				curColDef = DBColDef(newColDef.name, newColDef.type, newColDef.nullable, curColDef.index)

			if bCreateIndex:
				# create index
				sql = self._db._sqlFactory.sqlStmt_createIndex(self, curColDef)
				self._db._dbConnection.execute(sql)
				curColDef = DBColDef(curColDef.name, curColDef.type, curColDef.nullable, newColDef.index)

		self._columnDefsByName[columnName] = curColDef
		n = self._columnDefsNameToIndex[columnName]
		self._columnDefs[n] = curColDef
		self._db._storeDataModel()
	#



	#
	# Remove a column.
	#
	# @TODO Not implemented yet!
	#
	def removeColumn(self, columnName):
		raise NotImplementedError()
	#



	#
	# Be aware that an index might be created here. SQLite might fail during index creation. This is NOT wrapped in a transaction.
	#
	def addColumn(self, colDef):
		assert isinstance(colDef, DBColDef)
		if colDef.name in self._columnDefsByName:
			raise Exception("Column already defined: " + str(colDef))
		if (colDef.type == EnumDBColType.PK) and (self.pkColumn != None):
			raise Exception("Can't create a second primary key column!")
		if (colDef.type != EnumDBColType.PK) and not colDef.nullable and colDef.unique:
			n = self.countRows()
			if n > 1:
				raise Exception("Can't create unique index on table if no distinct values have been stored in the new column! The values wouldn't be unique!")

		with self._db._dbConnection:
			self._beginTA()
			sql = self._db._sqlFactory.sqlStmt_addTableColumn(self, colDef)
			self._db._dbConnection.execute(sql)

			if colDef.index != EnumDBIndexType.NONE:
				sql = self._db._sqlFactory.sqlStmt_createIndex(self, colDef)
				self._db._dbConnection.execute(sql)

		count = len(self._columnDefs)
		self._columnDefs.append(colDef)
		self._columnDefsByName[colDef.name] = colDef
		self._columnDefsNameToIndex[colDef.name] = count

		if self.__cachedColumnNames != None:
			self.__cachedColumnNames.append(colDef.name)

		self._db._storeDataModel()
	#



	#
	# Add a single row to the table.
	#
	# @param	dict fieldData				A hash map containing the data
	# @param	str[] limitToColumnNames	If not <c>None</c> ignores other keys in the maps in <c>fieldDataList</c> than the ones specified here.
	#
	def addRow(self, fieldData, limitToColumnNames = None):
		assert isinstance(fieldData, dict)

		if limitToColumnNames != None:
			assert isinstance(limitToColumnNames, (tuple, list))
		else:
			limitToColumnNames = fieldData.keys()
		for columnName in limitToColumnNames:
			assert isinstance(columnName, str)
		existingColumnNames = set(self.columnNames)
		columnNames = []
		for columnName in limitToColumnNames:
			if columnName in existingColumnNames:
				columnNames.append(columnName)
			else:
				raise Exception("Invalid column names: " + str(limitToColumnNames))

		dataValueList = []
		for key in columnNames:
			dataValueList.append(fieldData.get(key, None))

		with self._db._dbConnection:
			self._beginTA()
			sql = self._db._sqlFactory.sqlStmt_insertRowIntoTable(self, columnNames)
			self._db._dbConnection.execute(sql, dataValueList)

		#self._commitTA(c)
	#



	#
	# Add a varieties of rows to the table.
	#
	# @param	list<dict> fieldDataList		A list of hash maps containing the data
	# @param	str[] limitToColumnNames	If not <c>None</c> ignores other keys in the maps in <c>fieldDataList</c> than the ones specified here.
	#
	def addRows(self, fieldDataList, limitToColumnNames = None):
		assert isinstance(fieldDataList, list)
		for fieldData in fieldDataList:
			assert isinstance(fieldData, dict)

		if limitToColumnNames != None:
			assert isinstance(limitToColumnNames, (tuple, list))
		else:
			limitToColumnNames = set()
			for fieldData in fieldDataList:
				limitToColumnNames.update(fieldData.keys())
		for columnName in limitToColumnNames:
			assert isinstance(columnName, str)
		existingColumnNames = set(self.columnNames)
		columnNames = []
		for columnName in limitToColumnNames:
			if columnName in existingColumnNames:
				columnNames.append(columnName)
			else:
				raise Exception("Invalid column names: " + str(limitToColumnNames))

		sql = self._db._sqlFactory.sqlStmt_insertRowIntoTable(self, columnNames)

		with self._db._dbConnection:
			self._beginTA()
			for fieldData in fieldDataList:
				dataValueList = []
				for key in columnNames:
					dataValueList.append(fieldData.get(key, None))
				self._db._dbConnection.execute(sql, dataValueList)
	#



	def updateRows(self, fieldData, filter, limitToColumnNames = None):
		assert isinstance(fieldData, dict)

		if limitToColumnNames != None:
			assert isinstance(limitToColumnNames, (tuple, list))
		else:
			limitToColumnNames = fieldData.keys()
		for columnName in limitToColumnNames:
			assert isinstance(columnName, str)
		existingColumnNames = set(self.columnNames)
		columnNames = []
		for columnName in limitToColumnNames:
			if columnName in existingColumnNames:
				columnNames.append(columnName)
			else:
				raise Exception("Invalid column names: " + str(limitToColumnNames))

		sql, filterValues = self._db._sqlFactory.sqlStmt_updateRowInTable(self, columnNames, filter)

		with self._db._dbConnection:
			self._beginTA()
			dataValueList = []
			for key in columnNames:
				dataValueList.append(fieldData.get(key, None))
			dataValueList.extend(filterValues)
			self._db._dbConnection.execute(sql, dataValueList)
	#



	def deleteRows(self, filter):
		sql, filterValues = self._db._sqlFactory.sqlStmt_deleteRowsFromTable(self, filter)

		with self._db._dbConnection:
			self._beginTA()
			self._db._dbConnection.execute(sql, filterValues)
	#



	def countRows(self, filter = None):
		if filter != None:
			assert isinstance(filter, dict)

		sql, filterValues = self._db._sqlFactory.sqlStmt_countRowsInTable(self, filter)

		c = self._db._dbConnection.cursor()
		ret = c.execute(sql, filterValues).fetchone()
		c.close()

		return ret[0]
	#



	def getRow(self, filter = None):
		if filter != None:
			assert isinstance(filter, dict)

		sql, filterValues = self._db._sqlFactory.sqlStmt_selectSingleRowFromTable(self, filter)

		c = self._db._dbConnection.cursor()
		ret = c.execute(sql, filterValues).fetchone()
		c.close()
		return ret
	#



	def getRows(self, filter = None):
		if filter != None:
			assert isinstance(filter, dict)

		sql, filterValues = self._db._sqlFactory.sqlStmt_selectMultipleRowsFromTable(self, filter)

		c = self._db._dbConnection.cursor()
		ret = c.execute(sql, filterValues).fetchall()
		c.close()
		return ret
	#



	def getDistinct(self, columnNames, filter = None):
		if filter != None:
			assert isinstance(filter, dict)

		columnDefs = []
		assert isinstance(columnNames, list)
		for columnName in columnNames:
			assert isinstance(columnName, str)
			columnDefs.append(self.getColumnE(columnName))

		sql, filterValues = self._db._sqlFactory.sqlStmt_selectDistinctValuesFromTable(self, columnDefs, filter)

		c = self._db._dbConnection.cursor()
		ret = c.execute(sql, filterValues).fetchall()
		c.close()
		return ret
	#



	def getRowIterator(self, filter = None):
		if filter != None:
			assert isinstance(filter, dict)

		sql, filterValues = self._db._sqlFactory.sqlStmt_selectMultipleRowsFromTable(self, filter)

		c = self._db._dbConnection.cursor()
		for row in c.execute(sql, filterValues).fetchall():
			yield row
		c.close()
	#



	def copyToOtherTable(self, otherTable, columnMapping):
		assert isinstance(otherTable, AbstractDBTable)
		if otherTable._db != self._db:
			raise Exception("Can't copy table to other data base!")
		assert isinstance(columnMapping, (tuple, list, dict))

		existingFromColumns = set(self.columnNames)
		existingToColumns = set(otherTable.columnNames)

		fromColumns = []
		toColumns = []
		if isinstance(columnMapping, (tuple, list)):
			for fromColumn, toColumn in columnMapping:
				if (fromColumn != None) and (toColumn != None):
					if fromColumn not in existingFromColumns:
						raise Exception("No such source column: " + fromColumn)
					if toColumn not in existingToColumns:
						raise Exception("No such destination column: " + toColumn)
					fromColumns.append(fromColumn)
					toColumns.append(toColumn)
		else:
			for fromColumn in columnMapping:
				toColumn = columnMapping[fromColumn]
				if toColumn != None:
					if fromColumn not in existingFromColumns:
						raise Exception("No such source column: " + fromColumn)
					if toColumn not in existingToColumns:
						raise Exception("No such destination column: " + toColumn)
					fromColumns.append(fromColumn)
					toColumns.append(toColumn)

		sql = self._db._sqlFactory.sqlStmt_insertFromTableIntoTable(self, fromColumns, otherTable, toColumns)

		with self._db._dbConnection:
			self._beginTA()
			self._db._dbConnection.execute(sql)
	#



	# ----------------------------------------------------------------



	def __str__(self):
		s = "sqlite-table: " + self._name + " [ "
		bRequiresComma = False
		for col in self._columnDefs:
			if bRequiresComma:
				s += ", "
			s += col.name + ":" + str(col.type)
			bRequiresComma = True
		s += " ]"
		return s
	#



	def __repr__(self):
		return self.__str__()
	#



#











