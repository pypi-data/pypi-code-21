#!/usr/bin/env python
"""An non-displaying terminal emulator.

This is intended to be used for testing code that uses escape sequences to
provided fancy terminal output. Normally such code will write to stdout and
only do the fancy stuff if stdout advertises itself as a real TTY.

This modules provides a class TTY, which pretends to be a terminal, but allows
the details of what is currently displayed to be queried.

This implementation is only currently capable of, partially, emulating a simple
X terminal.

"""
from __future__ import print_function



import re
import sys
from functools import partial
from cStringIO import StringIO


# Define patterns for some well defined teminal control sequences.
sSetAttr1 = r'(\x1b)\[(\d+)m'
sNormal1 = r'(\x1b)\(B\x1b\[(m)'
sNormal2 = r'(\x1b)\[0;10(m)'
sNormal3 = r'(\x1b)\[(m)\x1b\(B'
rPat = re.compile('|'.join([sSetAttr1, sNormal1, sNormal2, sNormal3]))
rLine = re.compile(r'(\n\r|\n|\r)')


_fgMap = {
    30: "black", 31: "red", 32: "green", 33: "yellow",
    34: "blue", 35: "magenta", 36: "cyan", 37: "white",
}
_fgMap.update([(v, k) for k, v in _fgMap.iteritems()])

_bgMap = {
    "40": "black", "41": "red", "42": "green", "43": "yellow",
    "44": "blue", "45": "magenta", "46": "cyan", "47": "white",
}
_bgMap.update([(v, k) for k, v in _bgMap.iteritems()])


def _buildCStates(default, *actions):
    mm = []
    newState, handler = default
    for i in range(256):
        mm.append((handler, newState))
    for chars, newState, handler in actions:
        for c in chars:
            mm[ord(c)] = (handler, newState)
    return mm


class NoSpace(Exception):
    pass


class Attrs(object):
    """Ecapsulation of character cell attributes.

    """
    def __init__(self, *attrValues):
        self.reset()

    def reset(self):
        self.fg = Cell.black
        self.bg = Cell.white
        self.bold = False
        self.blink = False
        self.underline = False
        self.reverse = False

    # SMELL
    def set(self, attrValue):
        if 30 <= attrValue <= 37:
            self.fg = Cell._colcodeMap[attrValue - 30]
        elif 40 <= attrValue <= 47:
            self.bg = Cell._colcodeMap[attrValue - 40]
        elif attrValue == 1:
            self.bold = True
        elif attrValue == 4:
            self.underline = True
        elif attrValue == 5:
            self.blink = True
        elif attrValue == 7:
            self.reverse = True
        elif attrValue in (0, None):
            self.reset()

    @property
    def attrTuple(self):
        """The attributes as a human friendly tuple.

        """
        v = ["", "", ""]
        v[0] = self.fg
        v[1] = self.bg
        if self.bold:
            v[2] += "b"
        if self.underline:
            v[2] += "u"
        if self.blink:
            v[2] += "B"
        if self.reverse:
            v[2] += "r"
        return tuple(v)

    def copy(self):
        c = Attrs()
        c.fg= self.fg
        c.bg= self.bg
        c.bold = self.bold
        c.blink = self.blink
        c.underline = self.underline
        c.reverse = self.reverse
        return c


class Cell(object):
    black = intern("black")
    red = intern("red")
    green = intern("green")
    yellow = intern("yellow")
    blue = intern("blue")
    magenta = intern("magenta")
    cyan = intern("cyan")
    white = intern("white")
    _colcodeMap = {
        0: black, 1: red, 2: green, 3: yellow,
        4: blue, 5: magenta, 6: cyan, 7: white}
    _colcodeMap.update(dict((n, c) for c, n in _colcodeMap.iteritems()))

    def __init__(self):
        self.clear()

    def clear(self):
        self.c = None
        self.attrs = Attrs()

    def set(self, c, attrs):
        self.c = c
        self.attrs = attrs.copy()

    def fillSpace(self):
        """Fill with a space character unless already set.

        """
        if self.c is None:
            self.c = " "
            self.attrs = set()

    @property
    def attrTuple(self):
        """The cell attributes as a human friendly tuple.

        """
        return self.attrs.attrTuple

    def __nonzero__(self):
        """Test whether this cell is set.

        A cell is considered non-zero if the character value `c` has been set.

        """
        return self.c is not None


