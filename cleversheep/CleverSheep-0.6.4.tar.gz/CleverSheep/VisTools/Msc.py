#! /usr/bin/env python
"""Sequence diagram drawing module."""


# System modules
import sys
import textwrap
from itertools import chain

from CleverSheep.TTY_Utils import Colours, RichTerm

try:
    if sys.stdout.isatty(): #pragma: to test
        import ultraTB
        # sys.excepthook = ultraTB.ColorTB()
        # sys.excepthook = ultraTB.VerboseTB()
except ImportError:
    pass
except AttributeError: #pragma: debug
    pass # For epydoc processing


streams = {}
def _getStream(f, fg=None, bg=None, bold=False, blink=False, uline=False):
    fg = fg or None
    bg = bg or None
    bold = bold or False
    blink = blink or False
    uline = uline or False
    if bold: bold = True
    if blink: blink = True
    if uline: uline = True
    key = (f, fg, bg, bold, blink, uline)

    if key in streams:
        return streams[key]

    streams[key] = Colours.ColourStream(RichTerm.RichTerminal(f),
            fg=fg, bg=bg,
            bold=bold, blink=blink, uline=uline)
    return streams[key]


def _getTextPlusScheme(text):
    scheme = None
    if isinstance(text, AttrString):
        return text.segments
    elif isinstance(text, (tuple, list)):
        text, scheme = text
    assert isinstance(text, str)
    scheme = scheme or Scheme()
    return [(text, scheme)]


def _getAttrString(text):
    if isinstance(text, AttrString):
        return text
    return AttrString(_getTextPlusScheme(text)[0])


class AttrString(object):
    """A string with attributes for each character.

    This is used to store a string with information about how each character
    should be represented - things like colour and bold.

    Typical use is to create an instance then append additional text, in order
    to create a string with a mixture of colours, etc. For example:<py>:

        s = AttrString("Hello", fg="blue")
        s.append("and goodbye!", fg="red", bold=True)

    """
    def __init__(self, text=""):
        """Constructor:

        :Param text:
            The initial text.
        :Param fg, bg:
            The foreground and background colours for ``text``.
        :Param bold, blink, uline:
            Additional boolean attribute flags.

        """
        if not text:
            self.segments  = []
        else:
            self.segments = _getTextPlusScheme(text)

    def append(self, text, fg=None, bg=None, bold=False, blink=False, uline=False):
        """Append text to the string.

        :Param text:
            The initial text.
        :Param fg, bg:
            The foreground and background colours for ``text``.
        :Param bold, blink, uline:
            Additional boolean attribute flags.

        """
        self.segments.extend(_getTextPlusScheme(text))

    def replace(self, pos, text=""):
        text = _getAttrString(text)
        left, right = self.split(pos)
        _, right = right.split(len(text))
        self.segments = left.segments + text.segments + right.segments

    def split(self, leftLen):
        tLen = 0
        left = AttrString()
        right = AttrString()
        right.segments = list(self.segments)

        while len(left) < leftLen and len(right) > 0:
            left.append(right.segments.pop(0))

        d = -99
        if len(left) > leftLen:
            d = len(left) - leftLen
            text, scheme = left.segments.pop()
            left.append((text[:-d], scheme))
            right.segments[0:0] = [(text[-d:], scheme)]
        #print ">>>", leftLen, d, len(self), repr(str(self))
        #print "   ", repr(str(left)), repr(str(right))
        return left, right

    def __add__(self, rhs):
        n = AttrString()
        n.segments = self.segments + rhs.segments
        return n

    def __len__ (self):
        return sum(len(seg[0]) for seg in self.segments)

    def __str__(self):
        """Convert to a plain string.

        :Return:
            A plain string representation, losing attribute info.

        """
        return "".join([seg[0] for seg in self.segments])
    str = __str__

    def seq(self, f=None):
        """Convert to a sequence for `Colours.Xstream`.

        :Return:
            A sequence of `Colours.ColourStream` instances and strings.

        """
        f = f or sys.stdout
        def groups (l):
            group = []
            for c, code in l:
                if not group:
                    group.append ((c, code))
                    curCode = code
                elif code != curCode:
                    yield group
                    group = [(c, code)]
                    curCode = code
                else:
                    group.append ((c, code))
            if group:
                yield group

        s = ""
        xxx = []
        for g in groups (self.chars):
            code = g[0][1]
            cs = _getStream(f, *code)
            xxx.append(cs)
            s = ""
            for c, code in g:
                s += c
            xxx.append(s)
            xxx.append(_getStream(f))
        return xxx


