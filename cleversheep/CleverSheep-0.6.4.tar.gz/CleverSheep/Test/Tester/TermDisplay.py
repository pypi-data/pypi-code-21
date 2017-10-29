"""Display module for basic terminal display.

This is the default module for test display output.

"""



import textwrap
import os

from CleverSheep.Test.Tester import Coordinator
from CleverSheep.Test.Tester import Core

from CleverSheep.Sys.Platform import platformType
from CleverSheep.Prog import Files
from CleverSheep.TTY_Utils import Colours
from CleverSheep.Test.Tester import Logging
from CleverSheep.TTY_Utils import StatusLine
from CleverSheep.Test.Tester import options, Tty


class Terminal(object):
    """Encapsulates the idea of a simple terminal.

    A terminal provides the minimal features for displaying textual output.
    You can do the following things:

    - Write one or more characters.
    - Move to the next line, as in the way a type writer's carriage return
      normally works; which in computer speak is CR/LF.

    A terminal has a number of rows and columns. When a new line is started,
    the top-most line is lost to make space for the new line. When the last
    character written was in the last column then:

    - The terminal scrolls up by a single line.
    - The next character is written in the first character position of the
      next line.

    The above defined behaviour is designed so that it can be implemented
    in practice for most terminal types. However, only terminals that act like
    default X terminals are supported.

    This class is designed to update an actual terminal. It does not attempt
    to model the full terminal state - it tracks little more than the current
    row and column.

    """
    def __init__(self, stdout, stderr):
        self.row = 0
        self.dims = (24, 80)
        self._rem = None
        self.stdout = stdout
        self.stderr = stderr
        self.lineCount = 0
        self.column = 0

    def write(self, s):
        lines = s.splitlines(True)
        if not lines:
            return
        lines, last = lines[:-1], lines[-1]
        for line in lines:
            self.stdout.write(line)
            self.lineCount += 1
            self.column = 0
        self.stdout.write(last)
        if last.endswith("\n"):
            self.lineCount += 1
            self.column = 0
        else:
            self.column += len(last)
        self.stdout.flush()

    def nl(self, count=1):
        if self.stdout.isatty():
            self.write("\n" * count)

    def __getattr__(self, name):
        return getattr(self.stdout, name)


_terminal = None

def getStdout():
    global _terminal

    tty = Coordinator.getServiceProvider("tty")
    if _terminal is not None:
        if tty.out is _terminal.stdout and tty.err is _terminal.stderr:
            return _terminal
    _terminal = Terminal(tty.out, tty.err)
    return _terminal


# Output streams for different purposes.
sTestSummary = Colours.ColourStream(getStdout, fg="magenta")
sFail = Colours.ColourStream(getStdout, fg="red", bold=True)
sSerious = Colours.ColourStream(getStdout, fg="red", bold=False)
sError = Colours.ColourStream(getStdout, fg="yellow", bg="red")
sWarning = Colours.ColourStream(getStdout, fg="red", bold=False)
sTitle = Colours.ColourStream(getStdout, bold=True)
sNormal = Colours.ColourStream(getStdout)
sConsole = Colours.ColourStream(getStdout, fg="blue")
sBold = Colours.ColourStream(getStdout, bold=True)
sFile = Colours.ColourStream(getStdout, fg="blue", bold=True)
sLineNum = Colours.ColourStream(getStdout, bold=True)
sFunc = Colours.ColourStream(getStdout, fg="magenta")
sCode = Colours.ColourStream(getStdout, fg="magenta")
sEmphCode = Colours.ColourStream(getStdout, fg="magenta", bold=True)
sPass = Colours.ColourStream(getStdout, bold=True)
sEmph = Colours.ColourStream(getStdout, fg="blue")
sFailDetail = Colours.ColourStream(getStdout, fg="blue")
if platformType == "windows":
    sEmph = Colours.ColourStream(getStdout, fg="blue", bold=True)
    sFailDetail = Colours.ColourStream(getStdout, fg="blue", bold=True)


