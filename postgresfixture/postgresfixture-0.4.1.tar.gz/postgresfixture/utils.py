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
    "LockFile",
    "LockAlreadyTaken",
]

from contextlib import contextmanager
from fcntl import (
    LOCK_EX,
    LOCK_SH,
    LOCK_UN,
    lockf,
    )
import io
import os
import threading


class LockFile:
    """A non-reentrant lock based on `lockf`."""

    def __init__(self, path):
        super(LockFile, self).__init__()
        self._lock = threading.Lock()
        self._path = path

    @property
    def exclusive(self):
        """A context manager for an exclusive lock."""
        return self._take(LOCK_EX)

    @property
    def shared(self):
        """A context manager for a shared lock."""
        return self._take(LOCK_SH)

    @property
    def path(self):
        """The filesystem path to the lock file."""
        return self._path

    @contextmanager
    def _take(self, mode):
        if self._lock.acquire(False):
            try:
                # Open with os.open() so that we create the file even when
                # opening read-only, using O_CREAT. Then we have to do a
                # little dance with io.open for lockf's benefit.
                oflag = os.O_RDWR if mode == LOCK_EX else os.O_RDONLY
                fileno = os.open(self._path, os.O_CREAT | oflag, 0o600)
                fmode = "ab" if mode == LOCK_EX else "rb"
                with io.open(fileno, fmode) as handle:
                    lockf(handle, mode)
                    try:
                        yield
                    finally:
                        lockf(handle, LOCK_UN)
            finally:
                self._lock.release()
        else:
            raise LockAlreadyTaken(self)


class LockAlreadyTaken(Exception):
    """A lock has already been taken."""

    def __init__(self, lock):
        super(LockAlreadyTaken, self).__init__(lock.path)
        self.lock = lock