class Scheme(object):
    """A colour and formatting scheme for a chart entity or line.

    Provides an abstract scheme to be applied during rendering. The renderer
    chooses exactly how a given scheme will be displayed.

    The following attributes are supported.

    weight
        Should be heavy, normal (the default) or light.

    colour
        Should be black (the default), red, green, blue, cyan, magenta or
        yellow.

    preferredColour
        Can be any colour defined in ``/etc/rgb.txt``. The preferred colour is
        only used of the renderer supports it, otherwise the ``colour`` is
        chosen.

    """

    def __init__(self, **kwargs):
        self.colour = "black"
        self.weight = "normal"
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        return self.__dict__.get(name, None)


class Message(object):
    """A message on a sequence chart."""
    typeName = "message"

    def __init__ (self, label="", time=None, scheme=None):
        """Constructor:

        :Param label:
            The label that should appear on the message line.
        :Param fg, bd:
            Foreground and background colours for the ``labOn``. If you want
            colour for the other labels then use the `addAbove` or
            `addBelow` methods.
        :Param bold:
            Set true to draw in a bold font.
        :Param prefix:
            A prefix to place to the left of the chart in the left margin,
            provided there is a left margin.

        """
        self.label = AttrString(label)
        self.above = []
        self.below = []
        self.time = time
        if time is not None:
            self.msTime, self.absTime = time
        self.scheme = scheme or Scheme()

    def addAbove (self, label, append=0):
        """Add a label above the line.

        Adds a label above the line for this message. This can be called
        multiple times to add several lines of label. Each call pushes
        earlier lable up so that, for example::

            m.addLabel("Hello")
            m.addLabel("World")

        will render in the same order. You can also use multiple colours and
        bold effects for a label by making multiple calls using the ``append``
        argument.

        :Return:
            The `AttrString` that represents the label

        :Param label:
            The label that should appear above the message line.
        :Param fg, bd:
            Foreground and background colours for the ``labOn``. If you want
            colour for the other labels then use the `addAbove` or
            `addBelow` methods on the returned `Message`.
        :Param bold:
            Set true to draw in a bold font.
        :Param append:
            Set true to append to the previously added label rather than push a
            new one just above the line. A space will be added before the new
            text.
        """
        if self.above and append:
            self.above[-1].append(AttrString(" "))
            self.above[-1].append(AttrString(label))
        else:
            self.above.append(AttrString(label))
        return self.above[-1]

    def addBelow (self, label, append=0):
        """Add a label below the line.

        Very similar to addAbove, but (of course) adds a label below the line.
        This can be called multiple times to add several lines of label. Each
        call adds below earlier lable so that, for example::

            m.addLabel("Hello")
            m.addLabel("World")

        will render in the same order. Otherwise it behaves in the same way as
        addAbove and has the same arguments.
        """
        if self.below and append:
            self.below[-1].append(AttrString(" "))
            self.below[-1].append(AttrString(label))
        else:
            self.below.append(AttrString(label))
        return self.below[-1]

    def getAbove (self):
        """Get the last label added above.

        :Return:
            The `AttrString` that represents the label

        """
        if self.above:
            return self.above[-1]

    def getBelow (self):
        """Get the last label added below.

        :Return:
            The `AttrString` that represents the label

        """
        if self.below:
            return self.below[-1]

    def len(self):
        """Get the length of the label, for rendering.

        :Return:
            Actually the witdh required to display the label, i.e. the
            maximum width of the above/on/below labels.

        """
        return max([len(m) for m in [self.label] + self.above + self.below])