class StateWriter(object):
    def __init__(self):
        self.writers = None

    def __getitem__(self, name):
        if self.writers is None:
            # Only those states that can be output for a run step are relevant
            # here as they seem to only be used when reporting the state of
            # each step as the tests run, not in the summary of failures for
            # example.

            self.writers = {}
            self.writers[Core.State.NOT_RUN] = sNormal
            self.writers[Core.State.PASS] = sPass
            self.writers[Core.State.FAIL] = sFail
            self.writers[Core.State.EXIT_SUITE] = sEmph
            self.writers[Core.State.EXIT_ALL] = sEmph
            self.writers[Core.State.USER_STOPPED] = sEmph
            self.writers[Core.State.SKIPPED] = sEmph
            self.writers[Core.State.BUG] = sEmph
            self.writers[Core.State.BUG_PASS] = sWarning
            self.writers[Core.State.TODO] = sWarning
            self.writers[Core.State.BAD_SETUP] = sFail

        return self.writers.get(name, sNormal)


#: This is used to map from a test state to the log stream used to print
#: the state.
stateWriter = StateWriter()


def _addPerLinePrefix(lines, prefix):
    return [prefix + l for l in lines]


# TODO: Duplicate from Manager.py
def addHang(lines, hangText):
    res = []
    pad = " " * len(hangText)
    for i, line in enumerate(lines):
        if i:
            res.append(pad + line)
        else:
            res.append(hangText + line)
    return res


def _addHang(lines, hangText):
    if not hangText:
        return lines
    a, b = lines[0], lines[1:]
    a = hangText + a
    b = _addPerLinePrefix(b, " " * len(hangText))
    return [a] + b



def _ifNotNullTest(func):
    def run(self, test, *args, **kwargs):
        if not test.amNull:
            return func(self, test, *args, **kwargs)
    return run


def _execOnly(func):
    def run(self, *args, **kwargs):
        if self.mode not in ("EXECUTION", "FAIL-SUMMARY"):
            return
        return func(self, *args, **kwargs)
    return run


def _messesStatus(func):
    def run(self, *args, **kwargs):
        self.status.kill()
        try:
            return func(self, *args, **kwargs)
        finally:
            self.status.update()
    return run


def _interactOnly(func):
    def run(self, *args, **kwargs):
        if self.mode not in ("EXECUTION", "FAIL-SUMMARY", "SUMMARY", "DETAILS",
                    "IDS-SUMMARY"):
            return
        return func(self, *args, **kwargs)
    return run


def _logExecOnly(func):
    def run(self, *args, **kwargs):
        if self.mode not in ("EXECUTION", "RUN-SUMMARY", "FAIL-SUMMARY"):
            return
        return func(self, *args, **kwargs)
    return run


