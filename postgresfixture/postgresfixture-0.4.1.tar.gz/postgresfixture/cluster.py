# Copyright 2012-2014 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Manage a PostgreSQL cluster."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "Cluster",
    "PG_VERSION_MAX",
    "PG_VERSIONS",
    ]

from contextlib import closing
from distutils.version import LooseVersion
from glob import iglob
from os import (
    devnull,
    environ,
    makedirs,
    path,
    )
import pipes
from shutil import (
    copyfileobj,
    rmtree,
    )
from subprocess import (
    CalledProcessError,
    check_call,
    )
import sys
from tempfile import TemporaryFile

from postgresfixture.utils import LockFile
import psycopg2


PG_BASE = "/usr/lib/postgresql"

PG_VERSION_BINS = {
    path.basename(pgdir): path.join(pgdir, "bin")
    for pgdir in iglob(path.join(PG_BASE, "*"))
    if path.exists(path.join(pgdir, "bin", "pg_ctl"))
}

PG_VERSION_MAX = max(PG_VERSION_BINS, key=LooseVersion)
PG_VERSIONS = sorted(PG_VERSION_BINS, key=LooseVersion)


def get_pg_bin(version):
    """Return the PostgreSQL ``bin`` directory for the given `version`."""
    return PG_VERSION_BINS[version]


def path_with_pg_bin(exe_path, version):
    """Return `exe_path` with the PostgreSQL ``bin`` directory added."""
    exe_path = [
        elem for elem in exe_path.split(path.pathsep)
        if len(elem) != 0 and not elem.isspace()
        ]
    pg_bin = get_pg_bin(version)
    if pg_bin not in exe_path:
        exe_path.insert(0, pg_bin)
    return path.pathsep.join(exe_path)


class Cluster:
    """Represents a PostgreSQL cluster, running or not."""

    def __init__(self, datadir, version=PG_VERSION_MAX):
        self.datadir = path.abspath(datadir)
        self.version = version
        self.lock = LockFile(path.join(
            path.dirname(self.datadir),
            ".%s.lock" % path.basename(self.datadir)))

    def execute(self, *command, **options):
        """Execute a command with an environment suitable for this cluster."""
        env = options.pop("env", environ).copy()
        env["PATH"] = path_with_pg_bin(env.get("PATH", ""), self.version)
        env["PGDATA"] = env["PGHOST"] = self.datadir
        check_call(command, env=env, **options)

    @property
    def exists(self):
        """Whether or not this cluster exists on disk."""
        version_file = path.join(self.datadir, "PG_VERSION")
        return path.exists(version_file)

    @property
    def pidfile(self):
        """The (expected) pidfile for a running cluster.

        Does *not* guarantee that the pidfile exists.
        """
        return path.join(self.datadir, "postmaster.pid")

    @property
    def logfile(self):
        """The log file used (or will be used) by this cluster."""
        return path.join(self.datadir, "backend.log")

    @property
    def running(self):
        """Whether this cluster is running or not."""
        with open(devnull, "wb") as stdout, TemporaryFile() as stderr:
            try:
                self.execute("pg_ctl", "status", stdout=stdout, stderr=stderr)
            except CalledProcessError as error:
                # PostgreSQL has evolved to return different error codes in
                # later versions, so here we check for specific codes to avoid
                # masking errors from insufficient permissions or missing
                # executables, for example.
                version = LooseVersion(self.version)
                if version >= LooseVersion("9.4"):
                    if error.returncode == 3:
                        # 3 means that the data directory is present and
                        # accessible but that the server is not running.
                        return False
                    elif error.returncode == 4:
                        # 4 means that the data directory is not present or is
                        # not accessible. If it's missing, then the server is
                        # not running. If it is present but not accessible
                        # then crash because we can't know if the server is
                        # running or not.
                        if not self.exists:
                            return False
                elif version >= LooseVersion("9.2"):
                    if error.returncode == 3:
                        # 3 means that the data directory is present and
                        # accessible but that the server is not running OR
                        # that the data directory is not present.
                        return False
                else:
                    if error.returncode == 1:
                        # 1 means that the server is not running OR the data
                        # directory is not present OR that the data directory
                        # is not accessible.
                        return False

                # This is not a recognised error. First print out the cached
                # stderr then re-raise the CalledProcessError.
                try:
                    stderr.seek(0)  # Rewind.
                    copyfileobj(stderr, sys.stderr)
                finally:
                    raise
            else:
                return True

    def create(self):
        """Create this cluster, if it does not exist."""
        with self.lock.exclusive:
            self._create()

    def _create(self):
        if not self.exists:
            if not path.isdir(self.datadir):
                makedirs(self.datadir)
            self.execute("pg_ctl", "init", "-s", "-o", "-E utf8 -A trust")

    def start(self):
        """Start this cluster, if it's not already started."""
        with self.lock.exclusive:
            self._start()

    def _start(self):
        if not self.running:
            self._create()
            # pg_ctl options:
            #  -l <file> -- log file.
            #  -s -- no informational messages.
            #  -w -- wait until startup is complete.
            # postgres options:
            #  -h <arg> -- host name; empty arg means Unix socket only.
            #  -F -- don't bother fsync'ing.
            #  -k -- socket directory.
            self.execute(
                "pg_ctl", "start", "-l", self.logfile, "-s", "-w",
                "-o", "-h '' -F -k %s" % pipes.quote(self.datadir))

    def connect(self, database="template1", autocommit=True):
        """Connect to this cluster."""
        connection = psycopg2.connect(
            database=database, host=self.datadir)
        connection.autocommit = autocommit
        return connection

    def shell(self, database="template1"):
        self.execute("psql", "--quiet", "--", database)

    @property
    def databases(self):
        """The names of databases in this cluster."""
        with closing(self.connect("postgres")) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("SELECT datname FROM pg_catalog.pg_database")
                return {name for (name,) in cur.fetchall()}

    def createdb(self, name):
        """Create the named database."""
        with closing(self.connect()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("CREATE DATABASE %s" % name)

    def dropdb(self, name):
        """Drop the named database."""
        with closing(self.connect()) as conn:
            with closing(conn.cursor()) as cur:
                cur.execute("DROP DATABASE %s" % name)

    def stop(self):
        """Stop this cluster, if started."""
        with self.lock.exclusive:
            self._stop()

    def _stop(self):
        if self.running:
            # pg_ctl options:
            #  -w -- wait for shutdown to complete.
            #  -m <mode> -- shutdown mode.
            self.execute("pg_ctl", "stop", "-s", "-w", "-m", "fast")

    def destroy(self):
        """Destroy this cluster, if it exists.

        The cluster will be stopped if it's started.
        """
        with self.lock.exclusive:
            self._destroy()

    def _destroy(self):
        if self.exists:
            self._stop()
            rmtree(self.datadir)