class Commentary(object):
    """A commentary on a sequence chart."""
    typeName = "commentary"

    def __init__(self, text):
        self.text = text


class _Struct(object):
    """General structure to hold a collection of values.

    """


class SequenceChart(object):
    """Class to hold a sequence chart.

    :Ivariables:
      entries
        The entries that make up the chart, in time order.
      parties
        The names of all the parties identified from the entries, or explicitly
        defined.

    """
    def __init__ (self, parties=None, cont=0, chartWidth=80, outfile=sys.stdout,
                    leftLabWidth=0, firstCol=0):
        """Constructor:

        :Param parties:
             List of names of each party. First appears on the left.
        """
        self.entries = []
        self.parties = parties or []
        self._partyScheme = {}
        self._messageSchemes = {}
        self._partyColour = {}
        self._partyEmphasis = {}
        self._firstCol = firstCol
        self._outputEnt = 0
        self._cont = cont
        self._outfile = outfile
        self._startTime = None

    def getRelTime_ms(self, msTime):
        return msTime - self._startTime

    def getTimeStr(self, msg, width=7):
        if hasattr(msg, "msTime"):
            t = self.getRelTime_ms(msg.msTime)
            return "%*d.%03d" % (width-4, t // 1000, t % 1000)
        return " " * 7

    def getSchemes(self):
        return chain(self._partyScheme.itervalues(), self._messageSchemes)

    def partyScheme(self, name):
        return self._partyScheme.get(name, Scheme())

    def partyColour(self, name):
        return self._partyColour.get(name, None)

    def partyEmphasis(self, name):
        return self._partyEmphasis.get(name, None)

    def setParties (self, parties):
        """Define the parties for the chart.

        Used to set/modify the parties exchanging message, post construction.

        """
        self.parties = parties

    def setPartyColour(self, name, colour):
        self._partyColour[name] = colour

    def setPartyScheme(self, name, scheme):
        self._partyScheme[name] = scheme

    def setPartyEmphasis(self, name, emphasis):
        self._partyEmphasis[name] = emphasis

    def addMessage(self, src, dst, labOn="", labAbove="", labBelow="",
                time=None, scheme=None, prefix=None):
        """Add a message to the chart.

        :Return:
            A `Message` instance for the newly added message.

        :Param src, dst:
            The source and destination parties for the message.
        :Param labOn:
            The label that should appear on the message line.
        :Param labAbove, labBelow:
            Labels that should be drawn above/below the message line.
        :Param fg, bd:
            Foreground and background colours for the ``labOn``. If you want
            colour for the other labels then use the `Message.addAbove` or
            `Message.addBelow` methods on the returned `Message`.
        :Param bold:
            Set true to draw in a bold font.
        :Param leftLab:
            Currently not used.
        :Param time:
            The time of the message.

        """
        if time is not None and self._startTime is None:
            msTime, absTime = time
            self._startTime = msTime
        if scheme is not None:
            self._messageSchemes[scheme] = None
        #if self._cont:
        #    self.drawAsText (cont=1)
        #    self.entries = []
        #    self._outputEnt = 0
        if prefix is not None:
            labOn = "%s %s" % (prefix, labOn)
        msg = Message(labOn, time=time, scheme=scheme)
        if labBelow:
            msg.addBelow(labBelow)
        if labAbove:
            msg.addAbove(labAbove)
        self.entries.append ((src, dst, msg))
        return msg

    def addCommentary(self, text):
        self.entries.append((None, None, Commentary(text)))

    def getMsg (self):
        """Get the `Message` instance for the last added message

        :Raises IndexError:
            If there are no messages.
        :Return:
            A `Message` instance.
        """
        if self.entries:
            return self.entries[-1][2]

    def drawDump (self, outfile=None, chartWidth=None, cont=0):
        """Draw this chart in text form.

        Renders the chart using text. If the output is a terminal then the
        output will also be coloured.

        :Param outfile:
            The file to which the chart should be written, use this to
            over-ride the default set at construction.
        :Param chartWidth:
            The nominal width (in characters) for the chart.
        :Param cont:
            Not intended for direct use. It is used internally when generating
            a continuously updating chart.
        """
        return self.renderAsText(outfile=outfile, chartWidth=chartWidth, cont=cont,
                Streamer=DumpStream)


class Renderer(object):
    """Render base class.

    """
    def __init__(self, chart, outfile=None):
        self.chart = chart
        self._outfile = outfile or sys.stdout
        self.timeFormat = ""


class MscgenRenderer(Renderer):
    """Render for Msc-generator output.

    """
    def loadRGB(self):
        self.colours = colours = {}
        with open("/etc/X11/rgb.txt") as f:
            for line in f:
                parts = line.split()
                if len(parts) != 4:
                    continue
                colours[parts[-1]] = ",".join(parts[:3])

    def render(self, outfile=None, chartWidth=None, Streamer=Colours.Xstream):
        def escape(s):
            s = s.replace('\\', '\\\\')
            s = s.replace(r'[', r'\[')
            s = s.replace(r']', r'\]')
            s = s.replace(r';', r'\;')
            return s

        def makeRichText(s, prefix=""):
            parts = []
            for text, scheme in s.segments:
                if scheme:
                    name = schemes.get(scheme, None)
                if name:
                    parts.append(r"\s(%s)%s%s" % (name, prefix, escape(text)))
                else:
                    parts.append(r"\s(default)%s%s" % (prefix, escape(text)))
            return "".join(parts)

        self.loadRGB()
        chart = self.chart
        if len(chart.parties) < 2:
            return

        # The header
        f = self._outfile
        f.write('hscale=auto;\n')
        f.write('defcolor magenta="255,0,255";\n')
        f.write('defcolor cyan="0,255,255";\n')
        f.write('defstyle default [text.color="black"];\n')
        done = {}
        for scheme in chart.getSchemes():
            if not scheme.preferredColour or scheme.preferredColour in done:
                continue
            done[scheme.preferredColour] = None
            f.write('defcolor %s="%s";\n' % (scheme.preferredColour,
                self.colours[scheme.preferredColour]))
        schemes = {}
        for i, scheme in enumerate(chart.getSchemes()):
            schemes[scheme] = "style_%s" % i
            s = []
            colour = scheme.preferredColour or scheme.colour
            if colour is not None:
                s.append("line.color=%s" % colour)
                s.append("text.color=%s" % colour)
            f.write("defstyle %s [%s];\n" % (schemes[scheme], ", ".join(s)))

        for p in chart.parties:
            partyScheme = chart.partyScheme(p)
            attrs = []
            #emphasis = chart.partyEmphasis(p)
            #if emphasis:
            #    attrs.append('%s' % emphasis)
            colour = partyScheme.preferredColour or partyScheme.colour
            if colour:
                attrs.append('color=%s' % colour)
            if attrs:
                f.write('%s [%s];\n' % (p, ",".join(attrs)))
            else:
                f.write('%s;\n' % (p,))
        accrossAll = chart.parties[0], chart.parties[-1]

        # The entries
        msgNum = 0
        for ent in chart.entries:
            src, dst, msg = ent
            if msg.typeName == "message":
                attrs = []
                emphasis = chart.partyEmphasis(src) or chart.partyEmphasis(dst)
                if emphasis:
                    attrs.append('%s' % emphasis)
                lineStyle = schemes.get(msg.scheme, "")
                if lineStyle:
                    lineStyle = " [%s]" % lineStyle
                for i, attrString in enumerate(chain([msg.label], msg.above, msg.below)):
                    if i == 0:
                        msgNum += 1
                        f.write('%s->%s%s: %s. %s\n' % ( src, dst, lineStyle, msgNum,
                            makeRichText(attrString)))
                    elif 1 or i == 1:
                        f.write('        %s\n' % (makeRichText(attrString, '\-')))
                f.write(';\n')
            elif msg.typeName == "commentary":
                src, dst = accrossAll
                lines = textwrap.wrap(msg.text, 80)
                for i, line in enumerate(lines):
                    if i == 0:
                        f.write('%s==%s: %s\n' % (src, dst, escape(line)))
                    else:
                        f.write('        %s\n' % (escape(line),))
                f.write(';\n')


class ChartLine(AttrString):
    """Represents a line on a message sequence chart.

    This is really only intended for internal use.

    """
    def __init__ (self, length, columns, chart):
        super(ChartLine, self).__init__()
        AttrString.__init__(self, " " * length)
        for name in columns:
            self.replace(columns[name], ("|", chart.partyScheme(name)))
            #self.put (columns[name], "|", bold=1, fg=partyScheme.colour)


class TextRenderer(Renderer):
    """Render for textual output.

    """
    def __init__(self, chart, outfile=None):
        super(TextRenderer, self).__init__(chart, outfile)
        self._marginWidth = 0 # leftLabWidth
        self._chartWidth = 80 # chartWidth
        self._needHdr = True

    def render(self, outfile=None, chartWidth=None, Streamer=Colours.Xstream):
        if len(self.chart.parties) < 2:
            return

        # Work out general positions
        self.pad = " " * self._marginWidth
        self.outfile = outfile or self._outfile
        self.columns = self._calcLinePositions(chartWidth)
        self.chartWidth = max(self.columns.values()) + 1

        self.xs = Streamer(outfile)
        self._renderHeader()
        self._renderEntries()

    def _renderAttrString(self, line):
        seq = []
        for text, scheme in line.segments:
            bold = scheme.weight == "heavy"
            seq.append(_getStream(self.outfile, fg=scheme.colour, bold=bold))
            seq.append(text)
        seq.append(_getStream(self.outfile))
        self.xs.write(seq)

    def _renderHeader(self):
        chart = self.chart
        chartWidth = self.chartWidth
        columns = self.columns
        pad = self.pad
        xs = self.xs
        if self.timeFormat == "absolute":
            pad += "            "
        elif self.timeFormat == "relative":
            pad += "       "

        if self._needHdr:
            self._needHdr = False
            line = AttrString()
            for name in chart.parties:
                partyScheme = chart.partyScheme(name)
                col = columns[name]
                pos = col - len(name) / 2
                if pos < 0:
                    pos = 0
                if pos + len(name) > chartWidth:
                    pos = chartWidth - len(name)
                line.append(" " * (pos - len(line)))
                line.append((name, partyScheme))
            xs.write(pad)
            self._renderAttrString(line)
            xs.write("\n")

    def _renderEntries(self):
        chart = self.chart
        chartWidth = self.chartWidth
        columns = self.columns
        pad = self.pad
        xs = self.xs
        if self.timeFormat == "absolute":
            pad += "            "
        elif self.timeFormat == "relative":
            pad += "       "

        needBlank = False
        for ent in chart.entries:
            src, dst, msg = ent
            if msg.typeName == "commentary":
                text = textwrap.wrap(msg.text, chartWidth - 2)
                xs.write(pad[:-2] + ",")
                xs.write("-" * (chartWidth + 2))
                xs.write(".\n")
                for line in text:
                    xs.write(pad[:-2] + "| ")
                    xs.write(line.ljust(chartWidth))
                    xs.write(" |\n")
                xs.write(pad[:-2] + "`")
                xs.write("-" * (chartWidth + 2))
                xs.write("'\n")
                continue

            if msg.typeName != "message":
                continue
            a = columns.get(src)
            b = columns.get(dst)
            if a == None or b == None:
                continue

            line = ChartLine (chartWidth, columns, chart)
            if needBlank or msg.above:
                xs.write(pad)
                self._renderAttrString(line)
                xs.write("\n")
            needBlank = bool(msg.below)

            length = b - a
            if length < 0:
                length = 0 - length - 1
                #arrow = AttrString('<' + '-' * (length-1), bold=1)
                arrow = AttrString(('<' + '-' * (length-1), msg.scheme))
                pos = b + 1
            else:
                length -= 1
                #arrow = AttrString('-' * (length-1) + ">", bold=1)
                arrow = AttrString(('-' * (length-1) + ">", msg.scheme))
                pos = a + 1

            for lab in msg.above:
                lab = str(lab)
                line = ChartLine (chartWidth, columns, chart)
                line.replace(pos + 2, lab[:length - 4])
                #line.put (pos + 2, lab[0:length-4])
                xs.write(pad)
                self._renderAttrString(line)
                #xs.write(line.seq(self.outfile))
                xs.write("\n")

            line = ChartLine (chartWidth, columns, chart)
            line.replace(pos, arrow)
            if msg.label:
                line.replace(pos + 2, msg.label)
            prefix = pad
            if self.timeFormat == "relative":
                prefix = chart.getTimeStr(msg).rjust(len(prefix))
            elif self.timeFormat == "absolute":
                prefix = msg.absTime.rjust(len(prefix))
                #prefix = chart.getTimeStr(msg.prefix[:self._marginWidth] + pad[len(msg.prefix):]
            xs.write(prefix)
            self._renderAttrString(line)
            #xs.write(line.seq(self.outfile))
            xs.write("\n")

            for lab in msg.below:
                lab = str(lab)
                line = ChartLine (chartWidth, columns, chart)
                line.replace(pos + 2, lab[:length - 4])
                xs.write(pad)
                self._renderAttrString(line)
                #xs.write(line.seq(self.outfile))
                xs.write("\n")

    def _calcLinePositions(self, chartWidth):
        # Work out the minimum widths based on the known messages.
        # We only consider messages between immediate neighbours.
        chart = self.chart
        neighbours = {}
        for i, name in enumerate(chart.parties[:-1]):
            pair = tuple(sorted([name, chart.parties[i+1]]))
            neighbours[pair] = i
        minWidths = [0] * (len(chart.parties) - 1)
        for src, dst, msg in chart.entries:
            pair = tuple(sorted([src, dst]))
            idx = neighbours.get(pair, None)
            if idx is None:
                continue
            minWidths[idx] = max(minWidths[idx], msg.len())
            print "IDX", idx, minWidths[idx]

        # Now work out the line positions, allowing for the known message
        # widths and the head/tail of the arrowed lines.
        chartWidth = chartWidth or self._chartWidth
        columns = {}
        names = list(chart.parties)
        col = 0
        usedWidth = 0
        lParties = len(chart.parties)
        for i, name in enumerate(chart.parties):
            columns[name] = col
            if lParties - i - 1 > 1:
                nominalSpace = (chartWidth - usedWidth) / (lParties - 1)
            else:
                nominalSpace = chartWidth - usedWidth - 1
            if lParties - i - 1 > 0:
                nominalSpace = max(nominalSpace, minWidths[i] + 5)
            col += nominalSpace
            usedWidth += nominalSpace
        return columns


class DumpRenderer(TextRenderer):
    """Render for dumped output.

    """
    def render(self, outfile=None, chartWidth=None):
        super(DumpRenderer, self).render(outfile, chartWidth, Streamer=DumpStream)


class DumpStream(object):
    def __init__(self, f=None):
        self.f = f or sys.stdout

    def write(self, seq):
        """Write a sequence of strings, using several streams,

        The arguments should be a sequence of strings and streams.
        When a stream is encountered, subsequent strings are written to
        that stream.

        A stream is anything based on `ColourStream` or ``file``.
        """
        f = self.f
        if isinstance(seq, basestring):
            seq = [seq]
        for arg in seq:
            if isinstance(arg, (file, Colours.ColourStream)):
                f = arg
                continue
            try:
                scheme = f.scheme
                fg = scheme.get("fg", None)
                bg = scheme.get("bg", None)
                bold = scheme.get("bold", None)
            except:
                fg = bg = bold = None
            self.f.write("%r\n" % {
                "bg": bg, "fg": fg, "bold": bold, "text": arg,})

