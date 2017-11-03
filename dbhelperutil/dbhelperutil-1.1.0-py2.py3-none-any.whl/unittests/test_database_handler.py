import os
import shutil
import sqlite3
import unittest
from collections import OrderedDict

from dbhelperutil import database_handler


class TestDatabaseHandler(unittest.TestCase):

    def check_record_status(self):
        """ Override this to return True/False for record status """

    def setUp(self):

        self.file_dir = u'.{s}test_data{s}database_handler{s}'.format(s=os.sep)
        self.db_name = u'test.db'
        self.db_path = u'{p}{n}'.format(p=self.file_dir, n=self.db_name)
        self.db_path_old = u'{p}{n}.old'.format(p=self.file_dir, n=self.db_name)

        self.db = database_handler.DatabaseHandler(self.db_path, record_changes=self.check_record_status())
        self.db.open()

        self.dummy_table = u'testing'
        self.dummy_headings = [u'date', u'trans', u'symbol', u'qty', u'price']

        self.dummy_columns = OrderedDict()
        self.dummy_columns[u'date'] = u'text'
        self.dummy_columns[u'trans'] = u'text'
        self.dummy_columns[u'symbol'] = u'text'
        self.dummy_columns[u'qty'] = u'real'
        self.dummy_columns[u'price'] = u'real'

        self.dummy_data = [[u'2006-01-05', u'BUY', u'C', 100, 35.14],
                           [u'2006-01-06', u'SELL', u'B', 100, 35.14],
                           [u'2006-01-07', u'BUY', u'A', 100, 35.14]]
        self.dummy_data_extra = [u'2006-01-07', u'SELL', u'D', 100, 35.14]

        self.dummy_description = [u'Description line 1', u'Description line 2', u'Description line 3']
        self.dummy_description_update = [u'Description line 1', u'Updated Description line 2', u'Description line 3']
        self.dummy_description_parsed = {0: u'Description line 1', 1: u'Description line 2', 2: u'Description line 3'}

    def tearDown(self):
        try:
            self.db.close()

        except Exception:
            pass

        os.remove(self.db.db_path)

        if os.path.exists(self.db_path_old):
            os.remove(self.db_path_old)

        if os.path.exists(os.path.join(self.file_dir, u'dump_config')):
            shutil.rmtree(os.path.join(self.file_dir, u'dump_config'))

    # Useful methods
    def dummy_create_table(self):
        self.db.create_table(table=self.dummy_table,
                             columns=self.dummy_columns)

    def dummy_select(self):
        self.db.select(table=self.dummy_table)

    def dummy_insert_data(self):

        for item in self.dummy_data:
            self.db.execute(statement=u'INSERT INTO testing VALUES (?,?,?,?,?)',
                            params=tuple(item))


