# vim: set fileencoding=utf-8 :

'''
Functional tests for the jaraco.postgres module.

Intended to be run using py.test.
'''

import os
import shutil
from subprocess import CalledProcessError
import unittest  # We use unittest just for its helpful assertXxxx() methods.

import psycopg2
import portend

import jaraco.postgres as pgtools


UNUSED_PORT = portend.find_available_local_port()


class Test_PostgresDatabase(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        """Automatically called by py.test to set up this class for testing.
        """
        cls.dbms = None
        cls.port = UNUSED_PORT
        cls.dbms = pgtools.PostgresServer(port=cls.port)
        cls.dbms.initdb()
        cls.dbms.start()

    @classmethod
    def teardown_class(cls):
        """Automatically called to undo the effect of .setup_class().
        """
        if cls.dbms:
            cls.dbms.destroy()
            cls.dbms = None

    def setUp(self):
        """Automatically called by py.test once per test method.
        """
        self.database = None

    def tearDown(self):
        """Automatically called to undo the effect of .setUp().
        """
        if self.database:
            self.database.drop_if_exists()
            self.database.drop_user()

    def test___init__can_create_multiple_databases(self):
        database_1 = None
        database_2 = None
        try:
            database_1 = pgtools.PostgresDatabase(db_name='test_pgtools_1',
                port=self.port)
            database_2 = pgtools.PostgresDatabase(db_name='test_pgtools_2',
                port=self.port)
        finally:
            if database_1:
                database_1.drop_if_exists()
            if database_2:
                database_2.drop_if_exists()

    def test___init__ok(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)

    def test___init__ok_when_port_integer(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=int(self.port))

    def test___init__ok_when_port_string(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=str(self.port))

    def test___repr__(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            user='pmxtest', host='localhost', port=self.port,
            superuser='postgres', template='template1')
        self.assertEqual(repr(self.database),
            'PostgresDatabase(db_name=test_pgtools, user=pmxtest, host=localhost,'
            ' port=%s, superuser=postgres, template=template1)' % self.port)

    def test___str__(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            user='pmxtest', host='localhost', port=self.port,
            superuser='postgres', template='template1')
        self.assertEqual(str(self.database),
            'PostgresDatabase(db_name=test_pgtools, user=pmxtest, host=localhost,'
            ' port=%s, superuser=postgres, template=template1)' % self.port)

    def test_create_fails_when_user_nonexistent(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port, user='no_such_user')
        self.assertRaises(CalledProcessError, self.database.create)

    def test_create_ok_when_no_sql(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()

    def test_create_ok_with_sql(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create('CREATE TABLE test (value text)')

    def test_create_ok_with_sql_containing_unicode(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create(u'CREATE TABLE countries (value text) -- ¡México!')

    def test_create_ok_with_sql_using_psl_extensions(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create('\set ON_ERROR_STOP FALSE\nSYNTAX ERROR HERE')

    def test_drop(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.drop()
        # Can't select; the database is gone!
        self.assertRaises(psycopg2.OperationalError, self.database.sql, 'SELECT 1')

    def test_drop_is_idempotent(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.drop()
        self.database.drop()
        self.database.drop()

    def test_psql_detects_bogus_params(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()

    def test_psql_detects_sql_error(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.assertRaises(CalledProcessError, self.database.psql, ['-c', 'bogus'])

    def test_psql_ok_when_sql_is_valid(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.psql(['-c', 'SELECT 1'])

    def test_sql_detects_bogus_params(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.assertRaises(TypeError, self.database.sql, 3.14)
        self.assertRaises(psycopg2.ProgrammingError, self.database.sql, [])

    def test_sql_ok_when_sql_is_valid(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.assertEqual(self.database.sql('SELECT 1'), [(1,)])
        self.assertEqual(self.database.sql("SELECT 'hello', 2"), [('hello', 2)])

    def test_super_psql_detects_bogus_params(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()

    def test_super_psql_detects_sql_error(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.assertRaises(CalledProcessError, self.database.super_psql, ['-c', 'bogus'])

    def test_super_psql_ok_when_sql_is_valid(self):
        self.database = pgtools.PostgresDatabase(db_name='test_pgtools',
            port=self.port)
        self.database.create_user()
        self.database.create()
        self.database.super_psql(['-c', 'SELECT 1'])


class Test_PostgresServer(unittest.TestCase):

    def setUp(self):
        self.dbms = None

    def tearDown(self):
        if self.dbms:
            self.dbms.destroy()
            self.dbms = None

    def test___init__ok(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)

    def test___repr__(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.assertEqual(repr(self.dbms),
            'PostgresServer(host=localhost, port=%s, base_pathname=%s, superuser=%s)'
            % (self.dbms.port, self.dbms.base_pathname, self.dbms.superuser))

    def test___str__(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.assertEqual(str(self.dbms),
            'PostgreSQL server at %s:%s (with storage at %s)' %
            (self.dbms.host, self.dbms.port, self.dbms.base_pathname))

    def test_destroy_handles_deleted_directory(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.dbms.initdb()
        # Reach under the covers and pre-emptively delete the directory.
        # (But first, some checking to prevent hideously self-destructive acts.)
        assert self.dbms.base_pathname is not None
        assert self.dbms.base_pathname is not ''
        assert self.dbms.base_pathname is not '.'
        shutil.rmtree(self.dbms.base_pathname)
        self.dbms.destroy()

    def test_destroy_ok(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.dbms.destroy()

    def test_destroy_is_idempotent(self):
        self.dbms = pgtools.PostgresServer(host='localhost', port=UNUSED_PORT)
        self.dbms.destroy()
        self.dbms.destroy()
        self.dbms.destroy()

    def test_initdb_base_pathname_bogus(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT, base_pathname='/n&^fX:d#f9')
        self.assertRaises((OSError, IOError), self.dbms.initdb)

    def test_initdb_ok(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()

    def test_is_running(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.assertEqual(self.dbms.is_running(), False)
        self.dbms.initdb()
        self.assertEqual(self.dbms.is_running(), False)
        self.dbms.start()
        self.assertEqual(self.dbms.is_running(), True)
        self.dbms.stop()
        self.assertEqual(self.dbms.is_running(), False)

    def test_is_running_tries_bogus(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.assertRaises(ValueError, self.dbms.is_running, -1)
        self.assertRaises(ValueError, self.dbms.is_running, -10)
        self.assertRaises(ValueError, self.dbms.is_running, 0)

    def test_pid(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        pid = self.dbms.pid

        # Weak test -- just check to see whether such a process exists.
        os.kill(pid, 0)
        self.dbms.stop()
        self.assertRaises(OSError, os.kill, pid, 0)

    def test_pid_returns_None_when_not_running(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.assertEqual(self.dbms.pid, None)
        self.dbms.initdb()
        self.assertEqual(self.dbms.pid, None)
        self.dbms.start()
        self.assertNotEqual(self.dbms.pid, None)
        os.kill(self.dbms.pid, 0)
        self.dbms.stop()
        self.assertEqual(self.dbms.pid, None)

    def test_start_host_bogus(self):
        # Hostnames aren't checked until the postgres server starts up
        self.dbms = pgtools.PostgresServer(host='no.such.host.exists')
        self.dbms.initdb()
        self.assertRaises(RuntimeError, self.dbms.start)

    def test_start_port_out_of_range(self):
        self.dbms = pgtools.PostgresServer(port=99999999)
        self.dbms.initdb()
        errors = CalledProcessError, RuntimeError
        self.assertRaises(errors, self.dbms.start)

    def test_start_port_value_error(self):
        self.dbms = pgtools.PostgresServer(port='BOGUS')
        self.dbms.initdb()
        errors = CalledProcessError, RuntimeError
        self.assertRaises(errors, self.dbms.start)

    def test_start_ok(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        self.assertEqual(self.dbms.is_running(), True)

    def test_start_raises_NotInitializedError_when_uninitialized(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.assertRaises(pgtools.NotInitializedError, self.dbms.start)

    def test_stop_is_idempotent(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        self.dbms.stop()
        self.dbms.stop()
        self.dbms.stop()
        self.assertEqual(self.dbms.is_running(), False)

    def test_stop_ok(self):
        self.dbms = pgtools.PostgresServer(port=UNUSED_PORT)
        self.dbms.initdb()
        self.dbms.start()
        self.dbms.stop()
        self.assertEqual(self.dbms.is_running(), False)