class Reporter(object):
    """Interface for test reporting objects.

    This can act as a base class, but it also defines the interface that must
    be provided by test reporters. Basically the object must provide a number
    of methods:

    -- `enterSuite`(summary)
    -- `leaveSuite`(summary)
    -- `announceTestStart`(number, summary)
    -- `putResult`(state)
    -- `setCommentary`(text)
    -- `setDelayLeft`(seconds)
    -- `setProgress`(n, m)
    -- `setMode`(mode)

    """
    def __init__(self):
        self.level = 0
        self._columns = 80
        self.mode = "EXEC"

    def setField(self, name, s):
        pass

    def enterSuite(self, suite, state=None):
        """Announce a suite is being entered.

        A call to this will always be matched by a corresponding
        `leaveSuite`.

        """
        try:
            return self._announceSuiteStart(suite, state=state)
        finally:
            self.level += 1

    def leaveSuite(self, suite):
        """Announce a suite is being exited.

        This always matches a call to `enterSuite`.

        """
        self.level -= 1
        return self._announceSuiteEnd(suite.summary)

    def announceTestStart(self, test, number, state=None):
        """Announce a test is being started.

        This is invoked before any per-test set up is invoked.

        """

    def summariseResult(self, test):
        """Provide a summary of a test's state.

        """

    def summariseSuiteResult(self, suite):
        """Provide a summary of a suite's state.

        """

    def putResult(self, test, itemType=None):
        """Announce the state of the most recently run test.

        This is invoked before any per-test tear down.

        """
        pass

    def setCommentary(self, s):
        """Set the commentary line.

        This is invoked to allow an update of commentary part of a status line.

        """
        pass

    def setDelayLeft(self, rem):
        """Set the amount of time left when the framework is delaying.

        This is used to allow the reporter to update a delay countdown.

        """
        pass

    def setProgress(self, n, m):
        """Set the progress to ``n`` out of ``m`` tests.

        """
        pass

    def setMode(self, mode):
        """Set the current test execution mode.

        The framework defined a set of execution modes. Each has a mode string.
        TODO: List them, for example "summary".

        This method allows the reporter object to react differently to
        invocations of the other methods depending on the mode.

        """
        self.mode = mode
        self._setMode(mode)

    def _setMode(self, mode):
        pass

    @property
    def indent(self):
        return self.level * 2

    @property
    def pad(self):
        return " " * self.indent

    @property
    def columns(self):
        return self._columns

    def formatAnnouncement(self, summary, number=None, testID=None,
            addMargin=0, wrap=True, isLines=False, timeStr=""):
        """Format the announcement of a test/suite.

        For a test the number should be supplied, which will be added as
        hanging indent. The summary is formatted to fit within a suitable
        number of columns, allowing for the test number, level and addMargin.

        :Return:
            A typle of (list, textLen, dotLen). The list is the set of
            formatted lines. The textLen is the length of the last line. The
            dotLen is the number of dots to add to the last line.

        """
        annSpace = 19
        columns = self.columns - addMargin - len(self.pad) - annSpace
        leader = ""
        if number:
            leader = "%-4d: " % number
            columns -= len(leader)

        if testID is not None:
            summary = "[%s] %s" % (testID, summary)
        if not isLines:
            summary = timeStr + summary
        if wrap:
            lines = textwrap.wrap(summary, columns - 1)
            dotLen = columns - len(lines[-1]) - 1
            lines = _addHang(lines, leader)
            lines = _addPerLinePrefix(lines, self.pad)
            textLen = len(lines[-1])
        else:
            dotLen = 0
            if isLines:
                lines = summary
            else:
                lines = [summary]
            lines = _addHang(lines, leader)
            lines = _addPerLinePrefix(lines, self.pad)
            textLen = len(lines[0])

        return lines, textLen, dotLen

    def _announceSuiteEnd(self, summary):
        pass


class FileLikeReporter(Reporter):
    """A reporter that can be used as a file.

    This is normally TODO.

    """
    def __init__(self):
        Reporter.__init__(self)
        self._pendingIndent = True
        self._columns = 80

    def _write(self, s):
        pass

    def write(self, s, indent_lines=True):
        self.writelines(s.splitlines(True), indent_lines)

    def writelines(self, lines, indent_lines=True):
        if not lines:
            return
        pad = self.ind
        lines = list(lines)
        if indent_lines:
            if self._pendingIndent:
                lines[0] = pad + lines[0]
            lines[1:] = [pad + l for l in lines[1:]]
            self._pendingIndent = lines[-1][-1] == '\n'
        self._write("".join(lines))


