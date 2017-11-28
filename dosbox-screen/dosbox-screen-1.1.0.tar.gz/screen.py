# -*- coding: utf-8 -*-

"""Provides :class:`Screen`, which lets you write text to specific coordinates
   in the dos command shell, with colors.
"""
# pylint:disable=R0201,R0902
# R0201: method could be a function
# R0902: too many instance attributes
from __future__ import print_function
import sys
import os
import struct
import pprint
import threading

try:
    import colorama
    colorama.init()
    USE_ANSI = True
except ImportError:
    USE_ANSI = os.environ.get("ConEmuANSI") == "ON" or sys.platform != 'win32'


class ScreenInfo(object):
    """Information about the screen dimensions.
       Calls SetConsoleMode and GetConsoleScreenBufferInfo on windows,
       and tries various methods of getting the screen dimension on
       non-windows platforms.
    """

    def __init__(self, **kw):
        self.width = kw.get('width', 0)
        self.height = kw.get('height', 0)
        self.x = kw.get('x', 0)
        self.y = kw.get('y', 0)
        self.left = kw.get('left', 0)
        self.top = kw.get('top', 0)
        self.right = kw.get('right', 0)
        self.bottom = kw.get('bottom', 0)
        self.maxx = kw.get('maxx', 0)
        self.maxy = kw.get('maxy', 0)
        self.xpos = kw.get('xpos', 0)
        self.ypos = kw.get('ypos', 0)

        if sys.platform == 'win32':
            self.__set_from_screen_info_win32()
        else:
            self.__set_screen_info_nix()

    def __get_screen_size_nix(self):
        """Try various methods of getting the screen size on *nixen.
           From: http://stackoverflow.com/a/566752/75103
        """
        env = os.environ

        def ioctl_GWINSZ(fd):
            try:
                import fcntl, termios
                cr = struct.unpack(
                    'hh',
                    fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234')
                )
            except:
                return
            return cr

        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
        return int(cr[1]), int(cr[0])

    def __set_screen_info_nix(self):
        cols, lines = self.__get_screen_size_nix()
        self.width = cols - 1
        self.height = lines - 1
        self.right = self.maxx = self.width
        self.bottom = self.maxy = self.height

    def __set_from_screen_info_win32(self):
        """Call windows internals to get dimensions of dosbox.

           typedef struct _CONSOLE_SCREEN_BUFFER_INFO {
              COORD      dwSize;
              COORD      dwCursorPosition;
              WORD       wAttributes;
              // A SMALL_RECT structure that contains the console screen buffer
              // coordinates of the upper-left and lower-right corners of the
              // display window.
              SMALL_RECT srWindow;

              // A COORD structure that contains the maximum size of the console
              // window, in character columns and rows, given the current screen
              // buffer size and font and the screen size.
              COORD      dwMaximumWindowSize;
           } CONSOLE_SCREEN_BUFFER_INFO;

           typedef struct _COORD {
             SHORT X;
             SHORT Y;
           } COORD, *PCOORD;

           typedef struct _SMALL_RECT {
             SHORT Left;
             SHORT Top;
             SHORT Right;
             SHORT Bottom;
           } SMALL_RECT;

        """
        from ctypes import windll, create_string_buffer

        # Disable line wrapping at bottom of terminal. Having it on means that
        # anything written to the bottom-most/right-most spot causes the
        # terminal to wrap -- that is most likely not what you want when
        # doing absolute cursor positioning.
        h = windll.kernel32.GetStdHandle(-11)
        windll.kernel32.SetConsoleMode(h, 1)

        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if not res:
            raise RuntimeError("Error calling: GetConsoleScreenBufferInfo.")
        vals = struct.unpack("hhhhHhhhhhh", csbi.raw)
        self.width = vals[0]
        self.height = vals[1]
        self.x = vals[2]
        self.y = vals[3]
        self.left = vals[5]
        self.top = vals[6]
        self.right = vals[7]
        self.bottom = vals[8]
        self.maxx = vals[9]
        self.maxy = vals[10]


screen_lock = threading.Lock()