class Line(object):
    def __init__(self, maxLen):
        self.cells = [Cell() for c in range(maxLen)]
        self.col = 0

    def putChar(self, c, attrs):
        cell = self.cells[self.col]
        if cell.c is not None and cell is self.cells[-1]:
            raise NoSpace
        cell.set(c, attrs)
        if self.col < len(self.cells) - 1:
            self.col += 1
        for i in range(self.col):
            self.cells[i].fillSpace()

    def clear(self):
        """Completely emprty this lines.

        """
        self.col = 0
        self.clearToEol()

    def clearToEol(self):
        """Clear cells from cursor to end of line.

        """
        for cell in self.cells[self.col:]:
            cell.clear()

    def clearToSol(self):
        """Clear cells from cursor to start of line.

        """
        for cell in self.cells[:self.col + 1]:
            cell.clear()
        self._repadLine()

    def _repadLine(self):
        for k, cell in enumerate(self.cells):
            if cell:
                for i in range(k):
                    self.cells[i].fillSpace()
                return

    def cr(self):
        self.col = 0

    def asStr(self):
        """Get content as a simple string.

        :Return:
          An empty string if no cell contains a character. Otherwise a string
          for the line, with spaces used to fill cells before the right-most
          non-empty cell.

        """
        return "".join([cell.c for cell in self._trimmed()])

    def _trimmed(self):
        cells = list(self.cells)
        while cells and not cells[-1]:
            cells.pop()
        return cells

    #def __getitem__(self, idx):
    #    return self.cells[idx]

    def __nonzero__(self):
        """Test whether line has any cell set.

        A line is considered non-zero if any character position has been set.

        """
        for cell in self.cells:
            if cell.c is not None:
                return True
        return False


