'''
This module provides helpers for creating and managing databases.

This technique may be helpful in production code, and it's especially relevant
to functional tests which depend on test databases.

Note that this package is more "persistent" than you might expect. The
Postgres
servers created by this module will remain alive after this module terminates.
A future instance of this module, running in a different process, can adopt
that postgres server and manage it without a hitch.

Thus this module can create a postgres server at one time, then be reborn in
another process at another time and continue to manage that server. It can
also
manage postgres servers and databases that were created elsewhere.

This capability is useful for production code, where many things may happen
between server launch and server shutdown.

The key to this flexibility is that the DBMS can be located by pathname to the
storage directory. That pathname handle leads to the server's PID, status,
etc.

Warning: These methods are inconsistent about the exceptions that they raise.
Some errors provoke OSError, whereas other similar errors might provoke
CalledProcessError or RuntimeError.  This should be made consistent.
'''

from __future__ import absolute_import, print_function

import glob
import logging
import os
import shutil
import signal
import subprocess
import tempfile
import time
import importlib
import itertools
import re

from jaraco.services import paths


DEV_NULL = open(os.path.devnull, 'r+')

log = logging.getLogger('jaraco.postgres')


class NotInitializedError(Exception):
    "An exception raised when an uninitialized DBMS is asked to do something"


class PostgresDatabase(object):
    '''
    Typical usage:
        db = PostgresDatabase(db_name='test_db', user='test_user')
        db.create_user()
        db.create('CREATE TABLE foo (value text not null); ...')
        db.sql('Ad-hoc string of SQL...')
        ...
        db.drop()
        db.drop_user()
    '''
    def __init__(self, db_name, user='pmxtest', host='localhost',
                 port=5432, superuser='postgres', template='template1'):
        '''Manage a database.  (Not a DBMS; just a database.)

        This method doesn't do anything; it just remembers its params for use
        by subsequent method calls.

        @param db_name: The name of the database.
        @type schema: str

        Note: Tested with postgresql 8.3

        WARNING: Some methods are open to SQL injection attack; don't pass
        unvetted values of <db_name>, <user>, etc.
        '''
        # Mild defense against SQL injection attacks.
        assert "'" not in user
        assert "'" not in db_name
        assert "'" not in template

        self.db_name = db_name
        self.user = user
        self.host = host
        self.port = str(port)
        self.superuser = superuser
        self.template = template

    def __repr__(self):
        tmpl = (
            'PostgresDatabase(db_name=%s, '
            'user=%s, host=%s, port=%s, '
            'superuser=%s, template=%s)'
        )
        return tmpl % (
            self.db_name, self.user, self.host,
            self.port, self.superuser, self.template
        )

    __str__ = __repr__

    def create(self, sql=None):
        """CREATE this DATABASE.

        @param sql: (Optional) A string of psql (such as might be generated
        by pg_dump); it will be executed by psql(1) after creating the
        database.
        @type sql: str

        @rtype: None
        """
        create_sql = 'CREATE DATABASE {self.db_name} WITH OWNER {self.user}'
        create_sql = create_sql.format(**vars())
        self.super_psql(['-c', create_sql])
        if sql:
            self.psql_string(sql)

    def psql_string(self, sql):
        """
        Evaluate the sql file (possibly multiple statements) using psql.
        """
        argv = [
            PostgresFinder.find_root() / 'psql',
            '--quiet',
            '-U', self.user,
            '-h', self.host,
            '-p', self.port,
            '-f', '-',
            self.db_name,
        ]
        popen = subprocess.Popen(argv, stdin=subprocess.PIPE)
        popen.communicate(input=sql.encode('utf-8'))
        if popen.returncode != 0:
            raise subprocess.CalledProcessError(popen.returncode, argv)

    def create_user(self):
        """
        CREATE this USER.

        Beware that this method is open to SQL injection attack.  Don't use
        unvetted values of self.user.
        """
        self.super_psql(['-c', "CREATE USER %s" % self.user])

    def drop(self):
        """DROP this DATABASE, if it exists."""
        self.super_psql(['-c', "DROP DATABASE IF EXISTS %s" % self.db_name])

    # For legacy compatibility.
    drop_if_exists = drop

    def drop_user(self):
        """DROP this USER, if it exists."""
        self.super_psql(['-c', "DROP USER IF EXISTS %s" % self.user])

    def psql(self, args):
        """Invoke psql, passing the given command-line arguments.

        Typical <args> values: ['-c', <sql_string>] or ['-f', <pathname>].

        Connection parameters are taken from self.  STDIN, STDOUT,
        and STDERR are inherited from the parent.

        WARNING: This method uses the psql(1) program, which ignores SQL
        errors
        by default.  That hides many real errors, making our software less
        reliable.  To overcome this flaw, add this line to the head of your
        SQL:
            "\set ON_ERROR_STOP TRUE"

        @return: None. Raises an exception upon error, but *ignores SQL
        errors* unless "\set ON_ERROR_STOP TRUE" is used.
        """
        argv = [
            PostgresFinder.find_root() / 'psql',
            '--quiet',
            '-U', self.user,
            '-h', self.host,
            '-p', self.port,
        ] + args + [self.db_name]
        subprocess.check_call(argv)

    def sql(self, input_string, *args):
        """Execute a SQL command using the Python DBI directly.

        Connection parameters are taken from self.  Autocommit is in effect.

        Example: .sql('SELECT %s FROM %s WHERE age > %s', 'name', 'table1',
            '45')

        @param input_string: A string of SQL.  May contain %s or %(name)s
        format specifiers; they are replaced with corresponding values taken
        from args.

        @param args: zero or more parameters to interpolate into the string.
        Note that they're passed individually, not as a single tuple.

        @return: Whatever .fetchall() returns.
        """
        """
        # I advise against using sqlalchemy here (it's more complicated than
        # what we need), but here's an implementation Just In Case.  -jps
        import psycopg2, sqlalchemy
        engine = sqlalchemy.create_engine(
            'postgres://%s@%s:%s/%s' %
            (self.user, self.host, self.port, self.db_name),
            echo=False, poolclass=sqlalchemy.pool.NullPool)
        connection = engine.connect()
        result = connection.execute(input_string, *args)
        try:
            # sqlalchemy 0.6.7 offers a result.returns_rows attribute, but
            # no prior version offers anything comparable.  A tacky
            # workaround...
            try:
                return result.fetchall()
            except psycopg2.ProgrammingError:
                return None
        finally:
            result.close()
            connection.close()
        """
        psycopg2 = importlib.import_module('psycopg2')
        importlib.import_module('psycopg2.extensions')
        connection = psycopg2.connect(
            user=self.user, host=self.host,
            port=self.port, database=self.db_name)
        connection.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            cursor = connection.cursor()
            cursor.execute(input_string, args)
            # No way to ask whether any rows were returned, so just try it...
            try:
                return cursor.fetchall()
            except psycopg2.ProgrammingError:
                return None
        finally:
            connection.close()

    def super_psql(self, args):
        """Just like .psql(), except that we connect as the database superuser
        (and we connect to the superuser's database, not the user's database).
        """
        argv = [
            PostgresFinder.find_root() / 'psql',
            '--quiet',
            '-U', self.superuser,
            '-h', self.host,
            '-p', self.port,
        ] + args
        subprocess.check_call(argv)


