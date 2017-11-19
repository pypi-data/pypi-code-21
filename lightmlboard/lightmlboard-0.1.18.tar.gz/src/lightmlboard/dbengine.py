"""
@file
@brief Manages a sqlite3 database.
"""
import numpy
import sqlite3
import datetime
import decimal


class DBException(Exception):
    """
    Exception raised by class @see cl Database.
    """
    pass


class Database:
    """
    Common functions about sqlite3.
    """

    _field_option = ["PRIMARYKEY", "AUTOINCREMENT", "AUTOFILL"]

    def __init__(self, dbfile):
        """
        @param      dbfile      filename or ``:memory:``
        """
        self._sql_file = dbfile
        self._connection = None

    def get_file(self):
        """
        Returns the file name.
        """
        return self._sql_file

    def _check_connection(self):
        """
        Check the SQL connection.
        """
        if self._connection is None:
            message = "Use connect method before doing operation on this database."
            raise Exception(message)

    def _is_memory(self):
        """
        Tells if the database takes place in memory (``:memory:``).
        """
        return self._sql_file == ":memory:"

    def connect(self):
        """
        Opens a connection to the database.
        """
        if self._is_memory():
            if self._connection is None:
                self._connection = sqlite3.connect(self._sql_file)
        elif self._connection is not None:
            raise Exception("A previous connection was not closed.")
        else:
            self._connection = sqlite3.connect(self._sql_file)

    def close(self):
        """
        Close the database.
        """
        self._check_connection()
        if self._is_memory():
            # We should not close, otherwise, we lose the data.
            # self._connection = None
            pass
        else:
            self._connection.close()
            self._connection = None

    def commit(self):
        """
        Call this function after any insert request.
        """
        self._check_connection()
        self._connection.commit()

    def execute(self, request):
        """
        Open a cursor with a query and return it to the user.

        @param      request         SQL request
        @return                     cursor
        """
        # classic ways
        self._check_connection()
        cur = self._connection.cursor()
        try:
            cur.execute(request)
        except Exception as e:
            raise DBException(
                "Unable to execute a SQL request (1) (file '%s')" %
                self.get_file(), e, request) from e
        return cur

    def get_table_list(self):
        """
        Returns the list of tables.

        @return                         the table list
        """
        self._check_connection()
        request = """   SELECT name
                        FROM (SELECT * FROM sqlite_master UNION ALL SELECT * FROM sqlite_temp_master) AS temptbl
                        WHERE type in('table','temp') AND name != 'sqlite_sequence' ORDER BY name;"""

        select = self._connection.execute(request)
        res = []
        for el in select:
            res.append(el[0])
        return res

    def create_table(self, table, columns, temporary=False):
        """
        Creates a table.

        @param      table           table name
        @param      columns         columns definition, dictionary ``{ key:(column_name,python_type) }``
                                    if ``PRIMARYKEY`` is added, the key is considered as the primary key.
                                    Example::

                                        columns = { -1:("key", int, "PRIMARYKEY", "AUTOINCREMENT"),
                                                                0:("name",str), 1:("number", float) }

        @param      temporary       if True the table is temporary
        @return                     cursor
        """
        if table == "sqlite_sequence":
            raise DBException("Unable to create a table named 'sql_sequence'.")

        tables = self.get_table_list()
        if table in tables:
            raise DBException("Tables '{0}' is already present.".format(table))

        if isinstance(columns, list):
            columns = {i: v for i, v in enumerate(columns)}

        if temporary:
            sql = "CREATE TEMPORARY TABLE " + table + "("
        else:
            sql = "CREATE TABLE " + table + "("
        col = []
        for c, val in columns.items():
            if isinstance(val[1], tuple):
                v = val[1][0]
            else:
                v = val[1]

            if v is str:
                col.append(val[0] + " TEXT")
            elif v is int:
                col.append(val[0] + " INTEGER")
            elif v is float:
                col.append(val[0] + " FLOAT")
            elif v is numpy.int64:
                col.append(val[0] + " INTEGER")
            elif v is numpy.float64:
                col.append(val[0] + " FLOAT")
            elif v is decimal.Decimal:
                col.append(val[0] + " Decimal")
            elif v is datetime.datetime:
                col.append(val[0] + " DATETIME")
            else:
                raise DBException(
                    "Unable to add column '{0}' ... {1} v={2}".format(c, val, v))

            if "PRIMARYKEY" in val:
                if val[1] != int:
                    raise DBException(
                        "unable to create a primary key on something differont from an integer (%s)" %
                        str(val))
                col[-1] += " PRIMARY KEY"
                if "AUTOINCREMENT" in val:
                    if self.isMSSQL():
                        col[-1] += " IDENTITY(0,1)"
                    else:
                        col[-1] += " AUTOINCREMENT"

        sql += ",\n       ".join(col)
        sql += ");"
        return self.execute(sql)

    def has_rows(self, table):
        """
        Tells if a table has rows.

        @param      table       table name
        @return                 boolean
        """
        res = list(self.execute("SELECT * FROM {0} LIMIT 1".format(table)))
        return len(res) > 0