class TTY(object):
    """A file-like class emulating a terminal like file.

    This tries to be a partial approximation to an X terminal. The emulation
    does not currently try to be complete; only good enough to help test the
    code in CleverSheep.

    """
    TEXT = intern("TEXT")
    ESC = intern("ESC")
    CSI = intern("CSI")
    DSR = intern("DSR")     # Device status report
    DHCS = intern("DHCS")   # Designate hard character set

    #{ Initialisation and reset
    def __init__(self, width=80, height=25):
        """Initialisation:

        """
        self.lines = [Line(width) for r in range(height)]
        self.row = 0
        self.newLine = False
        self.attrs = Attrs()
        self.width = width
        self.height = height
        self._buildStateMachine()
        self._state = self.TEXT
        self._escSeq = []
        self._scrollStart, self._scrollEnd = 0, self.height - 1
        self.log = open("/tmp/emu.log", "w")

    def _buildStateMachine(self):
        b = partial(_buildCStates, (self.TEXT, self._putChar))
        q = partial(_buildCStates, (self.TEXT, self._ignore))
        nop = lambda c: None
        self._sm = {
            self.TEXT: b(("\n",        self.TEXT, self._newLine),
                         ("\r",        self.TEXT, self._carriageReturn),
                         (chr(27),     self.ESC,  self._initEsc),
                        ),
            self.ESC:  b(("[",          self.CSI,  self._initCSI),
                         ("()*+",       self.DHCS, self._store),
                        ),
            self.CSI:  b(("0123456789", self.CSI,  self._storeArg),
                         (";",          self.CSI,  self._newArgCSI),
                         ("HJKmr",      self.TEXT, self._handleEndCSI),
                         ("l",          self.TEXT, self._ignore),
                         ("?",          self.DSR,  self._store),
                        ),
            self.DSR:  b(("0123456789", self.DSR,  self._storeArg),
                         ("nh",         self.TEXT, self._ignore),
                        ),
            self.DHCS: q(),
            }
        self._csiVector = {
            ("J", (None,)): lambda c: (self._handleEndCSI("K"),
                                       self._clearLines(self.row + 1, -1)),
            ("J", (0,)):    lambda c: (self._handleEndCSI("K"),
                                       self._clearLines(self.row + 1, -1)),
            ("J", (1,)):    lambda c: (self._handleEndCSI("K"),
                                       self._clearLines(0, self.row)),
            ("J", (2,)):    self._clear,
            ("K", (None,)): lambda c: self.lines[self.row].clearToEol(),
            ("K", (0,)):    lambda c: self.lines[self.row].clearToEol(),
            ("K", (1,)):    lambda c: self.lines[self.row].clearToSol(),
            ("K", (2,)):    lambda c: (self.lines[self.row].clearToEol(),
                                       self.lines[self.row].clearToSol()),
            ("H", (None,)): self._home,
            ("H", 2):       self._positionCSI,
            ("m", 1):       self._attrCSI,
            ("r", 2):       self._regionCSI,
        }
    #}

    #{ File protocol support.
    def isatty(self):
        """Always return ``True`` so users treat this as a terminal.

        """
        return True

    def write(self, s):
        """Write text/control sequences at the current insertion point.

        :Param s:
            A text string. Supported special characters are interpreted as
            for an X terminal.

        """
        # Feed each character into the state machine.
        for c in s:
            self.log.write("CHAR %r %r %r\n" % (c, self._state, self._escSeq))
            self.log.flush()
            handler, newState = self._sm[self._state][ord(c)]
            handler(c)
            self._state = newState
    #}

    #{ State action handlers
    def _putChar(self, c):
        if self._escSeq:
            self.log.write("PAO Bad Seq %r\n" % (self._escSeq + [c],))
            self.log.flush()
            self._escSeq = []
        line = self.lines[self.row]
        try:
            line.putChar(c, self.attrs)
        except NoSpace:
            self._newLine(None)
            self._putChar(c)

    def _carriageReturn(self, c):
        self.lines[self.row].col = 0

    def _newLine(self, c):
        needToScroll = self.row == self._scrollEnd
        self.row += 1
        if needToScroll:
            a, b = self._scrollStart, self._scrollEnd
            self.lines.pop(a)
            self.lines[b: b] = [Line(self.width)]
            self.row -= 1
        self.lines[self.row].cr()

    def _initEsc(self, c):
        self._escSeq = [chr(27)]
        self._args = [None]

    def _store(self, c):
        self._escSeq .append(c)

    def _ignore(self, c):
        self.log.write("PAO IGN Seq %r\n" % (self._escSeq + [c],))
        self.log.write("---------------\n")
        self.log.flush()
        self._escSeq = []

    def _initCSI(self, c):
        self._escSeq.append(c)
        self._args = [None]

    def _storeArg(self, c):
        self._escSeq.append(c)
        if self._args[-1] is None:
            self._args[-1] = 0
        self._args[-1] = self._args[-1] * 10 + int(c)

    def _newArgCSI(self, c):
        self._escSeq.append(c)
        self._args.append(None)

    def _handleEndCSI(self, c):
        self._escSeq.append(c)
        for key in ((c, tuple(self._args)), (c, len(self._args))):
            func = self._csiVector.get(key, None)
            if func is not None:
                func(c)
                self.log.write("PAO OK Seq %r\n" % (self._escSeq,))
                self.log.write("---------------\n")
                self.log.flush()
                self._escSeq = []
                return
    #}

    #{ CSI completion methods
    def _clearLines(self, a, b):
        for line in self.lines[a: b]:
            line.clear()

    def _clear(self, c=None):
        self.lines = [Line(self.width) for r in range(self.height)]
        self.row = 0

    def _home(self, c):
        self.row = 0
        self.lines[self.row].col = 0

    def _positionCSI(self, c):
        if None not in self._args and 0 not in self._args:
            self.row, col = [v - 1  for v in self._args]
            self.lines[self.row].col = col

    def _regionCSI(self, c):
        if None in self._args:
            return
        self._scrollStart, self._scrollEnd = [v - 1 for v in self._args]

    def _attrCSI(self, c):
        self.attrs.set(self._args[0])

    def flush(self):
        """Support file protocol's flush method.

        """
        pass

    #{ Standard special methods
    def __str__(self):
        """Convert to a string.

        The string does *not* include escape sequences.

        """
        return "\n".join(self._strLines())

    def _strLines(self):
        lines = list(self.lines)
        while lines and not lines[-1]:
            lines.pop()
        return [line.asStr() for line in lines]
    #}

    #{ Properties
    @property
    def col(self):
        return self.lines[self.row].col
    #}

    #{ Debug support.
    def blocks(self):
        """Generator: Yield blocks of similarly rendered characters.

        This yields tuples of the form ``(s, (fg, bd, attrs))``, where, in each
        case ``s`` is the longest string for which the other values are all the
        same. Each newline is separately yielded, with ``(None, None, None)``
        for the attributes.

        """
        for line in self.lines:
            s, attrs = None, None
            for cell in line.cells:
                if cell.c is not None:
                    if s is None:
                        s, attrs = cell.c, cell.attrTuple
                    elif attrs != cell.attrTuple:
                        yield s, attrs
                        s, attrs = cell.c, cell.attrTuple
                    else:
                        s += cell.c
            if s is not None:
                yield s, attrs
            yield "\n", (None, None, None)
    #}