class LogReporter(FileLikeReporter):
    def __init__(self, *args, **kwargs):
        super(LogReporter, self).__init__(*args, **kwargs)
        self._extraPad = 0

    def _cleanText(self, s):
        lines = s.splitlines()
        return lines

    def _log(self, dest, fmt, args):
        logger = getattr(Logging.coreLog, dest)
        try:
            msg = fmt % args
        except TypeError:
            msg = "%s, %r" % (fmt, args)
        lines = self._cleanText(msg)
        prefix = self.pad + (" " * self._extraPad)
        lines = ["%s%s" % (prefix, m) for m in lines]
        msg = "\n".join(lines)
        if msg.strip():
            logger("%s", msg)

    def fatal(self, fmt, *args):
        return self._log("fatal", fmt, args)

    def critical(self, fmt, *args):
        return self._log("critical", fmt, args)

    def error(self, fmt, *args):
        return self._log("error", fmt, args)

    def warning(self, fmt, *args):
        return self._log("warning", fmt, args)

    def warn(self, fmt, *args):
        return self._log("warn", fmt, args)

    def info(self, fmt, *args):
        return self._log("info", fmt, args)

    def debug(self, fmt, *args):
        return self._log("debug", fmt, args)

    def _write(self, s):
        lines = self._cleanText(s)
        if not lines:
            return
        Logging.coreLog.info("%s", "\n".join(lines))

    def _announceItem(self, number=None, summary="", testID=None,
            itemType="Test"):
        typ = "%s:" % itemType
        prefix = ("%-6s " % typ)
        lines, textLen, dotLen = self.formatAnnouncement(summary,
                number=number, addMargin=len(prefix), testID=testID)
        lines = _addHang(lines, prefix)

        writer = Logging.coreLog.info
        writer("%s", "\n".join(lines))

    def _announceItemResult(self, number=None, summary="", testID=None,
            itemType="Test", state=None):
        typ = "%s:" % itemType.capitalize()
        prefix = ("%-6s " % typ)
        lines, textLen, dotLen = self.formatAnnouncement(summary,
                number=number, testID=testID, addMargin=len(prefix))
        lines = _addHang(lines, prefix)

        text = "\n".join(lines)
        writer = Logging.coreLog.info
        writer("%s%s%19s", text, "." * dotLen, state)

    def _announceItemResult2(self, item):
        typ = "%s:" % item.typeName
        state = item.state
        prefix = ("%-6s " % typ)
        try:
            testID = item.testID
        except AttributeError:
            testID = None
        lines, textLen, dotLen = self.formatAnnouncement(item.summary,
                number=item.number, addMargin=len(prefix), testID=testID)
        lines = _addHang(lines, prefix)

        text = "\n".join(lines)
        writer = Logging.coreLog.info
        writer("%s%s%19s", text, "." * dotLen, state)

    @_logExecOnly
    def _announceSuiteStart(self, suite, state=None):
        if state is not None:
            self._announceItemResult(summary=suite.summary, itemType="Suite",
                                     state=state)
        else:
            self._announceItem(summary=suite.summary, itemType="Suite")

    @_logExecOnly
    def announceTestStart(self, test, number, state=None):
        if test.number <= 0:
            return
        if state:
            self._announceItemResult(summary=test.summary, number=number,
                                     testID=test.testID, itemType="Test",
                                     state=state)
        else:
            if number > 0:
                self._announceItem(number=number, summary=test.summary,
                                   itemType="Test", testID=test.testID)
                self._extraPad = 13  # TODO: Messy!

    def summariseSuiteResult(self, suite):
        """Provide a summary of a suite's state.

        """
        state = suite.state
        self._announceItemResult2(suite)
        self.level += 1

    def summariseResult(self, test):
        """Provide a summary of a test's state."""
        assert not test.isSuite
        self._announceItemResult2(test)

    @_logExecOnly
    def putResult(self, test, itemType="Test"):
        # Add details to the log.
        if test.hasFailed:
            writer = Logging.coreLog.error
        else:
            writer = Logging.coreLog.info
        typ = "%s:" % itemType
        ePad = " " * 6
        writer("%-6s %s%s%s", typ, self.pad, ePad, test.state)
        self._extraPad = 7  # TODO: Messy!

    @property
    def ind(self):
        if self.mode in ("RUN-SUMMARY", "FAIL-SUMMARY", "NO_ACTION"):
            return ""
        return self.pad + "             "

    def _logFailException(self, exc):
        stack = exc.stack
        lines = []

        if exc.message:
            if not isinstance(exc.message, basestring):
                raise SyntaxError("Make sure the error message in your fail"
                                  " call is a string")
            ll = ["%s%s" % (self.ind, l) for l in exc.message.splitlines()]
        else:
            ll = ["%s%s" % (self.ind, l) for l in str(exc).splitlines()]
        lines.extend(ll)
        for i, x in enumerate(stack):
            try:
                path, lnum, funcName, context, lineIdx, meta = x
            except ValueError:
                path, lnum, funcName, context, lineIdx = x
                meta = ()
            lines.append("%s%s: %s" % (self.ind, Files.relName(path),
                funcName))
            self._logStackFrame(path, lnum, funcName, context, lineIdx, meta,
                    showContext=(i == 0) or (i == len(stack) - 1),
                    lines=lines)
        Logging.coreLog.error("%s", "\n".join(lines))
        return

        # When using the RPC module, the original exception may have the
        # remote-end traceback attached as ``_rpcTraceBack``. If so, now is the
        # time to write it.
        if hasattr(exc, "origExc"):
            if hasattr(exc.origExc, "_rpcTraceBack"):
                sNormal.write("\nRemote Traceback:\n")
                for l in exc.origExc._rpcTraceBack.splitlines():
                    sNormal.write("  %s\n" % l)

    def _logStackFrame(self, path, lnum, funcName, context, lineIdx, meta,
            showContext=False, lines=None):
        lines = lines or None
        if not showContext or not context:
            if not context:
                lines.append("%s   %-4d: <no context>" % (self.ind, lnum,))
            else:
                l = context[lineIdx].rstrip()
                if l.strip():
                    lines.append("%s   %-4d: %s" % (self.ind, lnum, l))
                else:
                    lines.append("%s   %-4d:" % (self.ind, lnum, ))
            return

        for i, line in enumerate(context):
            ci = i + lnum - lineIdx
            l = line.rstrip()
            if i == lineIdx:
                lines.append("%s==>%-4d: %s" % (self.ind, ci, l))
            else:
                if l.strip():
                    lines.append("%s   %-4d: %s" % (self.ind, ci, line.rstrip()))
                else: #pragma: unreachable
                    lines.append("%s   %-4d:" % (self.ind, ci, ))
        #Logging.coreLog.error("%s", "\n".join(lines))

    def logStage(self, test, op, msg):
        phaseRecord = test.getStepRecord(op)
        if phaseRecord is None or not phaseRecord.hasFailed:
            return
        Logging.coreLog.error("%s%s", self.ind, msg)
        if phaseRecord.exc:
            self._logFailException(phaseRecord.exc)

    def setLogPath(self, path):
        Logging.setLogPath(path)

    def set_columns(self, c):
        Logging.set_columns(c)

    def start(self):
        Logging.start()

    def setLogLevel(self, level):
        # TODO: Not right to poke the Logging module.
        Logging.setLevel(level)

    def startTestRun(self):
        pass

    def stopTestRun(self):
        pass

    def switchToTest(self, test, parentSkip=False):
        pass

    def leaveTest(self, test):
        pass

    # TODO: Hacky. Remove and provide all required methods/attrs.
    def __getattr__(self, name):
        return getattr(Logging, name)


