#!/usr/bin/env python
"""Module that supports automatic tracking of log file output.

"""
import os

NEW_DATA = 0
RESTART = 1
ORIG_DATA = 2
NO_FILE = 3


class FileTracker(object):
    """A class that helps follow a file as it is being written.

    Basically, this is like ``tail -f`` for python programs. You create one of
    these passing it the name of a file as the only argument. The file does not
    need to exist. Then you invoke the `read` method to get any data added to
    the file since the tracker was created.

    If the file is truncated or removed then the tracker will start delivering
    data from the start of the file; waiting for a new version of the file to
    be created if necessary. 
    """

    def __init__(self, path, readAll=False):
        """Constructor: See `FileTracker` for more details.
        
        :Param path:
            The path to the file to track.
        :Param readAll:
            Set this to True if you want to read all the content of the file,
            not just what is added after the tracker is created.
        """
        self.path = path
        self.ret = NEW_DATA
        try:
            self.size = os.path.getsize(self.path)
            if self.size > 0:
                self.ret = ORIG_DATA
        except os.error:
            self.size = 0
        if readAll:
            self.size = 0

    def read(self):
        """Read any newly arrived data.

        This tries to read all new data since the last time it was called.

        :Return:
            A tuple of (code, data). The data is as read from the file.
            The code can have any of the following values:

                NEW_DATA:
                  This is just new data.
                RESTART:
                  The file has been restarted, replaced or truncated, so this
                  data comes from the start of the file.
                ORIG_DATA:
                  This is the first read and the file was not initially empty.
                NO_FILE:
                  The file does not currently exist.

            If there is no new data then (NEW_DATA, None) is returned.

        """
        try:
            size = os.path.getsize(self.path)
        except os.error:
            # Looks like the file has been removed.
            if self.size > 0:
                self.ret = RESTART
            self.size = 0
            return NO_FILE, None

        if self.size == size:
            return NEW_DATA, None

        if size < self.size:
            # Treat truncation as if the file has been replaced by a smaller
            # version, which it probably has.
            if self.size > 0:
                self.ret = RESTART
            self.size = 0

        s = ""
        try:
            f = open(self.path, "rb", 0)
        except IOError: #pragma: no cover
            return NEW_DATA, None
        try:
            f.seek(self.size)

            if size != self.size:
                try:
                    s = f.read(size - self.size)
                except IOError:
                    # Can occur when files get (re)created quickly. Treat as no
                    # file.
                    return NO_FILE, None
                self.size = size

            r, self.ret = self.ret, NEW_DATA
            return r, s
        finally:
            f.close()
