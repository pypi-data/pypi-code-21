# encoding: utf-8

import codecs
import datetime
import os
import shutil
import sqlite3
from collections import OrderedDict

import logging_helper
from tableutil.table import Table
from tableutil.text_table import text_table_to_list

logging = logging_helper.setup_logging()

# Where constants
COLUMN = u'column'
VALUE = u'value'
OPERATOR = u'operator'
CONDITION = u'condition'

# Foreign key constants
TABLE_COLUMN = u'column'
FOREIGN_TABLE = u'foreign_table'
FOREIGN_COLUMN = u'foreign_column'


class DatabaseHandler(object):

    def __init__(self,
                 db_path=u':memory:',
                 record_changes=False):

        self.database_connection = None
        self.database_cursor = None
        self.auto_save = False
        self.last_select_table = None
        self.db_version = None
        self.default_tables = [u'db_change_log',
                               u'table_descriptions',
                               u'general_config']

        self.db_path = db_path
        self.record_changes = record_changes

        if not self.initialised:
            self.initialise_db()

    @property
    def db_open(self):
        return self.database_connection is not None and self.database_cursor is not None

    @property
    def initialised(self):
        return os.path.exists(self.db_path)

    def initialise_db(self):

        logging.info(u'Initialising database: {db}'.format(db=self.db_path))

        self.open()

        # Create the change record table
        change_table_name = u'db_change_log'

        columns = OrderedDict()
        columns[u'id'] = u'INTEGER PRIMARY KEY'
        columns[u'db_root_name'] = u'TEXT'
        columns[u'db_version'] = u'INTEGER'
        columns[u'sql_command'] = u'TEXT'
        columns[u'sql_params'] = u'TEXT'

        self.create_table(table=change_table_name,
                          columns=columns)

        # Create the descriptions table
        description_table_name = u'table_descriptions'

        columns = OrderedDict()
        columns[u'table_name'] = u'TEXT'
        columns[u'description_row'] = u'INTEGER'
        columns[u'description'] = u'TEXT'

        self.create_table(table=description_table_name,
                          columns=columns)

        # Create the general config table
        general_table_name = u'general_config'

        columns = OrderedDict()
        columns[u'parameter'] = u'TEXT'
        columns[u'value'] = u'TEXT'

        self.create_table(table=general_table_name,
                          columns=columns)

        # Add description for change record table
        table_description = [u'If change_log enabled for this database all modifications are logged here!',
                             u'NOTE: This file is for information only and will not be imported!']

        self.insert_table_description(table=change_table_name,
                                      description=table_description)

        # Add description for descriptions table
        table_description = [u'Contains descriptions for all tables.',
                             u'NOTE: This file is for information only and will not be imported, ',
                             u'      Please change descriptions in the table config files themselves!']

        self.insert_table_description(table=description_table_name,
                                      description=table_description)

        # Add description for general config table

        table_description = [u'A place to store any General configuration parameters that do not fit elsewhere!',
                             u'NOTE: This file is for information only and will not be imported, ',
                             u'      Any changes should be performed in your code!']

        self.insert_table_description(table=general_table_name,
                                      description=table_description)

        # Add db creation date to general_config table
        self.insert(table=u'general_config',
                    columns=[u'parameter', u'value'],
                    values=[u'db_creation_date',
                            datetime.datetime.now()
                            .strftime(u'%Y-%m-%d %H:%M:%S')])

        self.save()
        self.close()

        logging.info(u'Database initialised!')

    def reinitialise_db(self, backup=False):

        """ Reinitialise the Database

        Args:
            backup: Set to True if you want to keep last version
        """

        logging.info(u'Re-initialising database: {db}'.format(db=self.db_path))

        # Deal with existing db before recreating.
        if os.path.exists(self.db_path):

            if backup:
                old_path = u'{p}.old'.format(p=self.db_path)
                logging.info(u'Moving existing DB to {old_path}'.format(old_path=old_path))
                self.close()
                shutil.move(self.db_path, old_path)

            else:
                logging.info(u'Removing existing DB')
                self.close()
                os.remove(self.db_path)

        self.initialise_db()

    def open(self):

        if self.database_connection is None:

            try:
                # Ensure path exists if not saving to memory
                if not self.db_path == u':memory:':
                    path = u'/'.join(self.db_path.split(os.sep)[:-1])
                    logging_helper.ensure_path_exists(path)

                self.database_connection = sqlite3.connect(self.db_path)
                self.set_cursor()

            except Exception:
                logging.error(u'Cannot open database {path}.'.format(path=self.db_path))
                raise

        if self.db_open:
            self.db_version = self.get_db_version()
            self.database_cursor.execute(u'pragma foreign_keys = ON')

    def close(self):

        try:
            self.database_cursor.close()
            self.database_connection.close()

        except Exception as err:
            logging.debug(err)

        finally:
            self.database_connection = None
            self.database_cursor = None
            self.db_version = None

    def set_cursor(self):
        logging.debug(u'Setting Cursor')
        self.database_cursor = self.database_connection.cursor()

    def get_cursor(self):
        return self.database_cursor

    def record_change(self,
                      statement,
                      params):

        command = None

        logging.debug(u'recording statement')

        if statement.split(u' ')[2] not in self.default_tables:
            command = (u'INSERT INTO db_change_log '
                       u'(db_root_name, db_version, sql_command, sql_params) '
                       u'VALUES ("{n}", "{v}", "{s}", ?)'
                       .format(n=self.db_path.split(os.sep)[-1],
                               v=self.db_version + 1,
                               s=statement))

        if command:
            logging.debug(command)

            try:
                self.database_cursor.execute(command, (unicode(params),))

            except Exception as e:
                logging.exception(u'Failed to execute statement, '
                                  u'change not logged:\n'
                                  u'"{statement}"\nparams:"{params}"'
                                  .format(statement=command,
                                          params=params))

                raise e

    def execute(self,
                statement,
                params=()):

        """

        :param statement:   SQL statement to be executed
        :param params:      Tuple of variables corresponding
                            to ?'s in the SQL statement.
                            This allows for correct escaping
                             of characters in variables.
        :return:
        """

        if self.database_cursor:

            try:
                self.database_cursor.execute(statement, params)

                if self.auto_save:
                    self.save()

            except Exception as err:
                logging.warning(u'Failed to execute statement: '
                                u'"{statement}", params:"{params}"'.format(statement=statement,
                                                                           params=params))
                logging.warning(err)

                if all(x in str(err) for x in [u'table', u'already exists']):
                    pass

                else:
                    raise err

            else:
                if self.record_changes:
                    if statement.split(u' ')[0] in (u'UPDATE',
                                                    u'INSERT',
                                                    u'DELETE',
                                                    u'CREATE',
                                                    u'DROP',
                                                    u'ALTER'):
                        self.record_change(statement=statement,
                                           params=params)

        else:
            raise Exception(u'Cannot execute statement, Cursor not set!')

    def get_db_version(self):

        self.execute(statement=u'pragma user_version;')
        version = self.fetchone()[0]

        logging.debug(u'DB Version: {v}'.format(v=version))

        return version

    def set_db_version(self, version):
        self.execute(statement=u'pragma user_version = {v};'.format(v=version))
        self.db_version = version
        logging.info(u'DB Version Updated to: {v}'.format(v=version))

    def increment_db_version(self):
        version = self.get_db_version()
        version += 1
        self.set_db_version(version=version)

    def save(self):
        logging.debug(u'Committing changes to db: {db}'.format(db=self.db_path))

        try:
            self.database_connection.commit()

        except Exception:
            raise

    def save_and_close(self):
        self.save()
        self.close()

    def fetchone(self):
        return self.database_cursor.fetchone()

    def fetchone_formatted(self):

        result = None
        row = self.fetchone()
        headings = self.get_table_headings()

        # reformat result
        if row:
            result = OrderedDict()

            for i, heading in enumerate(headings):
                result[heading] = row[i]

        return result

    def fetchall(self):
        return self.database_cursor.fetchall()

    def fetchall_formatted(self):
        all = []
        one = self.fetchone_formatted()

        while one:
            all.append(one)
            one = self.fetchone_formatted()

        return all

    def get_table_row_count(self,
                            table,
                            where=None):

        # setup where clause
        if where:
            where_conditions, where_values = self.handle_where(where=where)

        else:
            where_conditions = u''
            where_values = ()

        try:
            self.execute(statement=u'SELECT COUNT(*) FROM {table} {where}'.format(table=table,
                                                                                  where=where_conditions),
                         params=where_values)

            count = self.fetchone()[0]

        except Exception as err:
            logging.warning(err)
            count = 0

        return count

    @staticmethod
    def handle_where(where):

        where_conditions = u'WHERE '
        where_values = []
        # TODO: handle scenario where there are no valid conditions

        if isinstance(where, dict):
            where = [where]

        # Validate where conditions
        for i, col_cond in enumerate(where):

            try:
                assert COLUMN in col_cond
                assert VALUE in col_cond
                assert OPERATOR in col_cond
                assert col_cond[OPERATOR] in (u'=',
                                              u'<>',
                                              u'>',
                                              u'<',
                                              u'<=',
                                              u'>=',
                                              u'LIKE',
                                              u'BETWEEN',
                                              u'IN')

                if i == 0:
                    assert CONDITION not in col_cond

                else:
                    assert CONDITION in col_cond
                    assert col_cond[CONDITION] in (u'AND', u'OR', u'NOT')

                col_cond[u'valid'] = True

            except AssertionError:
                col_cond[u'valid'] = False

        # Add valid conditions to where clause
        for i, col_cond in enumerate(where):

            if col_cond[u'valid']:

                if not i == 0:
                    where_conditions += u'{cond} '.format(cond=col_cond[CONDITION])

                # Correct for NULL values!
                if col_cond[VALUE] is not None:
                    op = col_cond[OPERATOR]
                    val = u'?'
                    where_values.append(col_cond[VALUE])

                else:
                    op = u'is'
                    val = u'null'

                where_conditions += u'{col} {op} {val} '.format(col=col_cond[COLUMN],
                                                                op=op,
                                                                val=val)

        where_values = tuple(where_values)

        logging.debug(where_conditions)
        logging.debug(where_values)

        return where_conditions, where_values

    @staticmethod
    def handle_primary_key(primary_key):
        # TODO: Write unittests for this method!

        if primary_key is None:
            return u''

        return u', PRIMARY KEY ({key_columns}) '.format(key_columns=u', '.join(primary_key))

    @staticmethod
    def handle_foreign_keys(foreign_keys):
        # TODO: Write unittests for this method!

        if foreign_keys is None:
            return u''

        keys = []

        for foreign_key in foreign_keys:
            keys.append(u'FOREIGN KEY ({table_column}) '
                        u'REFERENCES {foreign_table} '
                        u'({foreign_column})'.format(table_column=foreign_key.get(TABLE_COLUMN),
                                                     foreign_table=foreign_key.get(FOREIGN_TABLE),
                                                     foreign_column=foreign_key.get(FOREIGN_COLUMN)))

        return u', {foreign_keys}'.format(foreign_keys=u', '.join(keys))

    def create_table(self,
                     table,
                     columns,
                     primary_key=None,
                     foreign_keys=None):
        """

        @param table:           Table to select from.
        @param columns:         Columns to add. Dictionary of column: type pairs
                                    {col1: type1,
                                    col2: type2,}
        @param primary_key:     List of column names that will make up the primary key.
        @param foreign_keys:    Foreign key constraints for a table.  List of foreign keys:
                                    [{column: col_name,
                                      foreign_table: table_name,
                                      foreign_column: col_name},
                                     {column: col_name2,
                                      foreign_table: table_name2,
                                      foreign_column: col_name2}]
        """

        # TODO: Update unittests for this method to include testing foreign keys!

        # setup values
        table_columns = u''

        for col in columns:
            table_columns += (u'{col} {type}, '.format(col=col,
                                                       type=columns[col]))

        table_columns = table_columns[:-2]

        # Construct select
        create_statement = (u'CREATE TABLE {table} ({values}'
                            u'{primary_key}'
                            u'{foreign_keys})'.format(table=table,
                                                      values=table_columns,
                                                      primary_key=self.handle_primary_key(primary_key),
                                                      foreign_keys=self.handle_foreign_keys(foreign_keys)))

        logging.debug(create_statement)

        # Run select
        self.execute(statement=create_statement)

    def drop_table(self,
                   table):
        """

        @param table:   Table to drop.
        """

        # Construct select
        drop_statement = u'DROP TABLE {table}'.format(table=table)

        logging.debug(drop_statement)

        # Run statement
        try:
            self.execute(statement=drop_statement)

        except sqlite3.OperationalError as err:
            logging.warning(u'Cannot drop table; {e}'.format(e=err))

    def select(self,
               table,
               select_columns=None,
               where=None,
               order_by=None,
               ):

        """

        @param table:           Table to select from.
        @param select_columns:  Columns to select. Defaults to all columns (*)
                                    [col1, col2,]
        @param where:           Conditions of select. List of dictionaries.
                                    [{column: col1,
                                      value: x,
                                      operator: y
                                     },
                                     {column: col2,
                                      value: x,
                                      operator: y,
                                      condition: z
                                     },
                                    ]
                                    y can be one of: = <> > < <= >=
                                                     LIKE BETWEEN IN
                                    z can be one of: AND OR NOT
        @param order_by:        List of columns to order by.
                                    [col1, col2,]
        """

        # setup columns to select
        if isinstance(select_columns, (str, unicode)):
            columns = select_columns if select_columns else u'*'

        else:
            columns = u', '.join(select_columns) if select_columns else u'*'

        # setup where clause
        if where:
            where_conditions, where_values = self.handle_where(where=where)

        else:
            where_conditions = u''
            where_values = ()

        # setup order by clause
        if order_by:
            order_by_columns = u'ORDER BY '
            if isinstance(order_by, (str, unicode)):
                order_by_columns += order_by
            else:
                order_by_columns += u', '.join(order_by)
        else:
            order_by_columns = u''

        # Construct select
        select_statement = (u'SELECT {col} FROM {table} {where}{order}'.format(col=columns,
                                                                               table=table,
                                                                               where=where_conditions,
                                                                               order=order_by_columns))

        logging.debug(select_statement)

        # Run select
        self.execute(statement=select_statement,
                     params=where_values)
        self.last_select_table = table

    def get_formatted_row(self,
                          table,
                          where,
                          select_columns=None,
                          order_by=None, ):

        # Execute select
        self.select(table=table,
                    select_columns=select_columns,
                    where=where,
                    order_by=order_by)

        # Get result
        row = self.fetchone()
        headings = self.get_table_headings()

        # reformat result
        result = OrderedDict()

        if row:
            for i, heading in enumerate(headings):
                result[heading] = row[i]

        return result

    def get_formatted_rows(self,
                           table,
                           where,
                           select_columns=None,
                           order_by=None, ):

        # Execute select
        self.select(table=table,
                    select_columns=select_columns,
                    where=where,
                    order_by=order_by)

        # Get result
        unformatted_rows = self.fetchall()
        headings = self.get_table_headings()

        result = []

        for unformatted_row in unformatted_rows:
            # reformat result
            row = OrderedDict()

            for i, heading in enumerate(headings):
                row[heading] = unformatted_row[i]
            result.append(row)

        return result

    def insert(self,
               table,
               columns,
               values):

        """

        @param table:   Table to select from.
        @param columns: Columns to insert. Defaults to all columns (*)
                            [col1, col2,]
        @param values:  Values to insert.
                            [val1, val2,]
        """

        if table and columns and values:

            if not self.check_if_row_blank(values):

                # setup columns
                insert_columns = u', '.join(columns)

                # setup insert_values as list of question marks
                # for each item in values
                # values is then passed passed to execution
                # converted to a tuple so that the execute
                # function escapes the characters correctly for us!
                insert_values = u','.join((u'?' for _ in values))

                insert_statement = u'INSERT INTO {table} ({columns}) VALUES ({values})'.format(table=table,
                                                                                               columns=insert_columns,
                                                                                               values=insert_values)

                logging.debug(values)
                logging.debug(insert_statement)

                self.execute(statement=insert_statement,
                             params=tuple(values))

            else:
                logging.debug(u'Not adding as row is blank!')

    def update(self,
               table,
               values,
               where):

        """
        @param table:   Table to select from.
        @param values:  New values. Dictionary of column: value pairs
                            {col1: val1,
                             col2: val2,}
        @param where:   Conditions of select. List of dictionaries.
                            [{column: col1,
                              value: x,
                              operator: y
                             },
                             {column: col2,
                              value: x,
                              operator: y,
                              condition: z
                             },
                            ]
                            y can be one of: = <> > < <= >= LIKE BETWEEN IN
                            z can be one of: AND OR NOT
        """

        # setup values
        update_value_keys = u', '.join([u'{col} = ?'.format(col=col)
                                        for col in values.keys()])

        # setup where clause
        if where:
            where_conditions, where_values = self.handle_where(where=where)

        else:
            where_conditions = u''
            where_values = ()

        params = values.values()
        params.extend(where_values)

        # Construct select
        update_statement = u'UPDATE {table} SET {values} {where}'.format(table=table,
                                                                         values=update_value_keys,
                                                                         where=where_conditions,
                                                                         params=params)

        logging.debug(u'{update_statement}; # params = {params}'.format(update_statement=update_statement,
                                                                        params=params))

        # Run select
        self.execute(statement=update_statement,
                     params=params)

    def update_record(self,
                      table,
                      values,
                      where):

        logging.debug(u'Update Record')

        # parse params
        columns = []
        insert_values = []

        for col in values:
            columns.append(col)
            insert_values.append(values[col])

        # Check for row in table
        self.select(table=table,
                    where=where)
        existing_rows = self.fetchall()

        if len(existing_rows) >= 1:
            # If exists run update
            self.update(table=table,
                        values=values,
                        where=where)

        else:
            # If does not exist run insert
            self.insert(table, columns, insert_values)

    def delete(self,
               table,
               where):

        """

        @param table:   Table to select from.
        @param where:   Conditions of select. List of dictionaries.
                            [{column: col1,
                              value: x,
                              operator: y
                             },
                             {column: col2,
                              value: x,
                              operator: y,
                              condition: z
                             },
                            ]
                            y can be one of: = <> > < <= >= LIKE BETWEEN IN
                            z can be one of: AND OR NOT
        """

        # setup where clause
        if where:
            where_conditions, where_values = self.handle_where(where=where)

        else:
            where_conditions = u''
            where_values = ()

        # Construct select
        delete_statement = u'DELETE FROM {table} {where}'.format(table=table,
                                                                 where=where_conditions)

        logging.debug(delete_statement)

        # Run select
        self.execute(statement=delete_statement,
                     params=where_values)

    def add_column(self,
                   table,
                   column):

        """
        Add a column to an existing table

        Args:
            table:  Table name
            column: Tuple (Column, Column type)
        """

        # Construct
        alter_statement = (u'ALTER TABLE {table} ADD COLUMN {column} {type}'.format(table=table,
                                                                                    column=column[0],
                                                                                    type=column[1]))

        logging.debug(alter_statement)

        # Run
        self.execute(statement=alter_statement)

    def get_tables(self):
        # Get tables
        self.select(table=u'sqlite_master',
                    select_columns=[u'tbl_name'],
                    where=[{COLUMN: u'type',
                            VALUE: u'table',
                            OPERATOR: u'='}])

        tables = self.fetchall()

        default_config_tables = {}
        for table in tables:
            self.select(table=table[0])
            default_config_tables[table[0]] = self.get_table_headings()

        logging.debug(u'Existing tables: {tables}'.format(tables=default_config_tables))

        return default_config_tables

    def get_table_headings(self):
        # Get the column headings
        headings = self.database_cursor.description

        column_headings = []
        for heading in headings:
            column_headings.append(heading[0])

        return column_headings

    def get_table_data(self,
                       table_name):

        table_data = []

        self.select(table=table_name)
        table_headings = self.get_table_headings()

        rows = self.fetchall()

        if rows:
            for row in rows:
                table_row = OrderedDict()

                for i, table_heading in enumerate(table_headings):
                    table_row[table_heading] = row[i]

                table_data += [table_row]

        else:
            # Init empty table
            table_row = OrderedDict()

            for table_heading in table_headings:
                table_row[table_heading] = u''

            table_data += [table_row]

        logging.debug(u'Existing Table Data: {t}'.format(t=table_data))

        return table_data

    def get_table_data_dictionary(self,
                                  table_name):

        table_data = self.get_table_data(table_name=table_name)

        table_headings = list(table_data[0])
        logging.debug(table_headings)

        table_rows = []
        for row in table_data:

            r = list(row.values())
            logging.debug(r)

            table_rows.append(r)

        logging.debug(table_rows)

        table_data_dictionary = {u'table_name': table_name,
                                 u'headings': table_headings,
                                 u'rows': table_rows}

        logging.debug(u'Existing Table Data Dictionary: {t}'.format(t=table_data_dictionary))

        return table_data_dictionary

    def load_config(self,
                    path):

        """ Load text config tables to database

        Note: This will wipe out any existing config!

        @param path: Path to folder containing text files
        """

        # Re-initialise database before loading.
        self.reinitialise_db()
        self.load_config_updates(path=path)

    def load_config_updates(self,
                            path):

        """ Load updates to text config tables into database

        @param path: Path to folder containing text files
        """

        # TODO: split into subroutines. (10 levels of indentation)"""
        changes = False

        def convert_rows(r):
            # Generate New Row
            v = []
            for h in text_file_table_headings:
                v += [r[h] if r[h] else None]

            return v

        self.open()

        if os.path.exists(path):

            config_files = os.listdir(path)
            logging.debug(u'Config Files: {cfg}'.format(cfg=config_files))

            if not len(config_files) == 0:

                current_db_tables = self.get_tables()  # DEBUG logs "Existing Tables: ..."

                db_tables = list(current_db_tables)

                for table in self.default_tables:
                    try:
                        db_tables.remove(table)

                    except ValueError:
                        pass

                logging.debug(u'DB Tables: {cfg}'.format(cfg=db_tables))

                text_file_tables = [config_file.replace(u'.txt', u'')
                                    for config_file in config_files]

                logging.debug(u'Text File Tables: {cfg}'.format(cfg=text_file_tables))

                # Check for any tables that have been removed
                table_db_only = list(set(db_tables) - set(text_file_tables))
                logging.debug(u'Tables in db not text file: {t}'.format(t=table_db_only))

                logging.debug(u'Default_tables: {t}'.format(t=self.default_tables))

                for table in self.default_tables:
                    try:
                        table_db_only.remove(table)

                    except ValueError:
                        pass

                # Drop any removed tables
                if table_db_only:
                    changes = True
                    for table in table_db_only:
                        self.drop_table(table=table)

                # Check for changes to individual tables
                for i, table_name in enumerate(text_file_tables):
                    if table_name not in self.default_tables:
                        config_filepath = u'{path}{sep}{file}.txt'.format(path=path,
                                                                          sep=os.sep,
                                                                          file=table_name)

                        text_file_table_data = text_table_to_list(config_filepath)
                        text_file_table_description = text_file_table_data[u'Description']
                        text_file_table_headings = text_file_table_data[u'Headings']
                        text_file_table_rows = map(convert_rows, text_file_table_data[u'Data'])

                        table_columns = OrderedDict()

                        # Create the table if necessary
                        current_db_table_headings = current_db_tables.get(table_name)

                        if table_name not in current_db_tables:
                            for col in text_file_table_headings:
                                table_columns[col] = u'TEXT'

                            changes = True
                            self.create_table(table=table_name, columns=table_columns)

                        # Insert / Update description for this table
                        if self.update_table_description(table=table_name,
                                                         description=text_file_table_description):
                            changes = True

                        # Check whether columns match, if not correct them.
                        elif not set(current_db_table_headings) == set(text_file_table_headings):
                            logging.debug(u'Columns do not match, updating...')

                            col_db_only = list(set(current_db_table_headings) - set(text_file_table_headings))
                            col_text_file_only = list(set(text_file_table_headings) - set(current_db_table_headings))

                            logging.debug(u'Columns in db not text file: {t}'.format(t=col_db_only))
                            logging.debug(u'Columns in text file not db: {t}'.format(t=col_text_file_only))

                            # Need to remove a column therefore have to drop & recreate table!
                            if col_db_only:

                                logging.debug(u'Column(s) have been removed, dropping and re-creating db table!')
                                changes = True

                                self.drop_table(table=table_name)

                                for col in text_file_table_headings:
                                    table_columns[col] = u'TEXT'

                                self.create_table(table=table_name, columns=table_columns)

                            # Need to add a column
                            elif col_text_file_only:

                                logging.debug(u'Column(s) have been added, adding new columns to db table!')
                                changes = True

                                for column in col_text_file_only:
                                    self.add_column(table=table_name,
                                                    column=(column, u'TEXT'))

                        # Get the existing DB rows
                        db_table_data = self.get_table_data_dictionary(table_name=table_name)

                        db_table_rows = map(tuple, db_table_data.get(u'rows'))
                        text_file_table_rows = map(tuple, text_file_table_rows)

                        logging.debug(u'DB Rows: {t}'.format(t=db_table_rows))
                        logging.debug(u'Text File Rows: {t}'.format(t=text_file_table_rows))

                        # Determine rows that have changed
                        row_db_only = list(set(db_table_rows) - set(text_file_table_rows))
                        row_text_file_only = list(set(text_file_table_rows) - set(db_table_rows))

                        # Clean blank rows from row_db_only so that un-necessary deletes are not performed
                        # i.e if table is blank then an empty row is returned even if it does not exist.
                        for row in row_db_only:
                            if self.check_if_row_blank(row=row):
                                row_db_only.remove(row)

                        logging.debug(u'Rows in db not text file: {t}'.format(t=row_db_only))
                        logging.debug(u'Rows in text file not db: {t}'.format(t=row_text_file_only))

                        # Remove rows that are no longer in text files
                        if row_db_only:

                            changes = True

                            for row in row_db_only:

                                # Generate where clause
                                row = list(row)
                                logging.debug(u'Row X: {t}'.format(t=row))

                                where_clause = []

                                for heading in text_file_table_headings:
                                    if not where_clause:
                                        where_clause += [{COLUMN: heading,
                                                          VALUE: row[text_file_table_headings.index(heading)],
                                                          OPERATOR: u'='}]

                                    else:
                                        where_clause += [{COLUMN: heading,
                                                          VALUE: row[text_file_table_headings.index(heading)],
                                                          OPERATOR: u'=',
                                                          CONDITION: u'AND'}]

                                logging.debug(u'WHERE: {t}'.format(t=where_clause))

                                self.delete(table=table_name,
                                            where=where_clause)

                        # Add new/updated rows to DB
                        if row_text_file_only:

                            changes = True

                            for row in row_text_file_only:

                                row = list(row)
                                logging.debug(u'Row +: {t}'.format(t=row))

                                self.insert(table=table_name,
                                            columns=text_file_table_headings,
                                            values=row)

                        self.save()

        else:
            logging.warning(u'No config files to load!')

        # Was anything changed? if so increment DB version!
        if changes:
            self.increment_db_version()
            self.save()

        self.close()

    def dump_config(self,
                    path):
        """
        Dump database tables to text files on disk.
        """

        logging_helper.ensure_path_exists(path)

        tables = self.get_tables()

        for table_name in tables:

            table_description = self.get_table_description(table=table_name)
            table_data = Table.init_from_tree(title=table_name,
                                              tree=self.get_table_data(table_name=table_name),
                                              row_numbers=False,
                                              table_format=Table.TEXT_TABLE_FORMAT)

            description = u''
            for td in table_description:
                description += u'@ {descr_row}\n'.format(descr_row=td[2])

            table = table_data.text(solid_borders=False,
                                       show_title=False)

            filename = u'{path}{sep}{name}.txt'.format(path=path,
                                                       sep=os.sep,
                                                       name=table_name)

            if not table.strip() == u'Empty':
                with codecs.open(filename, u'w', encoding=u'utf8') as f:
                    f.write(table)
                    f.write(description)

    @staticmethod
    def parse_table_description(description):

        description_rows = {}

        for i, d in enumerate(description):
            description_rows[i] = d

        return description_rows

    def insert_table_description(self,
                                 table,
                                 description):

        """
        Insert descriptions into table_descriptions table.

        @param table:       Table to associate description with.
        @param description: Description (text string)
        @return:
        """

        table_description = self.parse_table_description(description)
        logging.debug(u'DESC: {d}'.format(d=table_description))

        for row in table_description:

            self.insert(table=u'table_descriptions',
                        columns=[u'table_name',
                                 u'description_row',
                                 u'description'],
                        values=[table, row, table_description[row]])

    def update_table_description(self,
                                 table,
                                 description):

        """
        Update descriptions in table_descriptions table.

        @param table:       Table to associate description with.
        @param description: Description (text string)
        @return:
        """

        changes = False

        # Get Current DB Description
        table_description_rows = self.get_table_description(table=table)

        logging.debug(u'DB Desc rows: {d}'.format(d=table_description_rows))

        # Format new description rows
        desc = []
        for i, row in enumerate(description):
            desc.append((table, i, row))

        logging.debug(u'New Desc rows: {d}'.format(d=desc))

        # Determine rows that have changed
        row_db_only = list(set(table_description_rows) - set(desc))
        row_new_only = list(set(desc) - set(table_description_rows))

        logging.debug(u'In DB desc not new desc: {t}'.format(t=row_db_only))
        logging.debug(u'In new desc not db desc: {t}'.format(t=row_new_only))

        # Delete any rows from the DB that are not in the new description
        for row in row_db_only:

            changes = True

            delete_where_clause = [{COLUMN: u'table_name',
                                    VALUE: row[0],
                                    OPERATOR: u'='},

                                   {COLUMN: u'description_row',
                                    VALUE: row[1],
                                    OPERATOR: u'=',
                                    CONDITION: u'AND'},

                                   {COLUMN: u'description',
                                    VALUE: row[2],
                                    OPERATOR: u'=',
                                    CONDITION: u'AND'}]

            self.delete(table=u'table_descriptions',
                        where=delete_where_clause)

        # Insert/update description rows
        for row in row_new_only:

            changes = True

            update_values = {u'table_name': row[0],
                             u'description_row': row[1],
                             u'description': row[2]}

            update_where = [{u'column': u'table_name',
                             u'value': row[0],
                             u'operator': u'='},
                            {u'column': u'description_row',
                             u'value': row[1],
                             u'operator': u'=',
                             u'condition': u'AND'}]

            self.update_record(table=u'table_descriptions',
                               values=update_values,
                               where=update_where)

        return changes

    def get_table_description(self,
                              table):
        where_clause = [{u'column': u'table_name',
                         u'value': table,
                         u'operator': u'='}]

        order_clause = [u'description_row']

        self.select(table=u'table_descriptions',
                    where=where_clause,
                    order_by=order_clause)

        table_description_rows = self.fetchall()

        return table_description_rows

    @staticmethod
    def check_if_row_blank(row):

        blank = True

        for item in row:
            if not item == u'':
                blank = False

        return blank


