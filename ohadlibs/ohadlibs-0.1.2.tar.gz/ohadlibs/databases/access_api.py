#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Requires both Python and Access in 32 bit versions. Written in Python 2.7.10

CONVENTIONS:
Field attributes: start with f_ that does not exist in the db. Wrapper functions omit them automatically.

"""

import os
import pyodbc


class Entry:

    def __init__(self):
        pass

    def setattr(self, key, value):
        setattr(self, "f_{}".format(key), value)

    def getattr(self, item):
        return getattr(self, "f_{}".format(item))

    def __str__(self):
        return str(self.__dict__)


class AccessDBAPI:

    def __init__(self, path):
        self.path = path
        database_file = os.getcwd() + "\\" + self.path
        connection_string = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s" % database_file
        self.db_connection = pyodbc.connect(connection_string)

    def query(self, query):
        print query
        cursor = self.db_connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        headers = [field_tuple[0] for field_tuple in rows[0].cursor_description]
        row_dicts_list = [dict(zip(headers, row)) for row in rows]
        entry_objects_list = []
        for row_dict in row_dicts_list:
            _entry = Entry()
            for key in row_dict:
                _entry.setattr(key, row_dict[key])
            entry_objects_list.append(_entry)
        return entry_objects_list

    def insert(self, table, *args, **kwargs):
        cursor = self.db_connection.cursor()
        if len(kwargs) > 0:
            arguments = kwargs.items()
        else:
            arguments = args[0].items()
        columns_str = ", ".join([x[0] for x in arguments])
        values_str = ", ".join(["'{}'".format(x[1]) if type(x[1]) is str else "{}".format(int(x[1])) for x in arguments])
        query = 'INSERT INTO {table} ({columns}) VALUES ({values})'.format(table=table, columns=columns_str, values=values_str)
        cursor.execute(query)
        self.db_connection.commit()
        # self.db_connection.close()
        return

    def select(self, table, *args, **kwargs):
        """

        :param table: Table name, String
        :param args: May supply with a dict of arguments for the WHERE part
        :param kwargs: Alternate way is to use kwargs for the arguments
        :return: List of the query results
        """
        try:
            try:
                parsed_args = self.arg_dict_to_query_syntax(args[0])
            except IndexError:
                parsed_args = self.arg_dict_to_query_syntax(kwargs)
            q = 'SELECT * FROM {table} WHERE {args}'.format(table=table, args=parsed_args)
        except IndexError:
            q = 'SELECT * FROM {table}'.format(table=table)
        return self.query(q)

    def select_left_join(self, *args):
        """
        :param args: For each join, should pass a tuple of two tables,
        where each argument is a tuple whose first arg is the <table name> and the second is the <key column>
        :return: Entities list
        """

        query_beginning = "SELECT DISTINCT * FROM {parentheses}{table_a}".format(parentheses=(len(args) - 1) * "(", table_a=args[0][0][0])
        left_join_template = " LEFT JOIN {table_b} ON ({table_a}.{table_a_key_col} = {table_b}.{table_b_key_col}{parenthesis}"

        left_joins_part = ""
        for idx, join in enumerate(args):
            curr_table_a = join[0][0]
            curr_table_a_key_col = join[0][1]
            curr_table_b = join[1][0]
            curr_table_b_key_col = join[1][1]
            left_join_table_part = left_join_template.format(table_a=curr_table_a, table_a_key_col=curr_table_a_key_col,
                                                             table_b=curr_table_b, table_b_key_col=curr_table_b_key_col, parenthesis=(len(args) - idx) * ")")
            left_joins_part += left_join_table_part
        q = query_beginning + left_joins_part
        return self.query(q)

    def get_table_headers(self, table):
        return [x.replace("f_", "") for x in dir(self.query("SELECT TOP 1 * FROM {table}".format(table=table))[0]) if x.startswith("f_")]

    def list_tables(self):
        cursor = self.db_connection.cursor()
        return [x[2] for x in cursor.tables().fetchall() if x[3] == 'TABLE']

    def list_table_columns(self, table):
        try:
            return [x.strip("f_") for x in dir(self.select(table)[0]) if x.startswith("f_")]
        except (IndexError, pyodbc.ProgrammingError):
            return []

    @staticmethod
    def arg_dict_to_query_syntax(arg_dict):
        return "{}='{}'".format(arg_dict.items()[0][0], arg_dict.items()[0][1])

    @staticmethod
    def log_query(query_result):
        for entry in query_result:
            print entry

    @staticmethod
    def get_entry_field_names(entry_object):
        return [attr for attr in dir(entry_object) if attr.startswith("t_")]