class PostgresServer(object):
    def __init__(
            self, host='localhost', port=5432, base_pathname=None,
            superuser='postgres'):
        """This class represents a DBMS server.

        This class can represent either
          - a postgres instance that's already up and running as part of
            the basic infrastructure, or
          - a temporary, local, homegrown instance that only you know about.
        It's your choice.  It depends on whether you call the .initdb()
        and .start() methods.

        @param base_pathname: (Optional) The directory wherein the server
        will store all files. If None or '', a temporary directory will be
        used.
        @type base_pathname: (str, None)

        @param schema: (Optional) A string of SQL which creates a schema,
        such as might be generated by pg_dump.
        @type schema: (str, None)

        Note: Tested with postgresql 8.3.7
        """
        self.host = str(host)
        self.port = str(port)
        self.base_pathname = base_pathname
        self.superuser = superuser

    def __repr__(self):
        tmpl = (
            'PostgresServer(host={host}, '
            'port={port}, '
            'base_pathname={base_pathname}, '
            'superuser={superuser})'
        )
        return tmpl.format(**vars(self))

    def __str__(self):
        tmpl = 'PostgreSQL server at %s:%s (with storage at %s)'
        return tmpl % (self.host, self.port, self.base_pathname)

    def destroy(self):
        """Undo the effects of initdb.

        Destroy all evidence of this DBMS, including its backing files.
        """
        self.stop()
        if self.base_pathname is not None:
            self._robust_remove(self.base_pathname)

    @staticmethod
    def _robust_remove(path):
        """
        Remove the directory specified by `path`. Because we can't determine
        directly if the path is in use, and on Windows, it's not possible to
        remove a path if it is in use, retry a few times until the call
        succeeds.
        """
        tries = itertools.count()
        max_tries = 50
        while os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except WindowsError:
                if next(tries) >= max_tries:
                    raise
                time.sleep(0.2)

    def initdb(self, quiet=True, locale='en_US.UTF-8'):
        """Bootstrap this DBMS from nothing.

        If you're running in an environment where the DBMS is provided as part
        of the basic infrastructure, you probably don't want to call this
        method!

        @param quiet: Should we operate quietly, emitting nothing if things go
        well?
        """
        # Defining base_pathname is deferred until this point because we don't
        # want to create a temp directory unless it's needed.  And now it is!
        if self.base_pathname in [None, '']:
            self.base_pathname = tempfile.mkdtemp()
        if not os.path.isdir(self.base_pathname):
            os.mkdir(self.base_pathname)
        stdout = DEV_NULL if quiet else None
        # The database superuser needs no password at this point(!).
        arguments = [
            '--auth=trust',
            '--username', self.superuser,
        ]
        if locale is not None:
            arguments.extend(('--locale', locale))
        cmd = [
            PostgresFinder.find_root() / 'initdb',
        ] + arguments + ['--pgdata', self.base_pathname]
        log.info('Initializing PostgreSQL with command: {}'.format(
            ' '.join(cmd)
        ))
        subprocess.check_call(cmd, stdout=stdout)

    @property
    def data_directory(self):
        return self.get_setting('data_directory')

    def get_setting(self, name):
        assert re.match('[A-Za-z_]', name)
        tmpl = "select setting from pg_settings where name='{name}';"
        query = tmpl.format(**locals())
        cmd = [
            PostgresFinder.find_root() / 'psql',
            '-p', self.port,
            'postgres',
            '-c', query,
            '-t',
        ]
        return subprocess.check_output(cmd)

    def is_running(self, tries=10):
        """
        Return True if this server is currently running and reachable.

        The postgres tools have critical windows during which they give
        misbehave
        or give the wrong answer.  If postgres was just launched:
            - it might not yet appear to be running, or
            - pg_ctl might think that it's running, but psql might not yet
              be able to connect to it, or
            - it might be about to abort because of a configuration problem,
            - or all three!  It might be starting up, but about to abort.
        Sadly, it's not easy to make a declaration about state if the server
        just started
        or stopped.  To increase confidence, makes repeated checks,
        and declares a decision only after <tries> consecutive measurements
        agree.
        """
        return self._is_running(tries) and (self._assert_ready() or True)

    def _is_running(self, tries=10):
        """
        Return if the server is running according to pg_ctl.
        """
        # We can't possibly be running if our base_pathname isn't defined.
        if not self.base_pathname:
            return False

        if tries < 1:
            raise ValueError('tries must be > 0')

        cmd = [
            PostgresFinder.find_root() / 'pg_ctl',
            'status',
            '-D',
            self.base_pathname,
        ]
        votes = 0
        while abs(votes) < tries:
            time.sleep(0.1)
            running = (subprocess.call(cmd, stdout=DEV_NULL) == 0)
            if running and votes >= 0:
                votes += 1
            elif not running and votes <= 0:
                votes -= 1
            else:
                votes = 0

        return votes > 0

    def _assert_ready(self):
        if self.ready():
            return
        cmd = self._psql_cmd()
        tmpl = 'The %s is supposedly up, but "%s" cannot connect'
        raise RuntimeError(tmpl % (self, ' '.join(cmd)))

    def _psql_cmd(self):
        return [
            PostgresFinder.find_root() / 'psql',
            '-h', self.host,
            '-p', self.port,
            '-U', self.superuser,
        ]

    def ready(self):
        """
        Assumes postgres now talks to pg_ctl, but might not yet be listening
        or connections from psql.  Test that psql is able to connect, as
        it occasionally takes 5-10 seconds for postgresql to start listening.
        """
        cmd = self._psql_cmd()
        for i in range(50, -1, -1):
            res = subprocess.call(
                cmd, stdin=DEV_NULL, stdout=DEV_NULL,
                stderr=DEV_NULL)
            if res == 0:
                break
            time.sleep(0.2)
        return i != 0

    @property
    def pid(self):
        """The server's PID (None if not running).
        """
        # We can't possibly be running if our base_pathname isn't defined.
        if not self.base_pathname:
            return None
        try:
            pidfile = os.path.join(self.base_pathname, 'postmaster.pid')
            return int(open(pidfile).readline())
        except (IOError, OSError):
            return None

    @staticmethod
    def get_version():
        """Returns the Postgres version in tuple form, e.g: (9, 1)"""
        cmd = [PostgresFinder.find_root() / 'pg_ctl', '--version']
        results = subprocess.check_output(cmd).decode('utf-8')
        match = re.search(r'(\d+\.\d+(\.\d+)?)', results)
        if match:
            ver_string = match.group(0)
            return tuple(int(x) for x in ver_string.split('.'))

    def start(self):
        """Launch this postgres server.  If it's already running, do nothing.

        If the backing storage directory isn't configured, raise
        NotInitializedError.

        This method is optional.  If you're running in an environment
        where the DBMS is provided as part of the basic infrastructure,
        you probably want to skip this step!
        """
        log.info('Starting PostgreSQL at %s:%s', self.host, self.port)
        if not self.base_pathname:
            tmpl = ('Invalid base_pathname: %r.  Did you forget to call '
                    '.initdb()?')
            raise NotInitializedError(tmpl % self.base_pathname)

        conf_file = os.path.join(self.base_pathname, 'postgresql.conf')
        if not os.path.exists(conf_file):
            tmpl = 'No config file at: %r.  Did you forget to call .initdb()?'
            raise NotInitializedError(tmpl % self.base_pathname)

        if not self.is_running():
            version = self.get_version()
            if version and version >= (9, 3):
                socketop = 'unix_socket_directories'
            else:
                socketop = 'unix_socket_directory'
            postgres_options = [
                # When running not as root, postgres might try to put files
                #  where they're not writable (see
                #  https://paste.yougov.net/YKdgi). So set the socket_dir.
                '-c', '{}={}'.format(socketop, self.base_pathname),
                '-h', self.host,
                '-i',  # enable TCP/IP connections
                '-p', self.port,
            ]
            subprocess.check_call([
                PostgresFinder.find_root() / 'pg_ctl',
                'start',
                '-D', self.base_pathname,
                '-l', os.path.join(self.base_pathname, 'postgresql.log'),
                '-o', subprocess.list2cmdline(postgres_options),
            ])

        # Postgres may launch, then abort if it's unhappy with some parameter.
        # This post-launch test helps us decide.
        if not self.is_running():
            tmpl = ('%s aborted immediately after launch, check '
                    'postgresql.log in storage dir')
            raise RuntimeError(tmpl % self)

    def stop(self):
        """Stop this DMBS daemon.  If it's not currently running, do nothing.

        Don't return until it's terminated.
        """
        log.info('Stopping PostgreSQL at %s:%s', self.host, self.port)
        if self._is_running():
            cmd = [
                PostgresFinder.find_root() / 'pg_ctl',
                'stop',
                '-D', self.base_pathname,
                '-m', 'fast',
            ]
            subprocess.check_call(cmd)
            # pg_ctl isn't reliable if it's called at certain critical times
            if self.pid:
                os.kill(self.pid, signal.SIGTERM)
        # Can't use wait() because the server might not be our child
        while self._is_running():
            time.sleep(0.1)

    def create(self, db_name, **kwargs):
        """
        Construct a PostgresDatabase and create it on self
        """
        db = PostgresDatabase(
            db_name, host=self.host, port=self.port,
            superuser=self.superuser, **kwargs)
        db.create_user()
        db.create()
        return db


class PostgresFinder(paths.PathFinder):
    # Where are the postgres executables?  Consider the following pathnames in
    # order.
    heuristic_paths = [
        # look on $PATH
        '',
        '/usr/local/pgsql/bin/',
        '/Program Files/pgsql/bin',
    ]
    # Prefer the highest-numbered version available.
    heuristic_paths.extend(
        sorted(glob.glob('/usr/lib/postgresql/*/bin'), reverse=True)
    )

    # allow the environment to stipulate where Postgres must
    #  be found.
    env_paths = [
        os.path.join(os.environ[key], 'bin')
        for key in ['POSTGRESQL_HOME']
        if key in os.environ
    ]

    candidate_paths = env_paths or heuristic_paths

    exe = 'pg_ctl'
    args = ['--version']