class KeyValueTable(object):
    """
    Class to allow dict style access for a key/value tables
    using a DatabaseHandler
    """
    KEY = u'key'
    VALUE = u'value'

    def __init__(self,
                 db,
                 table,
                 key_col=KEY,
                 value_col=VALUE):
        self.db = db()
        self.table = table
        self.key_col = key_col
        self.value_col = value_col

    def add_item(self,
                 key,
                 value):

        # Initialise the parameter if it doesn't already exist
        try:
            self[key]
        except KeyError:

            # Doesn't exist: Add it to the table
            self.db.open()

            logging.info(u'{key} not configured, configuring...'.format(key=key))

            self.db.insert(table=self.table,
                           columns=[self.key_col,
                                    self.value_col],
                           values=[key,
                                   value])
            self.db.save()

            self.db.close()

            logging.info(u'{key} initialised to: {value}'.format(key=key,
                                                                 value=value))

    def get(self,
            key,
            default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self,
                    key):
        self.db.open()

        row = self.db.get_formatted_row(table=self.table,
                                        where=[{u'column': self.key_col,
                                                u'value': key,
                                                u'operator': u'='}])
        self.db.close()

        try:
            return row[self.value_col]
        except KeyError:
            raise KeyError(key)

    def __setitem__(self,
                    key,
                    value):
        try:
            self[key]
        except KeyError:
            self.add_item(key=key,
                          value=value)
            return
        else:
            self.db.open()

            self.db.update(table=self.table,
                           values={self.value_col: value},
                           where={u'column': self.key_col,
                                  u'value': key,
                                  u'operator': u'='})
            self.db.save()
            self.db.close()

    def __delitem__(self,
                    key):
        self.db.open()

        # delete will raise KeyError if not found
        self.db.delete(table=self.table,
                       where={u'column': self.key_col,
                              u'value': key,
                              u'operator': u'='})
        self.db.save()
        self.db.close()
