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
    "ClusterFixture",
    ]

from errno import (
    EEXIST,
    ENOENT,
    ENOTEMPTY,
    )
from os import (
    getpid,
    listdir,
    makedirs,
    path,
    rmdir,
    unlink,
    )

from fixtures import Fixture
from postgresfixture.cluster import (
    Cluster,
    PG_VERSION_MAX,
    )


class ProcessSemaphore:
    """A sort-of-semaphore where it is considered locked if a directory cannot
    be removed.

    The locks are taken out one per-process, so this is a way of keeping a
    reference to a shared resource between processes.
    """

    def __init__(self, lockdir):
        super(ProcessSemaphore, self).__init__()
        self.lockdir = lockdir
        self.lockfile = path.join(
            self.lockdir, "%d" % getpid())

    def acquire(self):
        try:
            makedirs(self.lockdir)
        except OSError as error:
            if error.errno != EEXIST:
                raise
        open(self.lockfile, "w").close()

    def release(self):
        try:
            unlink(self.lockfile)
        except OSError as error:
            if error.errno != ENOENT:
                raise

    @property
    def locked(self):
        try:
            rmdir(self.lockdir)
        except OSError as error:
            if error.errno == ENOTEMPTY:
                return True
            elif error.errno == ENOENT:
                return False
            else:
                raise
        else:
            return False

    @property
    def locked_by(self):
        try:
            return [
                int(name) if name.isdigit() else name
                for name in listdir(self.lockdir)
                ]
        except OSError as error:
            if error.errno == ENOENT:
                return []
            else:
                raise


class ClusterFixture(Cluster, Fixture):
    """A fixture for a `Cluster`."""

    def __init__(self, datadir, preserve=False, version=PG_VERSION_MAX):
        """
        @param preserve: Leave the cluster and its databases behind, even if
            this fixture creates them.
        """
        super(ClusterFixture, self).__init__(datadir, version=version)
        self.preserve = preserve
        self.shares = ProcessSemaphore(
            path.join(self.datadir, "shares"))

    def setUp(self):
        super(ClusterFixture, self).setUp()
        # Only destroy the cluster if we create it...
        if not self.exists:
            # ... unless we've been asked to preserve it.
            if not self.preserve:
                self.addCleanup(self.destroy)
            self.create()
        self.addCleanup(self.stop)
        self.start()
        self.addCleanup(self.shares.release)
        self.shares.acquire()

    def createdb(self, name):
        """Create the named database if it does not exist already.

        Arranges to drop the named database during clean-up, unless `preserve`
        has been specified.
        """
        if name not in self.databases:
            super(ClusterFixture, self).createdb(name)
            if not self.preserve:
                self.addCleanup(self.dropdb, name)

    def dropdb(self, name):
        """Drop the named database if it exists."""
        if name in self.databases:
            super(ClusterFixture, self).dropdb(name)

    def stop(self):
        """Stop the cluster, but only if there are no other users."""
        if not self.shares.locked:
            super(ClusterFixture, self).stop()

    def destroy(self):
        """Destroy the cluster, but only if there are no other users."""
        if not self.shares.locked:
            super(ClusterFixture, self).destroy()
