#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import collections

import sqlite3

from .DBTableDef import *




#
# Class to produce SQL statments. This class is providing support for the SQLite databases.
#
class SQLFactorySQLite(object):



	def __init__(self, bDebuggingEnabled = False):
		self.__bDebuggingEnabled = bDebuggingEnabled
	#



	# ----------------------------------------------------------------



	@property
	def dbTypeName(self):
		return "SQLite"
	#



	@property
	def supportedDataTypes(self):
		return [ EnumDBColType.PK, EnumDBColType.BOOL, EnumDBColType.INT32, EnumDBColType.INT64, EnumDBColType.DOUBLE,
			EnumDBColType.STR256, EnumDBColType.CLOB, EnumDBColType.BLOB ]
	#



	@property
	def supportsCopyColumn(self):
		return True
	#



	@property
	def supportsDropColumn(self):
		return False
	#



	@property
	def supportsRenameColumn(self):
		return False
	#



	@property
	def supportsModifyColumn(self):
		return False
	#



	# ----------------------------------------------------------------



	def verifyTableDefinition(self, tableDef):
		pass
		# not needed right now
	#



	@staticmethod
	def __toSQLType(dataType):
		if dataType == EnumDBColType.PK:
			return "integer primary key"
		elif dataType == EnumDBColType.BOOL:
			return "int"
		elif dataType == EnumDBColType.INT32:
			return "int"
		elif dataType == EnumDBColType.INT64:
			return "int"
		elif dataType == EnumDBColType.DOUBLE:
			return "real"
		elif dataType == EnumDBColType.STR256:
			return "text"
		elif dataType == EnumDBColType.CLOB:
			return "text"
		elif dataType == EnumDBColType.BLOB:
			return "blob"
		else:
			raise Exception("Type not supported: " + str(EnumDBColType))
	#



	@staticmethod
	def __defaultValue(dataType):
		if dataType == EnumDBColType.PK:
			raise Exception()
		elif dataType == EnumDBColType.BOOL:
			return 0
		elif dataType == EnumDBColType.INT32:
			return 0
		elif dataType == EnumDBColType.INT64:
			return 0
		elif dataType == EnumDBColType.DOUBLE:
			return 0
		elif dataType == EnumDBColType.STR256:
			return ""
		elif dataType == EnumDBColType.CLOB:
			return ""
		elif dataType == EnumDBColType.BLOB:
			return ""
		else:
			raise Exception("Type not supported: " + str(EnumDBColType))
	#



	def sqlStmt_beginTA(self):
		if self.__bDebuggingEnabled:
			print("BEGIN")
		return "BEGIN"
	#



	def sqlStmt_renameTable(self, fromTableName, toTableName):
		assert isinstance(fromTableName, str)
		assert isinstance(toTableName, str)

		s = "ALTER TABLE " + fromTableName + " RENAME TO " + toTableName
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	def sqlStmt_dropTable(self, tableDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]

		s = "DROP TABLE " + tableDef.name
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	def sqlStmt_createTable(self, tableDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]

		s = "CREATE TABLE " + tableDef.name + " ("
		bRequiresComma = False
		for col in tableDef.columns:
			if bRequiresComma:
				s += ", "
			s += col.name + " " + SQLFactorySQLite.__toSQLType(col.type)
			if col.type != EnumDBColType.PK:
				if col.nullable:
					s += " NULL"
				else:
					s += " NOT NULL"
			bRequiresComma = True
		s += ")"
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	def sqlStmt_addTableColumn(self, tableDef, columnDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert columnDef.__class__.__name__ == "DBColDef"

		s = "ALTER TABLE " + tableDef.name + " ADD COLUMN "
		s += columnDef.name + " " + SQLFactorySQLite.__toSQLType(columnDef.type)
		if columnDef.type != EnumDBColType.PK:
			if columnDef.nullable:
				s += " NULL"
			else:
				s += " NOT NULL DEFAULT " + str(SQLFactorySQLite.__defaultValue(columnDef.type))
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	"""
	def sqlStmt_createIndex(self, tableDef, columnDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert columnDef.__class__.__name__ == "DBColDef"

		s = "ALTER TABLE " + tableDef.name + " "
		if columnDef.index == EnumDBIndexType.INDEX:
			s += "ADD INDEX idx_" + columnDef.name + " (" + columnDef.name + " ASC)"
		elif columnDef.index == EnumDBIndexType.UNIQUE_INDEX:
			s += "ADD UNIQUE INDEX idx_" + columnDef.name + " (" + columnDef.name + " ASC)"
		else:
			raise Exception("Unrecognized index: " + str(columnDef.index))
		return s
	#
	"""


	def sqlStmt_createIndex(self, tableDef, columnDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert columnDef.__class__.__name__ == "DBColDef"

		if columnDef.index == EnumDBIndexType.INDEX:
			s = "CREATE INDEX idx_" + tableDef.name + "_" + columnDef.name + " ON " + tableDef.name + " (" + columnDef.name + " ASC)"
		elif columnDef.index == EnumDBIndexType.UNIQUE_INDEX:
			s = "CREATE UNIQUE INDEX idx_" + tableDef.name + "_" + columnDef.name + " ON " + tableDef.name + " (" + columnDef.name + " ASC)"
		else:
			raise Exception("Unrecognized index: " + str(columnDef.index))
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	"""
	def sqlStmt_dropIndex(self, tableDef, columnDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert columnDef.__class__.__name__ == "DBColDef"

		s = "ALTER TABLE " + tableDef.name + " DROP INDEX idx_" + columnDef.name
		return s
	#
	"""



	def sqlStmt_dropIndex(self, tableDef, columnDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert columnDef.__class__.__name__ == "DBColDef"

		s = "DROP INDEX idx_" + tableDef.name + "_" + columnDef.name
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	def sqlStmt_dropTableColumn(self, tableDef, columnDef):
		raise Exception("Not supported!")
	#



	#
	# rename a table column
	#
	def sqlStmt_renameTableColumn(self, tableDef, oldColumnDef, newName):
		raise Exception("Not supported!")
	#



	"""
	def sqlStmt_renameTableColumn(self, tableDef, oldColumnDef, newName):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert oldColumnDef.__class__.__name__ == "DBColDef"
		assert isinstance(newName, str)

		s = "ALTER TABLE " + tableDef.name + " RENAME COLUMN "
		s += oldColumnDef.name + " " + newName
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#
	"""



	#
	# Modify the type of column
	#
	def sqlStmt_modifyTableColumn(self, tableDef, oldColumnDef, newColumnDef):
		raise Exception("Not supported!")
	#



	"""
	def sqlStmt_modifyTableColumn(self, tableDef, oldColumnDef, newColumnDef):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert oldColumnDef.__class__.__name__ == "DBColDef"
		assert newColumnDef.__class__.__name__ == "DBColDef"

		if oldColumnDef.name != newColumnDef.name:
			raise Exception("Can't rename column!")

		s = "ALTER TABLE " + tableDef.name + " CHANGE COLUMN "
		s += oldColumnDef.name + " "
		s += oldColumnDef.name + " " + SQLFactorySQLite.__toSQLType(newColumnDef.type)
		if newColumnDef.nullable:
			s += " NULL"
		else:
			s += " NOT NULL"
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#
	"""



	def sqlStmt_insertRowIntoTable(self, tableDef, dataKeys):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert isinstance(dataKeys, (tuple, list, collections.Iterable))

		s1 = "INSERT INTO " + tableDef.name + " ("
		s2 = ") VALUES ("
		bComma = False
		for key in dataKeys:
			assert isinstance(key, str)
			if bComma:
				s1 += ","
				s2 += ","
			else:
				bComma = True
			s1 += key
			s2 += "?"
		s = s1 + s2 + ")"
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	def sqlStmt_insertFromTableIntoTable(self, fromTableDef, fromDataKeys, intoTableDef, intoDataKeys):
		assert fromTableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert isinstance(fromDataKeys, (tuple, list, collections.Iterable))
		assert intoTableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert isinstance(intoDataKeys, (tuple, list, collections.Iterable))

		sSel = "SELECT "
		bComma = False
		for key in fromDataKeys:
			if bComma:
				sSel += ","
			else:
				bComma = True
			sSel += key
		sSel += " FROM " + fromTableDef.name

		sInsert = "INSERT INTO " + intoTableDef.name + " ("
		bComma = False
		for key in intoDataKeys:
			assert isinstance(key, str)
			if bComma:
				sInsert += ","
			else:
				bComma = True
			sInsert += key
		s = sInsert + ") " + sSel
		if self.__bDebuggingEnabled:
			print(s)
		return s
	#



	def sqlStmt_selectDistinctValuesFromTable(self, tableDef, columnDefs, filter):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert isinstance(columnDefs, list)
		assert isinstance(filter, (type(None), dict))

		s = "SELECT DISTINCT "
		bNeedComma = False
		for colDef in columnDefs:
			assert isinstance(colDef, DBColDef)
			if bNeedComma:
				s += ","
			else:
				bNeedComma = True
			s += colDef.name
		s += " FROM " + tableDef.name

		ret = []
		if filter != None:
			assert isinstance(filter, dict)
			s += " WHERE "
			bAddSep = False
			for key in filter:
				assert isinstance(key, str)
				if bAddSep:
					s += " AND "
				else:
					bAddSep = True
				value = filter[key]
				if value is None:
					s += "(" + key + " IS NULL)"
				else:
					s += "(" + key + " = ?)"
					ret.append(value)
		if self.__bDebuggingEnabled:
			print(s)
		return s, ret
	#



	def sqlStmt_selectMultipleRowsFromTable(self, tableDef, filter):
		s = self.__selectRowsFromTable(tableDef, filter, False)
		return s
	#



	def sqlStmt_selectSingleRowFromTable(self, tableDef, filter):
		s = self.__selectRowsFromTable(tableDef, filter, True)
		return s
	#



	def __selectRowsFromTable(self, tableDef, filter, bLimitToOne):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]
		assert isinstance(filter, (type(None), dict))

		s = "SELECT * FROM " + tableDef.name
		ret = []

		if filter != None:
			assert isinstance(filter, dict)
			s += " WHERE "
			bAddSep = False
			for key in filter:
				assert isinstance(key, str)
				if bAddSep:
					s += " AND "
				else:
					bAddSep = True
				value = filter[key]
				if value is None:
					s += "(" + key + " IS NULL)"
				else:
					s += "(" + key + " = ?)"
					ret.append(value)
		if bLimitToOne:
			s += " LIMIT 1"
		if self.__bDebuggingEnabled:
			print(s)
		return s, ret
	#



	def sqlStmt_countRowsInTable(self, tableDef, filter):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]

		s = "SELECT COUNT(*) FROM " + tableDef.name
		ret = []

		if filter != None:
			assert isinstance(filter, dict)
			s += " WHERE "
			bAddSep = False
			for key in filter:
				assert isinstance(key, str)
				if bAddSep:
					s += " AND "
				else:
					bAddSep = True
				value = filter[key]
				if value is None:
					s += "(" + key + " IS NULL)"
				else:
					s += "(" + key + " = ?)"
					ret.append(value)
		s += " LIMIT 1"
		if self.__bDebuggingEnabled:
			print(s)
		return s, ret
	#



	def sqlStmt_deleteRowsFromTable(self, tableDef, filter):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]

		s = "DELETE FROM " + tableDef.name + " WHERE "
		assert isinstance(filter, dict)
		assert len(filter) > 0

		bAddSep = False
		ret = []
		for key in filter:
			assert isinstance(key, str)
			if bAddSep:
				s += " AND "
			else:
				bAddSep = True
			value = filter[key]
			if value is None:
				s += "(" + key + " is null)"
			else:
				s += "(" + key + " = ?)"
				ret.append(value)

		if self.__bDebuggingEnabled:
			print(s)

		return s, ret
	#



	def sqlStmt_updateRowInTable(self, tableDef, dataKeys, filter):
		assert tableDef.__class__.__name__ in [ "DBTableDef", "SQLiteTable" ]

		s = "UPDATE " + tableDef.name + " SET "
		bComma = False
		for key in dataKeys:
			assert isinstance(key, str)
			if bComma:
				s += ","
			else:
				bComma = True
			s += key + " = ?"

		ret = []
		if filter != None:
			assert isinstance(filter, dict)
			s += " WHERE "
			bAddSep = False
			for key in filter:
				assert isinstance(key, str)
				if bAddSep:
					s += " AND "
				else:
					bAddSep = True
				value = filter[key]
				if value is None:
					s += "(" + key + " is null)"
				else:
					s += "(" + key + " = ?)"
					ret.append(value)
		if self.__bDebuggingEnabled:
			print(s)
		return s, ret
	#



#











