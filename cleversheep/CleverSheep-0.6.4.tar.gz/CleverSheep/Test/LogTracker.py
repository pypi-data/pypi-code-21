"""Test support for tracking log files.

This is a thin layer around the `Log.FileTracker`, which ties into the test
framework, by using the PollManager to regularly check tracked files.

"""



from CleverSheep.Prog.Aspects import intelliprop
from CleverSheep.Log import FileTracker


NEW_DATA = FileTracker.NEW_DATA
RESTART = FileTracker.RESTART
ORIG_DATA = FileTracker.ORIG_DATA
NO_FILE = FileTracker.NO_FILE


class LogTracker(FileTracker.FileTracker):
    """An automatic log file tracker.

    This provides a file tracker that is customised to be used in test scripts.
    Basically this means that:

    - It requires a `Test.PollManager.PollManeger` instance so that
      it can automatically schedule itself to poll its log file.

    - It provides the basic hooks for converting file content into events
      and writing them to the test event store.

    The name LogTracker was chosen on the basis that in test scenarios,
    we are typically interested in log files.

    """
    def __init__(self, poll, path, readAll=False, pollInterval=0.02):
        """Constructor:

        :Parameters:
          path
            The path of the the file to track.
          readAll
            Set this to True if you want to read all the content of the
            file, not just what is added after this tracker is created.
          pollInterval
            The approximate inerval between checking for new input
            being added to the file. Defaults to 0.02 seconds.
          
        """
        super(LogTracker, self).__init__(path, readAll=readAll)
        self._poll = poll
        self._pollInterval = pollInterval
        self._poll.addRepeatingTimeout(self._pollInterval, self._read)
        self._buf = []
        self._onRead = self.onRead

    def _read(self):
        """Invoked by timer to read any new input.

        This buffers the new data. If the file has been restarted then
        all old buffered data is discarded. Whenever new data is added to the
        buffer the onRead method is invoked.

        """
        code, text = self.read()
        if (code, text) == (NEW_DATA, None) or code == NO_FILE:
            return
        if code == FileTracker.RESTART:
            self._buf = []
            self._onRead(code)
        if text:
            self._buf.append(text)
            self._onRead(code)

    def onRead(self, code):
        """Invoked when new data is read.

        This should be overriden in a derived class. The derived method
        can use the `buf` property to get all the buffered data as a string.
        It should set the `buf` property with any unconsumed part of the
        string.

        :Parameters:
          code
            The code returned from the `read`.
        
        """

    @intelliprop
    def buf(self, value=None):
        """The current input buffer as a string.

        This can be set to modify the buffer's contents.

        """
        if value is not None:
            if not value:
                self._buf[:] = []
            else:
                self._buf[:] = [value]
        else:
            if not self._buf:
                return ""
            if len(self._buf) > 1:
                self._buf[:] = ["".join(self._buf)]
            return self._buf[0]


class LineLogTracker(LogTracker):
    """An automatic log file tracker, which reads whole lines.

    """
    def __init__(self, *args, **kwargs):
        super(LineLogTracker, self).__init__(*args, **kwargs)
        self.lines = []
        self._onRead = self._doOnRead

    def _doOnRead(self, code):
        """Invoked to process new input.

        This buffers the new data then splits it into lines and stores the
        lines.

        """
        if code == RESTART:
            self.lines = []
        text, rem = self.buf, ""
        whole_lines = text.endswith("\n")
        lines = text.splitlines()
        if lines and not whole_lines:
             rem = lines.pop()
        self.lines.extend(lines)
        self.buf = rem
        self.onRead(code)