class Window(object):
    """A window that will scroll text written to it.
       The screen object is thread safe when used through Window objects.
    """
    def __init__(self, screen, x, y, width, height):
        # self.dbg = []

        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.xpos, self.ypos = (0, 0)
        self.content = ['' for _ in range(self.height)]

    def __repr__(self):
        t = self.__dict__.copy()
        del t['content']
        del t['screen']
        # del t['dbg']
        return "screen.Window(%r)" % t

    def _paint_content(self):
        self.cls()
        with screen_lock:
            self.screen.writelinesxy(
                self.x, self.y, '\n'.join(self.content)
            )

    def _scroll_up(self, n=None):
        if n is None:
            n = self.height // 2
        self.content = self.content[n:] + [''] * n
        self._paint_content()
        self.ypos -= n

    def _write(self, txt):
        if self.ypos >= self.height:
            self._scroll_up()

        self.content[self.ypos] = self.content[self.ypos][:self.xpos] + txt

        self.writexy(self.xpos, self.ypos, txt)
        self.xpos += len(txt)

    def newline(self):
        self.xpos = 0
        self.ypos += 1

    def writexy(self, x, y, txt):
        """Write to position x, y relative to the window.
        """
        with screen_lock:
            self.screen.writexy(
                self.x + x,
                self.y + y,
                txt
            )

    def write(self, *args):
        """Write to current position in the window, scrolling
           the contents as needed.
        """
        txt = ' '.join(str(arg) for arg in args)
        if txt == '\n':
            self.newline()
        else:
            while txt:
                avail_space = self.width - self.xpos
                try:
                    nlpos = txt.index('\n')
                    if nlpos > avail_space:
                        raise ValueError()
                    rest_of_line = txt[:nlpos]
                    txt = txt[nlpos+1:]
                except ValueError:
                    rest_of_line = txt[:avail_space]
                    txt = txt[avail_space:]

                self._write(rest_of_line)
                if txt:
                    self.newline()

    def cls(self, color=None):
        """Clear window, fill it with the given color.
        """
        args = {}
        if color:
            args['background'] = color
        with screen_lock:
            self.screen.fill(self.x, self.y, self.width, self.height, char=' ', **args)