# TODO: Rename to something more descriptive.
# TODO: Only use this if sys.stdout is a TTY at startup.
class Screen(FileLikeReporter):
    """A reporter to produce clean terminal based output."""

    def __init__(self):
        super(Screen, self).__init__()
        self.rightPos = 0

        # Create a status line. Be careful to keep it OK for an 80 column
        # display.
        self.status = status = StatusLine.Status(startActive=False)
        status.setTerm(Tty.out)
        status.addSpinner()
        status.addLeftField("progress", 7)
        status.addLeftField("commentary", None)
        status.addRightField("delay", 8)

    @property
    def columns(self):
        return sConsole.columns

    def setField(self, name, s):
        self.status.setField(name, s)

    # TODO: Obsolete
    def start(self):
        self.status.start()

    # TODO: Obsolete
    def stop(self):
        self.status.stop()

    def update(self):
        self.status.update()

    def write(self, s):
        if self.mode in ("RUN-SUMMARY", "NO_ACTION"):
            return
        return super(Screen, self).write(s)

    @_messesStatus
    def _write(self, s):
        sConsole.write(s)

    @property
    def ind(self):
        if self.mode in ("EXECUTION",):
            return self.pad + "      "
        return ""

    def startTestRun(self):
        pass

    def stopTestRun(self):
        pass

    def switchToTest(self, test, parentSkip=False):
        self.status.start()

    def leaveTest(self, test):
        self.status.stop()

    def _announceItem(self, number=None, summary="", term="\n",
            testID=None, itemType="Test", stream=sNormal, wrap=True,
            uline="", prefix="", timeStr=""):
        lines, textLen, dotLen = self.formatAnnouncement(summary,
                number=number, testID=testID, wrap=wrap, timeStr=timeStr)
        text = "\n".join(lines)
        self.status.kill()

        writer = stream.write
        writer("%s%s" % (prefix, text))
        writer(term)
        if uline:
            pad = len(text) - len(text.strip())
            tt = uline * (textLen - pad)
            writer("%*s%s\n" % (pad, "", tt, ))

        self.rightPos = textLen + dotLen

        return dotLen

    def _writeDetails(self, details, stream=sNormal, ind="  "):
        if not details:
            return
        lines, textLen, dotLen = self.formatAnnouncement(details,
                wrap=False, isLines=True)
        for line in lines:
            stream.write("%s%s\n" % (ind, line))
        if details:
            sNormal.write("\n")

    def summariseSuiteResult(self, suite):
        """Provide a summary of a suite's state.

        """
        try:
            if self.mode not in ["FAIL-SUMMARY"]:
                return
            state = suite.state
            lines, textLen, dotLen = self.formatAnnouncement(suite.summary)
            text = "\n".join(lines)
            writer = sNormal.write
            writer("%s%s%19s\n" % (text, "." * dotLen, state))
        finally:
            self.level += 1

    def summariseResult(self, test):
        """Provide a summary of a test's state.

        """
        assert not test.isSuite
        if self.mode not in ["FAIL-SUMMARY"]:
            return
        state = test.state
        lines, textLen, dotLen = self.formatAnnouncement(
            test.summary, number=test.number, testID=test.testID)
        text = "\n".join(lines)
        writer = sNormal.write
        writer("%s%s%19s\n" % (text, "." * dotLen, state))

    def _announceItemResult(self, number=None, summary="", testID=None,
                            itemType="Test", state=None):
        lines, textLen, dotLen = self.formatAnnouncement(summary,
                number=number, testID=testID)
        text = "\n".join(lines)
        writer = sNormal.write
        writer("%s%s%12s\n" % (text, "." * dotLen, state.altName))

    @_interactOnly
    def _announceSuiteStart(self, suite, state=None):
        self.status.kill()
        if self.mode == "DETAILS":
            if self.level:
                sNormal.write("\n")
            self._announceItem(summary=suite.summary, stream=sTitle,
                    wrap=False, uline="=")
            sNormal.write("\n")
            self._writeDetails(suite.details, stream=sNormal)
        elif state is not None:
            self._announceItemResult(summary=suite.summary, state=state)
        elif self.mode == "IDS-SUMMARY":
            if self.level == 0:
                sNormal.write("(\n")
            self._announceItem(summary=suite.summary, wrap=False,
                    prefix="  # ")
        else:
            stream = sNormal
            self._announceItem(summary=suite.summary, term="")
            stream.write("\n")
        self.status.update()

    def _announceSuiteEnd(self, summary):
        if self.mode == "IDS-SUMMARY":
            if self.level == 0:
                sNormal.write(")\n")

    @_ifNotNullTest
    @_messesStatus
    @_interactOnly
    def announceTestStart(self, test, number, eol=True, state=None):
        if self.mode == "DETAILS":
            dotLen = self._announceItem(number=number, summary=test.summary,
                    testID=test.testID, term="", stream=sTitle)
            sNormal.write("\n")
            if test.details:
                sNormal.write("\n")
                self._writeDetails(test.details, stream=sNormal, ind="      ")
            else:
                sNormal.write("\n")

            ind = "          "
            didSteps = False
            spec = test.getTestProcedure()
            # TODO: Code largely duplicated in sphinx.py.
            prefixLens = [0] * 30
            for n, block, boundArgs in spec.walkSteps():
                num = ".".join("%d" % v for v in n) + ". "
                idx = len(n)
                prefixLens[idx] = max(len(num), prefixLens[idx])

            for n, block, boundArgs in spec.walkSteps():
                nn = len(n)
                a, b = prefixLens[nn - 1:nn + 1]
                b -= a
                if n[-1] == 0:
                    if n[0] == 0:
                        sNormal.write("\n%-*sSetup\n" % (a, "1. "))
                        n[0] += 1
                sNormal.write("\n")

                num = ".".join("%d" % v for v in n) + ". "
                hangStr = "%*s%-*s" % (a, "", b, num)
                for line in addHang(block, hangStr):
                    sNormal.write("%s      %s\n" % (ind, line))
                didSteps = True

            if didSteps:
                sNormal.write("\n")

            sEmph.write("%s      Path:     %s\n" % (self.pad, test.path))
            if test.klass:
                sEmph.write("%s      Class:    %s\n" % (self.pad, test.klass))
            sEmph.write("%s      Function: %s\n" % (self.pad, test.funcName))
            sNormal.write("\n")

        elif self.mode == "IDS-SUMMARY":
            dotLen = self._announceItem(number=number, summary=test.summary,
                    testID=test.testID, wrap=False, prefix="  # ")
            sNormal.write("  %s        %s,\n" % (self.pad, test.uid))

        elif state is not None:
            self._announceItemResult(summary=test.summary, state=state,
                                     number=number, testID=test.testID)

        else:
            self.currTest = test, number
            stream = sNormal
            if number > 0:
                timeStr = getattr(test, "execTime", "")
                dotLen = self._announceItem(number=number, summary=test.summary,
                        testID=test.testID, term="", timeStr=timeStr)
                self.annLine = sNormal.terminal.lineCount
                if self.mode not in ("RUN-SUMMARY", "SUMMARY", "DETAILS",
                            "xIDS-SUMMARY"):
                    stream.write("." * dotLen)
                    if eol:
                        stream.terminal.nl()
                else:
                    stream.write("\n")

    @_ifNotNullTest
    @_messesStatus
    @_execOnly
    def putResult(self, test, itemType=None):
        stream = sNormal
        stream.terminal.flush()
        if stream.terminal.column > 0:
            stream.terminal.nl()
        annLine = stream.terminal.lineCount
        if annLine - self.annLine >= 10:
            self.announceTestStart(*self.currTest, eol=False)
        stream.terminal.sol()
        stream.terminal.up(annLine - self.annLine)
        stream.terminal.right(self.rightPos)
        state = test.state
        if test.number > 0:
            stateWriter[state].write("%19s\n" % state.altName)
        stream.terminal.nl(annLine - self.annLine - 1)

    def logStage(self, test, op, msg):
        if options.get_option_value("quiet"):
            return
        phaseRecord = test.getStepRecord(op)
        if phaseRecord is None or not phaseRecord.hasFailed:
            return

        sNormal.write(self.ind)
        sError.write(msg)
        if phaseRecord.exc:
            self._logFailException(phaseRecord.exc)

    def _logFailException(self, exc):
        from CleverSheep.Test import Tester
        if options.get_option_value("quiet"):
            return
        stack = exc.stack
        ll = ["%s%s" % (self.ind, l) for l in str(exc).splitlines()]
        sFailDetail.write("%s\n" % ("\n".join(ll)))
        root = Tester.execDir
        for i, x in enumerate(stack):
            try:
                path, lnum, funcName, context, lineIdx, meta = x
            except ValueError:
                path, lnum, funcName, context, lineIdx = x
                meta = ()
            if meta:
                continue
            if not os.path.isabs(path):
                path = os.path.join(root, path)
            sFile.write("%s%s" % (self.ind, Files.relName(path, root)))
            sNormal.write(": ")
            sFunc.write("%s\n" % funcName)
            self._logStackFrame(path, lnum, funcName, context, lineIdx, meta,
                    showContext=(i == 0) or (i == len(stack) - 1))

        # When using the RPC module, the original exception may have the
        # remote-end traceback attached as ``_rpcTraceBack``. If so, now is the
        # time to write it.
        if hasattr(exc, "origExc"):
            if hasattr(exc.origExc, "_rpcTraceBack"):
                sNormal.write("\nRemote Traceback:\n")
                for l in exc.origExc._rpcTraceBack.splitlines():
                    sNormal.write("  %s\n" % l)

    def _logStackFrame(self, path, lnum, funcName, context, lineIdx, meta,
            showContext=False):
        if not showContext or not context:
            if not context:
                sCode.write("%s   %-4d: <no context>\n" % (self.ind, lnum,))
            else:
                l = context[lineIdx].rstrip()
                if l.strip():
                    sCode.write("%s   %-4d: %s\n" % (self.ind, lnum, l))
                else:
                    sCode.write("%s   %-4d:\n" % (self.ind, lnum, ))
            return

        for i, line in enumerate(context):
            ci = i + lnum - lineIdx
            l = line.rstrip()
            if i == lineIdx:
                sEmphCode.write("%s==>%-4d: %s\n" % (self.ind, ci, l))
            else:
                if l.strip():
                    sCode.write("%s   %-4d: %s\n" % (self.ind, ci, line.rstrip()))
                else: #pragma: unreachable
                    sCode.write("%s   %-4d:\n" % (self.ind, ci, ))


logger = LogReporter()
screen = Screen()

Coordinator.registerProvider("cscore", ("logging", ), logger)
Coordinator.registerProvider("cscore", ("status", ), screen)
Coordinator.registerProvider("cscore", ("reporter", ), screen)

