#!/usr/bin/env python
"""
Module SQLITE -- SQLite 3 Database Interface
Sub-Package DBTOOLS of Package PLIB
Copyright (C) 2008-2015 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module implements the SQLite 3 interface built with
PLIB.DBTOOLS.
"""

import sqlite3

from plib.dbtools import DBInterface


DB_FIELDTYPES = {
    'varchar': 'TEXT',
    'text': 'TEXT',
    'tinyint': 'INT',
    'smallint': 'INT',
    'int': 'INT',
    'bool': 'INT',
    'decimal': 'REAL',
}


class SQLite3DBInterface(DBInterface):
    
    conn_methods = DBInterface.conn_methods + ('close',)
    
    db_mod = sqlite3
    
    def _get_connection(self, *args, **kwargs):
        return sqlite3.connect(*args)
    
    def _get_fieldspec(self, field):
        fieldname, fieldtype = field.split(' ')[:2]
        if '(' in fieldtype:
            # Remove the length spec for varchars to simplify lookup
            fieldtype, _ = fieldtype.split('(', 1)
        return "{0} {1}".format(fieldname, DB_FIELDTYPES[fieldtype])
    
    tables_sql = "SELECT * FROM sqlite_master WHERE type='table';"
    tables_index = 1
    
    fields_sql = tables_sql
    fields_iter = False
    
    index_sql = tables_sql
    
    def _get_tablename(self, row):
        return row[1]
    
    def _get_fieldvalues(self, row):
        # TODO: add field types and canonicalize
        return [f.split()[0] for f in row[-1].split('(')[1].split(')')[0].split(', ')]  # type is f.split(1) in DATATYPE format