class Screen(object):
    """Screen provides a interface for positioned writing, with color,
       to the screen.
    """
    colors = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
    _foreground = {cname: i + 30 for i, cname in enumerate(colors)}
    _background = {cname: i + 40 for i, cname in enumerate(colors)}

    def __init__(self, screeninfo=None, **kw):
        """Default foreground and background colors can be specified as e.g.::

               scr = Screen(fg='white', bg='black')

           foreground color can be set with any of the following synonyms:

               fg, foreground, color

           background color can be set with any of the following synonyms:

               bg, background, on

           e.g.::

               scr = Screen(color='red', on='black')

        """
        s = screeninfo or ScreenInfo()
        self.buffer_width = s.width
        self.buffer_height = s.height
        self.buffer_x = s.x
        self.buffer_y = s.y
        self.buffer_left = s.left
        self.buffer_top = s.top
        self.buffer_right = s.right
        self.buffer_bottom = s.bottom
        self.maxx = s.maxx
        self.maxy = s.maxy

        self.xpos = self.buffer_x - self.buffer_left + 1
        self.ypos = self.buffer_y - self.buffer_top + 1
        self.fg = self.bg = ''
        self.fg, self.bg = self._get_colors(kw)

    # backwards compatibility setters/getters
    @property
    def Fore(self):
        return self.fg

    @Fore.setter
    def Fore(self, val):
        self.fg = val

    @property
    def Back(self):
        return self.bg

    @Back.setter
    def Back(self, val):
        self.bg = val

    def format(self, *args, **kwargs):
        """Similar to the print-function, but returns the resulting string
           instead of printing it.
        """
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '')
        # file = kwargs.get('file', sys.stdout)
        txt = sep.join(str(a) for a in args)
        return txt + end

    def color(self, *args, **kw):
        """Return a colored version of `s`, ready for printing.
        """
        txt = self.format(*args, **kw)
        if not USE_ANSI:
            return txt
        colors = self._get_colors(kw)
        setcolor = '\x1b[%sm' % ';'.join([str(c) for c in colors if c])
        clearcolor = '\x1b[0m'
        return setcolor + str(txt) + clearcolor

    def _get_colors(self, kw):
        """Grab color synonyms from `kw`.
        """
        kwkeys = set(kw.keys())

        def getcolor(which, synonyms, default=''):
            key = synonyms & kwkeys
            if key:
                return which.get(
                    kw.pop(key.pop()).lower(),
                    default
                )
            return default

        fg = getcolor(self._foreground, {'foreground', 'color', 'fg'}, self.fg)
        bg = getcolor(self._background, {'background', 'on', 'bg'}, self.bg)
        return fg, bg

    def windows(self, xcount, ycount):
        """Returns a list of ``count`` symetrically created windows.
        """
        wwidth = self.width // xcount
        wheight = self.height // ycount
        assert wwidth > 6 and wheight > 6
        rows = []
        for y in range(ycount):
            cols = []
            for x in range(xcount):
                w = Window(self, x * wwidth, y * wheight, wwidth - 1, wheight - 1)
                cols.append(w)
            rows.append(cols)
        return rows

    @property
    def left(self):
        """The first column of the screen (the visible part of the screen
           buffer).
        """
        return 0

    @property
    def top(self):
        """The first row of the screen.
        """
        return 0

    @property
    def right(self):
        """The rightmost column of the screen.
        """
        return self.width

    @property
    def bottom(self):
        """The last (bottom-most) row of the screen.
        """
        return self.height - 1

    @property
    def center(self):
        """The horizontal center of the screen.
        """
        return self.left + self.width // 2

    @property
    def middle(self):
        """The vertical middle of the screen.
        """
        return self.top + self.height // 2

    @property
    def width(self):
        """The width of the visible portion of the screen buffer.
        """
        return self.buffer_right - self.buffer_left + 1

    @property
    def height(self):
        """The height of the visible portion of the screen buffer.
        """
        return self.buffer_bottom - self.buffer_top + 1

    @property
    def coords(self):
        """Mostly a convenience method for debugging.
        """
        return dict(
            left=self.left,
            right=self.right,
            top=self.top,
            bottom=self.bottom,
            center=self.center,
            middle=self.middle,
            width=self.width,
            height=self.height,
        )

    def __repr__(self):
        tmp = self.coords
        tmp.update(self.__dict__)
        return pprint.pformat(tmp, width=35)

    def _xy(self, x, y):
        "Position the cursor at x, y (where x, y are zero-based coordinates)."
        if not USE_ANSI:
            return ""
        return '\033[%d;%dH' % (y + 1, x + 1)

    def gotoxy(self, x, y):
        """Put cursor at coordinates ``x``, ``y``.
        """
        sys.stdout.write(self._xy(x, y) + '')
        self.ypos = y
        self.xpos = x

    def writelinesxy(self, x, y, *args, **kw):
        """If the string resulting from prosessing `args` contains newlines,
           then write the next line at x, y+1, etc.
        """
        txt = self.format(*args, **kw)
        lines = txt.split('\n')
        for i, line in enumerate(lines):
            self.writexy(x, y + i, line, **kw)

    def print(self, *args, **kwargs):
        """Write output without cursor positioning.
        """
        print(self.color(*args, **kwargs), end=kwargs.get('end', '\n'))

    def write(self, *args, **kw):
        """Write args at current location, see writexy function for keyword
           arguments.
        """
        self.writexy(self.xpos, self.ypos, *args, **kw)

    def writexy(self, x, y, *args, **kw):
        """Write args at position x, y.
           Specify foreground and backround colors with keyword arguments.
           Available colors:

            - black
            - red
            - green
            - yellow
            - blue
            - magenta
            - cyan
            - white

           (Be aware that the color names can be mapped to entirely different
           colors by e.g. changing values in the registry:
           https://github.com/neilpa/cmd-colors-solarized)
        """
        txt = self.format(*args, **kw)
        sys.stdout.write(self._xy(x, y) + self.color(txt, **kw))
        self.ypos = y
        self.xpos = x + len(txt)

    def rightxy(self, x, y, *args, **kw):
        """Write text right justified at coordinates x, y.
           The last character will be written at position
           (x-1, y), which means that e.g.::

               scr.rightxy(scr.right, scr.bottom, 'bottom right')

           will be written flush in the bottom right corner, and::

               scr.rightxy(scr.center, scr.middle, 'hello')
               scr.writexy(scr.center, scr.middle, 'world')

           will output `helloworld` (without a space) in the middle
           of the screen.
        """
        txt = ' '.join(str(a) for a in args)
        self.writexy(x - len(txt), y, txt, **kw)

    def centerxy(self, x, y, *args, **kw):
        """Write text centered around the x coordinate.
        """
        txt = ' '.join(str(a) for a in args)
        self.writexy(self.center - len(txt) // 2, y, txt, **kw)

    def fill(self, x, y, width, height, char=' ', **kw):  # pylint:disable=R0913
        """Fill rectangle with char, and leave the writing position at
           the beginning of the rectangle (position x,y).
        """
        for ypos in range(y, y + height):
            self.writexy(x, ypos, char * width, **kw)
        self.xpos = x
        self.ypos = y

    def cls(self, color=None):
        """Clear screen, fill it with the given color.
        """
        args = {}
        if color:
            args['background'] = color
        self.fill(0, 0, self.width, self.height, char=' ', **args)