class TestDatabaseHandlerGeneral(TestDatabaseHandler):

    def check_record_status(self):
        return False

    # Test cases
    def test_initialise_db(self):
        self.assertTrue(os.path.exists(self.db_path))

    def test_reinitialise_db_backup_false(self):

        # Basic checks
        self.assertTrue(os.path.exists(self.db_path))

        headings = self.db.get_tables()
        expected_output = [u'db_change_log', u'table_descriptions', u'general_config']

        self.assertEqual(set(headings.keys()), set(expected_output))

        # Now re-init and re-check
        self.db.reinitialise_db(backup=False)
        self.db.open()

        self.assertTrue(os.path.exists(self.db_path))

        headings = self.db.get_tables()
        expected_output = [u'db_change_log', u'table_descriptions', u'general_config']

        self.assertEqual(set(headings.keys()), set(expected_output))

    def test_reinitialise_db_backup_true(self):

        # Basic checks
        self.assertTrue(os.path.exists(self.db_path))

        headings = self.db.get_tables()
        expected_output = [u'db_change_log', u'table_descriptions', u'general_config']

        self.assertEqual(set(headings.keys()), set(expected_output))

        # Now re-init and re-check
        self.db.reinitialise_db(backup=True)
        self.db.open()

        self.assertTrue(os.path.exists(self.db_path))
        self.assertTrue(os.path.exists(self.db_path_old))

        headings = self.db.get_tables()
        expected_output = [u'db_change_log', u'table_descriptions', u'general_config']

        self.assertEqual(set(headings.keys()), set(expected_output))

    def test_open(self):
        self.assertIsNotNone(self.db.database_connection)
        self.assertIsNotNone(self.db.database_cursor)
        self.assertIsNotNone(self.db.db_version)
        self.assertTrue(self.db.db_open)

    def test_open_failure(self):
        with self.assertRaises(Exception):
            database_handler.DatabaseHandler(u'/test.db')

    def test_close(self):

        self.db.close()

        self.assertIsNone(self.db.database_connection)
        self.assertIsNone(self.db.database_cursor)
        self.assertIsNone(self.db.db_version)
        self.assertFalse(self.db.db_open)

    def test_set_cursor(self):
        self.db.database_cursor = None
        self.db.set_cursor()

        self.assertIs(type(self.db.database_cursor), sqlite3.Cursor)

    def test_get_cursor(self):
        self.assertIs(type(self.db.database_cursor), sqlite3.Cursor)

    def test_execute(self):

        self.db.execute(u'SELECT * FROM general_config')

        rows = self.db.fetchall()

        self.assertEqual(len(rows), 1)
        self.assertIn(u'db_creation_date', rows[0])

    def test_execute_failed_no_cursor(self):

        self.db.database_cursor = None

        with self.assertRaises(Exception):
            self.db.execute(u'SELECT * FROM table_descriptions')

    def test_execute_failed_statement(self):

        with self.assertRaises(Exception):
            self.db.execute(u'SELECT * FROM does_not_exist')

    def test_get_db_version(self):
        version = self.db.get_db_version()
        self.assertEqual(version, 0)

    def test_set_db_version(self):

        ver = 33

        self.db.set_db_version(version=ver)
        version = self.db.get_db_version()

        self.assertEqual(version, ver)

    def test_increment_db_version(self):

        version = self.db.get_db_version()
        self.assertEqual(version, 0)

        self.db.increment_db_version()

        version = self.db.get_db_version()
        self.assertEqual(version, 1)

    def test_save(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.assertTrue(os.path.exists(os.path.join(self.file_dir, u'test.db')))
        self.assertTrue(os.path.exists(os.path.join(self.file_dir, u'test.db-journal')))

        self.db.save()

        self.assertTrue(os.path.exists(os.path.join(self.file_dir, u'test.db')))
        self.assertFalse(os.path.exists(os.path.join(self.file_dir, u'test.db-journal')))

    def test_save_failed(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.assertTrue(os.path.exists(os.path.join(self.file_dir, u'test.db')))
        self.assertTrue(os.path.exists(os.path.join(self.file_dir, u'test.db-journal')))

        os.remove(os.path.join(self.file_dir, u'test.db-journal'))

        with self.assertRaises(Exception):
            self.db.save()

    def test_fetchone(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.dummy_select()

        row = self.db.fetchone()
        expected_output = tuple(self.dummy_data[0])

        self.assertEqual(row, expected_output)

    def test_fetchone_formatted(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.dummy_select()

        row = self.db.fetchone_formatted()
        expected_output = self.dummy_data[0]

        self.assertIs(type(row), OrderedDict)

        for i, heading in enumerate(self.dummy_headings):
            self.assertEqual(row.get(heading), expected_output[i])

    def test_fetchall(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.dummy_select()

        rows = self.db.fetchall()
        expected_output = [tuple(d) for d in self.dummy_data]

        self.assertEqual(rows, expected_output)

    def test_fetchall_formatted(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.dummy_select()

        rows = self.db.fetchall_formatted()

        self.assertIs(type(rows), list)

        for i, row in enumerate(rows):

            self.assertIs(type(row), OrderedDict)

            expected_output = self.dummy_data[i]

            for j, heading in enumerate(self.dummy_headings):
                self.assertEqual(row.get(heading), expected_output[j])

    def test_get_table_row_count(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        count = self.db.get_table_row_count(table=self.dummy_table)

        self.assertEqual(count, 3)

    def test_handle_where(self):
        where = [{u'column': u'trans',
                  u'value': u'BUY',
                  u'operator': u'='},
                 {u'column': u'symbol',
                  u'value': u'A',
                  u'operator': u'=',
                  u'condition': u'AND'}]

        output = self.db.handle_where(where=where)

        expected_output = (u'WHERE trans = ? AND symbol = ? ', (u'BUY', u'A'))

        self.assertIs(type(expected_output), tuple)
        self.assertEqual(output, expected_output)

    def test_select_basic(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.db.select(table=self.dummy_table)
        self.assertEqual(self.db.last_select_table, self.dummy_table)

        rows = self.db.fetchall()
        self.assertEqual(len(rows), 3)

    def test_select_columns(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.db.select(table=self.dummy_table,
                       select_columns=[self.dummy_headings[1],
                                       self.dummy_headings[3]])
        self.assertEqual(self.db.last_select_table, self.dummy_table)

        row = self.db.fetchone()
        expected_output = (self.dummy_data[0][1],
                           self.dummy_data[0][3])

        self.assertEqual(row, expected_output)

    def test_select_where(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.db.select(table=self.dummy_table,
                       where=[{u'column': u'trans',
                               u'value': u'BUY',
                               u'operator': u'='},
                              {u'column': u'symbol',
                               u'value': u'A',
                               u'operator': u'=',
                               u'condition': u'AND'}])
        self.assertEqual(self.db.last_select_table, self.dummy_table)

        rows = self.db.fetchall()
        expected_output = tuple(self.dummy_data[2])

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], expected_output)

    def test_select_order_by(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.db.select(table=self.dummy_table,
                       order_by=[u'trans', u'symbol'])
        self.assertEqual(self.db.last_select_table, self.dummy_table)

        rows = self.db.fetchall()

        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], tuple(self.dummy_data[2]))
        self.assertEqual(rows[1], tuple(self.dummy_data[0]))
        self.assertEqual(rows[2], tuple(self.dummy_data[1]))

    def test_get_formatted_row(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        row = self.db.get_formatted_row(table=self.dummy_table,
                                        where=[{u'column': u'trans',
                                                u'value': u'BUY',
                                                u'operator': u'='},
                                               {u'column': u'symbol',
                                                u'value': u'A',
                                                u'operator': u'=',
                                                u'condition': u'AND'}])

        expected_output = self.dummy_data[2]

        self.assertIs(type(row), OrderedDict)

        for i, heading in enumerate(self.dummy_headings):
            self.assertEqual(row.get(heading), expected_output[i])

    def test_update_record_insert(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        # Update & Check
        self.db.update_record(table=u'testing',
                              values={u'date': u'2006-01-08',
                                      u'trans': u'SELL',
                                      u'symbol': u'D',
                                      u'qty': 100,
                                      u'price': 35.14},
                              where=[{u'column': u'symbol',
                                      u'value': u'D',
                                      u'operator': u'='}])

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 4)

        for row in rows[:2]:
            self.assertIn(row, self.dummy_data)

        expected_output = self.dummy_data_extra
        expected_output[0] = u'2006-01-08'

        self.assertEqual(rows[3], expected_output)

    def test_update_record_update(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.db.insert(table=self.dummy_table,
                       columns=self.dummy_headings,
                       values=self.dummy_data_extra)

        # Update & Check
        self.db.update_record(table=u'testing',
                              values={u'date': u'2006-01-08',
                                      u'trans': u'SELL',
                                      u'symbol': u'D',
                                      u'qty': 100,
                                      u'price': 35.14},
                              where=[{u'column': u'symbol',
                                      u'value': u'D',
                                      u'operator': u'='}])

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 4)

        for row in rows[:2]:
            self.assertIn(row, self.dummy_data)

        expected_output = self.dummy_data_extra
        expected_output[0] = u'2006-01-08'

        self.assertEqual(rows[3], expected_output)

    def test_get_tables(self):

        tables = self.db.get_tables()

        self.assertEqual(len(tables), 3)

        self.assertIn(u'db_change_log', tables)
        self.assertEqual(tables.get(u'db_change_log'),
                         [u'id', u'db_root_name', u'db_version', u'sql_command', u'sql_params'])

        self.assertIn(u'general_config', tables)
        self.assertEqual(tables.get(u'general_config'), [u'parameter', u'value'])

        self.assertIn(u'table_descriptions', tables)
        self.assertEqual(tables.get(u'table_descriptions'), [u'table_name', u'description_row', u'description'])

    def test_get_table_headings(self):

        self.dummy_create_table()
        self.dummy_select()
        headings = self.db.get_table_headings()

        expected_output = self.dummy_headings

        self.assertEqual(headings, expected_output)

    def test_get_table_data(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        data = self.db.get_table_data(table_name=self.dummy_table)

        # Check return type is correct
        self.assertIs(type(data), list)

        for i, item in enumerate(data):

            # Check item type is correct
            self.assertIs(type(item), OrderedDict)

            # Check returned data is correct
            self.assertEqual(item.get(self.dummy_headings[0]), self.dummy_data[i][0])
            self.assertEqual(item.get(self.dummy_headings[1]), self.dummy_data[i][1])
            self.assertEqual(item.get(self.dummy_headings[2]), self.dummy_data[i][2])
            self.assertEqual(item.get(self.dummy_headings[3]), self.dummy_data[i][3])
            self.assertEqual(item.get(self.dummy_headings[4]), self.dummy_data[i][4])

    def test_get_table_data_dictionary(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)

        # Check return type is correct
        self.assertIs(type(data), dict)

        # Check expected items exist
        self.assertIn(u'rows', data)
        self.assertIn(u'table_name', data)
        self.assertIn(u'headings', data)

        # Check name & headings
        self.assertEqual(data.get(u'table_name'), self.dummy_table)
        self.assertEqual(data.get(u'headings'), self.dummy_headings)

        # Check rows
        for i, item in enumerate(data.get(u'rows')):
            self.assertEqual(item, self.dummy_data[i])

    def test_load_config(self):

        load_dir = os.path.join(self.file_dir, u'load_config')

        self.db.load_config(path=load_dir)
        self.db.open()

        # Check table exists
        self.dummy_select()
        headings = self.db.get_table_headings()
        expected_output = self.dummy_headings

        self.assertEqual(headings, expected_output)

        # Check rows
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)

        expected_data = [[str(d) for d in row] for row in self.dummy_data]
        expected_data.append([str(d) for d in self.dummy_data_extra])

        for i, item in enumerate(data.get(u'rows')):
            self.assertIn(item, expected_data)

    def test_load_config_updates(self):

        load_dir = os.path.join(self.file_dir, u'load_config_updates')

        self.dummy_create_table()
        self.dummy_insert_data()
        self.db.load_config_updates(path=load_dir)
        self.db.open()

        # Check table exists
        self.dummy_select()
        headings = self.db.get_table_headings()
        expected_output = self.dummy_headings

        self.assertEqual(headings, expected_output)

        # Check rows
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)

        expected_data = self.dummy_data
        expected_data.append(self.dummy_data_extra)

        for row in expected_data:
            if row[2] == u'B':
                row[1] = u'BUY'

        for i, item in enumerate(data.get(u'rows')):
            self.assertIn(item, expected_data)

    def test_dump_config(self):

        dump_dir = os.path.join(self.file_dir, u'dump_config')

        self.dummy_create_table()
        self.dummy_insert_data()

        self.db.dump_config(path=dump_dir)

        # Check expected files exist
        self.assertEqual(os.listdir(dump_dir), [u'db_change_log.txt',
                                                u'general_config.txt',
                                                u'table_descriptions.txt',
                                                u'testing.txt'])

        # Check contents of file
        with open(os.path.join(dump_dir, u'testing.txt')) as f:
            data = f.readlines()

        expected_data = [u'   date    | trans | symbol |  qty  | price\n',
                         u'-----------+-------+--------+-------+------\n',
                         u'2006-01-05 | BUY   | C      | 100.0 | 35.14\n',
                         u'2006-01-06 | SELL  | B      | 100.0 | 35.14\n',
                         u'2006-01-07 | BUY   | A      | 100.0 | 35.14']

        self.assertEqual(data, expected_data)

    def test_parse_table_description(self):

        parsed_descr = self.db.parse_table_description(self.dummy_description)

        self.assertEqual(parsed_descr, self.dummy_description_parsed)

    def test_get_table_description(self):

        descr = self.db.get_table_description(table=u'general_config')

        self.assertEqual(descr, [(u'general_config', 0,
                                  u'A place to store any General configuration parameters that do not fit elsewhere!'),
                                 (u'general_config', 1,
                                  u'NOTE: This file is for information only and will not be imported, '),
                                 (u'general_config', 2,
                                  u'      Any changes should be performed in your code!')])

    def test_insert_table_description(self):

        self.db.insert_table_description(table=self.dummy_table,
                                         description=self.dummy_description)

        descr = self.db.get_table_description(table=self.dummy_table)

        self.assertEqual(descr, [(u'testing', 0, u'Description line 1'),
                                 (u'testing', 1, u'Description line 2'),
                                 (u'testing', 2, u'Description line 3')])

    def test_update_table_description(self):

        self.db.update_table_description(table=self.dummy_table,
                                         description=self.dummy_description_update)

        descr = self.db.get_table_description(table=self.dummy_table)

        self.assertEqual(descr, [(u'testing', 0, u'Description line 1'),
                                 (u'testing', 1, u'Updated Description line 2'),
                                 (u'testing', 2, u'Description line 3')])

    def test_check_if_row_blank_true(self):
        row = [u'', u'', u'', u'', u'']
        output = self.db.check_if_row_blank(row)

        self.assertTrue(output)

    def test_check_if_row_blank_false(self):
        row = [u'', u'', u'a', u'', u'']
        output = self.db.check_if_row_blank(row)

        self.assertFalse(output)


class TestDatabaseHandlerNoRecord(TestDatabaseHandler):

    def check_record_status(self):
        return False

    # Test cases
    def test_create_table(self):

        self.dummy_create_table()
        tables = self.db.get_tables()

        self.assertEqual(len(tables), 4)

        self.assertIn(self.dummy_table, tables)
        self.assertEqual(tables.get(self.dummy_table), self.dummy_headings)

    def test_drop_table(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        # Check table exists
        headings = self.db.get_tables()

        self.assertIn(self.dummy_table, headings)

        # Now drop and check no longer exists
        self.db.drop_table(self.dummy_table)
        headings = self.db.get_tables()

        self.assertNotIn(self.dummy_table, headings)

    def test_insert(self):

        self.dummy_create_table()

        self.db.insert(table=self.dummy_table,
                       columns=self.dummy_headings,
                       values=self.dummy_data_extra)

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], self.dummy_data_extra)

    def test_update(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.db.insert(table=self.dummy_table,
                       columns=self.dummy_headings,
                       values=self.dummy_data_extra)

        # Update & Check
        self.db.update(table=u'testing',
                       values={u'date': u'2006-01-08'},
                       where=[{u'column': u'symbol',
                               u'value': u'D',
                               u'operator': u'='}])

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 4)

        for row in rows[:2]:
            self.assertIn(row, self.dummy_data)

        expected_output = self.dummy_data_extra
        expected_output[0] = u'2006-01-08'

        self.assertEqual(rows[3], expected_output)

    def test_delete(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.db.insert(table=self.dummy_table,
                       columns=self.dummy_headings,
                       values=self.dummy_data_extra)

        self.db.delete(table = u'testing',
                       where = [{u'column': u'symbol',
                                 u'value': u'D',
                                 u'operator': u'='}])

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 3)

        for row in rows:
            self.assertIn(row, self.dummy_data)

    def test_add_column(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.db.add_column(table=self.dummy_table,
                           column=(u'test_col_1', u'text'))

        self.dummy_select()

        headings = self.db.get_table_headings()
        expected_output = self.dummy_headings + [u'test_col_1']

        self.assertEqual(headings, expected_output)

        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)

        # Check rows
        for i, item in enumerate(data.get(u'rows')):
            self.assertEqual(item, self.dummy_data[i] + [None])


# TODO: write more unhappy paths. i.e drop/create non-existent table
class TestDatabaseHandlerRecord(TestDatabaseHandler):

    # Records all UPDATE/DELETE/INSERT/CREATE/DROP/ALTER statements

    def check_record_status(self):
        return True

    # Helper functions
    def get_change_log(self):

        self.db.select(table=u'db_change_log')

        return self.db.fetchall()

    # Test cases
    def test_create_table(self):

        self.dummy_create_table()
        tables = self.db.get_tables()

        self.assertEqual(len(tables), 4)

        self.assertIn(self.dummy_table, tables)
        self.assertEqual(tables.get(self.dummy_table), self.dummy_headings)

        change_rows = self.get_change_log()

        self.assertEqual(len(change_rows), 1)
        self.assertEqual(change_rows[0][1], self.db_name)
        self.assertEqual(change_rows[0][3],
                         u'CREATE TABLE {t} ({c})'.format(t=self.dummy_table,
                                                          c=u', '.join([u'{c} {t}'.format(c=c, t=t)
                                                                        for c, t in self.dummy_columns.iteritems()])))
        self.assertEqual(change_rows[0][4], u'()')

    def test_drop_table(self):

        self.dummy_create_table()

        # Check table exists
        headings = self.db.get_tables()

        self.assertIn(self.dummy_table, headings)

        # Now drop and check no longer exists
        self.db.drop_table(self.dummy_table)
        headings = self.db.get_tables()

        self.assertNotIn(self.dummy_table, headings)

        change_rows = self.get_change_log()

        self.assertEqual(len(change_rows), 2)
        self.assertEqual(change_rows[1][1], self.db_name)
        self.assertEqual(change_rows[1][3],
                         u'DROP TABLE {t}'.format(t=self.dummy_table))
        self.assertEqual(change_rows[1][4], u'()')

    def test_insert(self):

        self.dummy_create_table()

        self.db.insert(table=self.dummy_table,
                       columns=self.dummy_headings,
                       values=self.dummy_data_extra)

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], self.dummy_data_extra)

        change_rows = self.get_change_log()

        self.assertEqual(len(change_rows), 2)
        self.assertEqual(change_rows[1][1], self.db_name)
        self.assertEqual(change_rows[1][3],
                         u'INSERT INTO {t} ({c}) VALUES ({v})'.format(t=self.dummy_table,
                                                                      c=u', '.join(self.dummy_columns),
                                                                      v=u','.join([u'?' for _ in self.dummy_columns])))
        self.assertEqual(change_rows[1][4], unicode(tuple(self.dummy_data_extra)))

    def test_update(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.db.insert(table=self.dummy_table,
                       columns=self.dummy_headings,
                       values=self.dummy_data_extra)

        # Update & Check
        self.db.update(table=u'testing',
                       values={u'date': u'2006-01-08'},
                       where=[{u'column': u'symbol',
                               u'value': u'D',
                               u'operator': u'='}])

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 4)

        for row in rows[:2]:
            self.assertIn(row, self.dummy_data)

        expected_output = self.dummy_data_extra
        expected_output[0] = u'2006-01-08'

        self.assertEqual(rows[3], expected_output)

        change_rows = self.get_change_log()

        self.assertEqual(len(change_rows), 6)
        self.assertEqual(change_rows[5][1], self.db_name)
        self.assertEqual(change_rows[5][3],
                         u'UPDATE {t} SET date = \'2006-01-08\' WHERE symbol = ? '.format(t=self.dummy_table))
        self.assertEqual(change_rows[5][4], u"(u'D',)")

    def test_delete(self):

        self.dummy_create_table()
        self.dummy_insert_data()
        self.db.insert(table=self.dummy_table,
                       columns=self.dummy_headings,
                       values=self.dummy_data_extra)

        self.db.delete(table = u'testing',
                       where = [{u'column': u'symbol',
                                 u'value': u'D',
                                 u'operator': u'='}])

        self.dummy_select()
        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)
        rows = data.get(u'rows')

        self.assertEqual(len(rows), 3)

        for row in rows:
            self.assertIn(row, self.dummy_data)

        change_rows = self.get_change_log()

        self.assertEqual(len(change_rows), 6)
        self.assertEqual(change_rows[5][1], self.db_name)
        self.assertEqual(change_rows[5][3],
                         u'DELETE FROM {t} WHERE symbol = ? '.format(t=self.dummy_table))
        self.assertEqual(change_rows[5][4], u"(u'D',)")

    def test_add_column(self):

        self.dummy_create_table()
        self.dummy_insert_data()

        self.db.add_column(table=self.dummy_table,
                           column=(u'test_col_1', u'text'))

        self.dummy_select()

        headings = self.db.get_table_headings()
        expected_output = self.dummy_headings + [u'test_col_1']

        self.assertEqual(headings, expected_output)

        data = self.db.get_table_data_dictionary(table_name=self.dummy_table)

        # Check rows
        for i, item in enumerate(data.get(u'rows')):
            self.assertEqual(item, self.dummy_data[i] + [None])

        change_rows = self.get_change_log()

        self.assertEqual(len(change_rows), 5)
        self.assertEqual(change_rows[4][1], self.db_name)
        self.assertEqual(change_rows[4][3],
                         u'ALTER TABLE {t} ADD COLUMN {c} text'.format(t=self.dummy_table,
                                                                       c=u'test_col_1'))
        self.assertEqual(change_rows[4][4], u'()')


if __name__ == u'__main__':
    unittest.main()
