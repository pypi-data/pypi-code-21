# Copyright 2017 Lowell Alleman, Yalei Du
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
""" logger.py:  A smart replacement for the standard TimedRotatingFileHandler.

ConcurrentTimeRotatingFileHandler:


See the README file for an example usage of this module.

This module supports Python 2.6 and later.

"""


import os
import re
import sys
import time
from logging import Handler, LogRecord
from logging.handlers import BaseRotatingHandler

try:
    import codecs
except ImportError:
    codecs = None
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

# Question/TODO: Should we have a fallback mode if we can't load portalocker /
# we should still be better off than with the standard RotattingFileHandler
# class, right? We do some rename checking... that should prevent some file
# clobbering that the builtin class allows.

# sibling module than handles all the ugly platform-specific details of file locking
from portalocker import lock, unlock, LOCK_EX, LOCK_NB, LockException


# Workaround for handleError() in Python 2.7+ where record is written to stderr
class NullLogRecord(LogRecord):
    def __init__(self):
        pass

    def __getattr__(self, attr):
        return None


class ConcurrentTimeRotatingFileHandler(BaseRotatingHandler):
    """
    Handler for logging to a set of files, which switches from one file to the
    next when the current file reaches a certain size. Multiple processes can
    write to the log file concurrently, but this may mean that the file will
    exceed the given size.
    """
    def __init__(self, filename, mode='a', when='h', backupCount=0, utc=False,
                 encoding=None, debug=True, delay=0, **kwargs):
        """
        Open the specified file and use it as the stream for logging.

        By default, the file grows indefinitely. You can specify particular
        values of maxBytes and backupCount to allow the file to rollover at
        a predetermined size.

        Rollover occurs whenever the current log file is nearly maxBytes in
        length. If backupCount is >= 1, the system will successively create
        new files with the same pathname as the base file, but with extensions
        ".1", ".2" etc. appended to it. For example, with a backupCount of 5
        and a base file name of "app.log", you would get "app.log",
        "app.log.1", "app.log.2", ... through to "app.log.5". The file being
        written to is always "app.log" - when it gets filled up, it is closed
        and renamed to "app.log.1", and if files "app.log.1", "app.log.2" etc.
        exist, then they are renamed to "app.log.2", "app.log.3" etc.
        respectively.

        If maxBytes is zero, rollover never occurs.

        On Windows, it is not possible to rename a file that is currently opened
        by another process.  This means that it is not possible to rotate the
        log files if multiple processes is using the same log file.  In this
        case, the current log file will continue to grow until the rotation can
        be completed successfully.  In order for rotation to be possible, all of
        the other processes need to close the file first.  A mechanism, called
        "degraded" mode, has been created for this scenario.  In degraded mode,
        the log file is closed after each log message is written.  So once all
        processes have entered degraded mode, the net rotation attempt should
        be successful and then normal logging can be resumed.  Using the 'delay'
        parameter may help reduce contention in some usage patterns.

        This log handler assumes that all concurrent processes logging to a
        single file will are using only this class, and that the exact same
        parameters are provided to each instance of this class.  If, for
        example, two different processes are using this class, but with
        different values for 'maxBytes' or 'backupCount', then odd behavior is
        expected. The same is true if this class is used by one application, but
        the RotatingFileHandler is used by another.
        """
        # Absolute file name handling done by FileHandler since Python 2.5
        BaseRotatingHandler.__init__(self, filename, mode, encoding, delay)
        self.delay = delay
        self._rotateFailed = False
        self.when = when.upper()
        if self.when == 'S':
            self.interval = 1 # one second
            self.suffix = "%Y-%m-%d_%H-%M-%S"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$"
        elif self.when == 'M':
            self.interval = 60 # one minute
            self.suffix = "%Y-%m-%d_%H-%M"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}$"
        elif self.when == 'H':
            self.interval = 60 * 60 # one hour
            self.suffix = "%Y-%m-%d_%H"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}_\d{2}$"
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24 # one day
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}$"
        elif self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7 # one week
            if len(self.when) != 2:
                raise ValueError("You must specify a day for weekly rollover from 0 to 6 (0 is Monday): %s" % self.when)
            if self.when[1] < '0' or self.when[1] > '6':
                raise ValueError("Invalid day specified for weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
            self.suffix = "%Y-%m-%d"
            self.extMatch = r"^\d{4}-\d{2}-\d{2}$"
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)
        self.extMatch = re.compile(self.extMatch)
        self.backupCount = backupCount
        self.utc = utc
        if utc:
            self._get_time = lambda: time.strftime(self.suffix, time.gmtime())
        else:
            self._get_time = lambda: time.strftime(self.suffix, time.localtime())
        self.time = self._get_time()
        self._open_lockfile()
        # For debug mode, swap out the "_degrade()" method with a more a verbose one.
        if debug:
            self._degrade = self._degrade_debug
        self.callback = kwargs.get('callback', None)

    def _get_time(self):
        if self.utc:
            return time.strftime(self.suffix, time.gmtime())
        else:
            return time.strftime(self.suffix, time.localtime())

    def _open_lockfile(self):
        # Use 'file.lock' and not 'file.log.lock' (Only handles the normal "*.log" case.)
        folder, logfile = os.path.split(self.baseFilename.lstrip('.log'))
        lock_file = os.path.join(folder, '.' + logfile + '.lock')
        self.stream_lock = open(lock_file,"w")

    def _open(self, mode=None):
        """
        Open the current base file with the (original) mode and encoding.
        Return the resulting stream.

        Note:  Copied from stdlib.  Added option to override 'mode'
        """
        if mode is None:
            mode = self.mode
        if self.encoding is None:
            stream = open(self.baseFilename, mode)
        else:
            stream = codecs.open(self.baseFilename, mode, self.encoding)
        return stream

    def _close(self):
        """ Close file stream.  Unlike close(), we don't tear anything down, we
        expect the log to be re-opened after rotation."""
        if self.stream:
            try:
                if not self.stream.closed:
                    # Flushing probably isn't technically necessary, but it feels right
                    self.stream.flush()
                    self.stream.close()
            finally:
                self.stream = None

    def acquire(self):
        """ Acquire thread and file locks.  Re-opening log for 'degraded' mode.
        """
        # handle thread lock
        Handler.acquire(self)
        # Issue a file lock.  (This is inefficient for multiple active threads
        # within a single process. But if you're worried about high-performance,
        # you probably aren't using this log handler.)
        if self.stream_lock:
            # If stream_lock=None, then assume close() was called or something
            # else weird and ignore all file-level locks.
            if self.stream_lock.closed:
                # Daemonization can close all open file descriptors, see
                # https://bugzilla.redhat.com/show_bug.cgi?id=952929
                # Try opening the lock file again.  Should we warn() here?!?
                try:
                    self._open_lockfile()
                except Exception:
                    self.handleError(NullLogRecord())
                    # Don't try to open the stream lock again
                    self.stream_lock = None
                    return
            lock(self.stream_lock, LOCK_EX)
        # Stream will be opened as part by FileHandler.emit()

    def release(self):
        """ Release file and thread locks. If in 'degraded' mode, close the
        stream to reduce contention until the log files can be rotated. """
        try:
            if self._rotateFailed:
                self._close()
        except Exception:
            self.handleError(NullLogRecord())
        finally:
            try:
                if self.stream_lock and not self.stream_lock.closed:
                    unlock(self.stream_lock)
            except Exception:
                self.handleError(NullLogRecord())
            finally:
                # release thread lock
                Handler.release(self)

    def close(self):
        """
        Close log stream and stream_lock. """
        try:
            self._close()
            if not self.stream_lock.closed:
                self.stream_lock.close()
        finally:
            self.stream_lock = None
            Handler.close(self)

    def _degrade(self, degrade, msg, *args):
        """ Set degrade mode or not.  Ignore msg. """
        self._rotateFailed = degrade
        del msg, args   # avoid pychecker warnings

    def _degrade_debug(self, degrade, msg, *args):
        """ A more colorful version of _degade(). (This is enabled by passing
        "debug=True" at initialization).
        """
        if degrade:
            if not self._rotateFailed:
                sys.stderr.write("Degrade mode - ENTERING - (pid=%d)  %s\n" %
                                 (os.getpid(), msg % args))
                self._rotateFailed = True
        else:
            if self._rotateFailed:
                sys.stderr.write("Degrade mode - EXITING  - (pid=%d)   %s\n" %
                                 (os.getpid(), msg % args))
                self._rotateFailed = False

    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.

        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        result.sort()
        if len(result) < self.backupCount:
            result = []
        else:
            result = result[:len(result) - self.backupCount]
        return result

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        self._close()
        if self.backupCount <= 0:
            # Don't keep any backups, just overwrite the existing backup file
            # Locking doesn't much matter here; since we are overwriting it anyway
            self.stream = self._open("w")
            return
        try:
            # Determine if we can rename the log file or not. Windows refuses to
            # rename an open file, Unix is inode base so it doesn't care.

            # Attempt to rename logfile to tempname:  There is a slight race-condition here, but it seems unavoidable
            try:
                # Do a rename test to determine if we can successfully rename the log file
                tmpname = "%s.%s" % (self.baseFilename, self.time)
                if not os.path.exists(tmpname):
                    os.rename(self.baseFilename, tmpname)
            except (IOError, OSError):
                exc_value = sys.exc_info()[1]
                self._degrade(True, "rename failed.  File in use?  "
                              "exception=%s", exc_value)
                return

            # Q: Is there some way to protect this code from a KeboardInterupt?
            # This isn't necessarily a data loss issue, but it certainly does
            # break the rotation process during stress testing.

            # There is currently no mechanism in place to handle the situation
            # where one of these log files cannot be renamed. (Example, user
            # opens "logfile.3" in notepad); we could test rename each file, but
            # nobody's complained about this being an issue; so the additional
            # code complexity isn't warranted.
            if self.backupCount > 0:
                for s in self.getFilesToDelete():
                    os.remove(s)
            #print "%s -> %s" % (self.baseFilename, dfn)
            self._degrade(False, "Rotation completed")
        finally:
            # Re-open the output stream, but if "delay" is enabled then wait
            # until the next emit() call. This could reduce rename contention in
            # some usage patterns.
            self.time = self._get_time()
            if not self.delay:
                self.stream = self._open()

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        For those that are keeping track. This differs from the standard
        library's RotatingLogHandler class. Because there is no promise to keep
        the file size under maxBytes we ignore the length of the current record.
        """
        del record  # avoid pychecker warnings
        # Is stream is not yet open, skip rollover check. (Check will occur on
        # next message, after emit() calls _open())
        if self.stream is None:
            return False
        if self._shouldRollover():
            # If some other process already did the rollover (which is possible
            # on Unix) the file our stream may now be named "log.1", thus
            # triggering another rollover. Avoid this by closing and opening
            # "log" again.
            self._close()
            self.stream = self._open()
            return self._shouldRollover()
        return False

    def _shouldRollover(self):
        self.stream.seek(0, 2)
        if self._get_time() != self.time:
            return True
        self._degrade(False, "Rotation done or not needed at this time")
