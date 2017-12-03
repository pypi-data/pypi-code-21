#!/usr/bin/env python
# coding: utf-8

import datetime
import locale
import os
import sys
import re
import random
import struct
import traceback
import argparse
import subprocess as sp
import unicodedata

from os.path import dirname, join

from quin import rua

ROOT = join(dirname(__file__), 'static')
DEFAULT_QUIN = 'quin.txt'


class Quin(object):
    def __init__(self, tty, ns):
        self.tty = tty
        self.ns = ns
        self.quin_path = join(ROOT, ns.quin_path or DEFAULT_QUIN)
        if ns.frequency:
            # such frequency based
            self.words = \
                rua.FrequencyBasedQuinDeque(*rua.WORD_LIST, step=ns.step)
        else:
            self.words = rua.QuinDeque(*rua.WORD_LIST)

    def setup(self):
        if self.tty.pretty:
            # stdout is a tty, load Shibe and calculate how wide he is
            quin = self.load_quin()
            max_quin = max(map(clean_len, quin))
        else:
            # stdout is being piped and we should not load Shibe
            quin = []
            max_quin = 15

        if self.tty.width < max_quin:
            # Shibe won't fit, so abort.
            sys.stderr.write('guna！这么小的终端\n')
            sys.stderr.write('没有猛男能在 {0} 列下存在\n'.format(max_quin))
            sys.exit(1)

        # Check for prompt height so that we can fill the screen minus how high
        # the prompt will be when done.
        prompt = os.environ.get('PS1', '').split('\n')
        line_count = len(prompt) + 1

        # Create a list filled with empty lines and Shibe at the bottom.
        fill = range(self.tty.height - len(quin) - line_count)
        self.lines = ['\n' for x in fill]
        self.lines += quin

        # Try to fetch data fed thru stdin
        had_stdin = self.get_stdin_data()

        # Get some system data, but only if there was nothing in stdin
        if not had_stdin:
            self.get_real_data()

        # Apply the text around Shibe
        self.apply_text()

    def apply_text(self):
        """
        Apply text around quin

        """

        # Calculate a random sampling of lines that are to have text applied
        # onto them. Return value is a sorted list of line index integers.
        linelen = len(self.lines)
        affected = sorted(random.sample(range(linelen), int(linelen / 3.5)))

        for i, target in enumerate(affected, start=1):
            line = self.lines[target][self.tty.width-57:]
            line = re.sub('\n', ' ', line)

            word = self.words.get()

            # If first or last line, or a random selection, use standalone rua.
            if i == 1 or i == len(affected) or random.choice(range(20)) == 0:
                word = 'rua'

            # Generate a new QuinMessage, possibly based on a word.
            self.lines[target] = QuinMessage(self, line, word).generate()

    def load_quin(self):
        """
        Return pretty ASCII Shibe.

        rua

        """

        if self.ns.no_shibe:
            return ['']

        with open(self.quin_path) as f:
            if sys.version_info < (3, 0):
                if locale.getpreferredencoding() == 'UTF-8':
                    quin_lines = [' '*(self.tty.width-57) + l.decode('utf-8') for l in f.xreadlines()]
                else:
                    # encode to printable characters, leaving a space in place
                    # of untranslatable characters, resulting in a slightly
                    # blockier quin on non-UTF8 terminals
                    quin_lines = [
                        ' '*(self.tty.width-57) + 
                        l.decode('utf-8')
                        .encode(locale.getpreferredencoding(), 'replace')
                        .replace('?', ' ')
                        for l in f.xreadlines()
                    ]
            else:
                quin_lines = [' '*(self.tty.width-57) + l for l in f.readlines()]
            return quin_lines

    def get_real_data(self):
        """
        Grab actual data from the system

        """

        ret = []
        username = os.environ.get('USER')
        if username:
            ret.append(username)

        editor = os.environ.get('EDITOR')
        if editor:
            editor = editor.split('/')[-1]
            ret.append(editor)

        # OS, hostname and... architechture (because lel)
        if hasattr(os, 'uname'):
            uname = os.uname()
            ret.append(uname[0])
            ret.append(uname[1])
            ret.append(uname[4])

        # Grab actual files from $HOME.
        files = os.listdir(os.environ.get('HOME'))
        if files:
            ret.append(random.choice(files))

        # Grab some processes
        ret += self.get_processes()[:2]

        # Prepare the returned data. First, lowercase it.
        # If there is unicode data being returned from any of the above
        # Python 2 needs to decode the UTF bytes to not crash. See issue #45.
        func = str.lower
        if sys.version_info < (3,):
            func = lambda x: str.lower(x).decode('utf-8')

        self.words.extend(map(func, ret))

    def filter_words(self, words, stopwords, min_length):
        return [word for word in words if
                len(word) >= min_length and word not in stopwords]

    def get_stdin_data(self):
        """
        Get words from stdin.

        """

        if self.tty.in_is_tty:
            # No pipez found
            return False

        if sys.version_info < (3, 0):
            stdin_lines = (l.decode('utf-8') for l in sys.stdin.xreadlines())
        else:
            stdin_lines = (l for l in sys.stdin.readlines())

        rx_word = re.compile("\w+", re.UNICODE)

        # If we have stdin data, we should remove everything else!
        self.words.clear()
        word_list = [match.group(0)
                     for line in stdin_lines
                     for match in rx_word.finditer(line.lower())]
        if self.ns.filter_stopwords:
            word_list = self.filter_words(
                word_list, stopwords=rua.STOPWORDS,
                min_length=self.ns.min_length)

        self.words.extend(word_list)

        return True

    def get_processes(self):
        """
        Grab a shuffled list of all currently running process names

        """

        procs = set()

        try:
            # POSIX ps, so it should work in most environments where quin would
            p = sp.Popen(['ps', '-A', '-o', 'comm='], stdout=sp.PIPE)
            output, error = p.communicate()

            if sys.version_info > (3, 0):
                output = output.decode('utf-8')

            for comm in output.split('\n'):
                name = comm.split('/')[-1]
                # Filter short and weird ones
                if name and len(name) >= 2 and ':' not in name:
                    procs.add(name)

        finally:
            # Either it executed properly or no ps was found.
            proc_list = list(procs)
            random.shuffle(proc_list)
            return proc_list

    def print_quin(self):
        for line in self.lines:
            if sys.version_info < (3, 0):
                line = line.encode('utf8')
            sys.stdout.write(line)
        sys.stdout.flush()


class QuinMessage(object):
    """
    A randomly placed and randomly colored message

    """

    def __init__(self, quin, occupied, word):
        self.quin = quin
        self.tty = quin.tty
        self.occupied = occupied
        self.word = word

    def generate(self):
        if self.word == 'rua':
            # Standalone rua. Don't apply any prefixes or suffixes.
            msg = self.word
        else:
            # Add a prefix.
            msg = '{0}{1}'.format(rua.PREFIXES.get(), self.word)

            # Seldomly add a suffix as well.
            if random.choice(range(15)) == 0:
                msg += ' {0}'.format(rua.SUFFIXES.get())

        # Calculate the maximum possible spacer
        zh = sum(unicodedata.east_asian_width(x) in ('F', 'W') for x in msg)        
        interval = self.tty.width - onscreen_len(msg) - zh
        interval -= clean_len(self.occupied)

        if interval < 1:
            # The interval is too low, so the message can not be shown without
            # spilling over to the subsequent line, borking the setup.
            # Return the quin slice that was in this row if there was one,
            # and a line break, effectively disabling the row.
            return self.occupied + "\n"

        # Apply spacing
        msg = '{0}{1}'.format(' ' * random.choice(range(interval)), msg)
        msg = msg.ljust(self.tty.width-57-zh)[-(self.tty.width-57-zh):]

        if self.tty.pretty:
            # Apply pretty ANSI color coding.
            msg = '\x1b[1m\x1b[38;5;{0}m{1}\x1b[39m\x1b[0m'.format(
                rua.COLORS.get(), msg
            )

        # Line ends are pretty cool guys, add one of those.
        return '{0}{1}\n'.format(msg, self.occupied)


class TTYHandler(object):
    def setup(self):
        self.height, self.width = self.get_tty_size()
        self.in_is_tty = sys.stdin.isatty()
        self.out_is_tty = sys.stdout.isatty()

        self.pretty = self.out_is_tty
        if sys.platform == 'win32' and os.getenv('TERM') == 'xterm':
            self.pretty = True

    def _tty_size_windows(self, handle):
        try:
            from ctypes import windll, create_string_buffer

            h = windll.kernel32.GetStdHandle(handle)
            buf = create_string_buffer(22)

            if windll.kernel32.GetConsoleScreenBufferInfo(h, buf):
                left, top, right, bottom = struct.unpack('4H', buf.raw[10:18])
                return right - left + 1, bottom - top + 1
        except:
            pass

    def _tty_size_linux(self, fd):
        try:
            import fcntl
            import termios

            return struct.unpack(
                'hh',
                fcntl.ioctl(
                    fd, termios.TIOCGWINSZ, struct.pack('hh', 0, 0)
                )
            )
        except:
            return

    def get_tty_size(self):
        """
        Get the current terminal size without using a subprocess

        http://stackoverflow.com/questions/566746
        I have no clue what-so-fucking ever over how this works or why it
        returns the size of the terminal in both cells and pixels. But hey, it
        does.

        """
        if sys.platform == 'win32':
            # stdin, stdout, stderr = -10, -11, -12
            ret = self._tty_size_windows(-10)
            ret = ret or self._tty_size_windows(-11)
            ret = ret or self._tty_size_windows(-12)
        else:
            # stdin, stdout, stderr = 0, 1, 2
            ret = self._tty_size_linux(0)
            ret = ret or self._tty_size_linux(1)
            ret = ret or self._tty_size_linux(2)

        return ret or (25, 80)


def clean_len(s):
    """
    Calculate the length of a string without it's color codes

    """

    s = re.sub(r'\x1b\[[0-9;]*m', '', s)

    return len(s)


def onscreen_len(s):
    """
    Calculate the length of a unicode string on screen,
    accounting for double-width characters

    """

    if sys.version_info < (3, 0) and isinstance(s, str):
        return len(s)

    length = 0
    for ch in s:
        length += 2 if unicodedata.east_asian_width(ch) == 'W' else 1

    return length


def setup_arguments():
    parser = argparse.ArgumentParser('quin')

    parser.add_argument(
        '--shibe',
        help='rua shibe file',
        dest='quin_path',
        choices=os.listdir(ROOT)
    )

    parser.add_argument(
        '--no-shibe',
        action="store_true",
        help="rua no quin show :("
    )

    parser.add_argument(
        '-f', '--frequency',
        help='such frequency based',
        action='store_true'
    )

    parser.add_argument(
        '--step',
        help='beautiful step',  # how much to step
        #  between ranks in FrequencyBasedQuinDeque
        type=int,
        default=2,
    )

    parser.add_argument(
        '--min_length',
        help='pretty minimum',  # minimum length of a word
        type=int,
        default=1,
    )

    parser.add_argument(
        '-s', '--filter_stopwords',
        help='many words lol',
        action='store_true'
    )

    parser.add_argument(
        '-mh', '--max-height',
        help='such max height',
        type=int,
    )

    parser.add_argument(
        '-mw', '--max-width',
        help='such max width',
        type=int,
    )
    return parser


def main():
    tty = TTYHandler()
    tty.setup()

    parser = setup_arguments()
    ns = parser.parse_args()
    if ns.max_height:
        tty.height = ns.max_height
    if ns.max_width:
        tty.width = ns.max_width

    try:
        shibe = Quin(tty, ns)
        shibe.setup()
        shibe.print_quin()

    except (UnicodeEncodeError, UnicodeDecodeError):
        # Some kind of unicode error happened. This is usually because the
        # users system does not have a proper locale set up. Try to be helpful
        # and figure out what could have gone wrong.
        traceback.print_exc()
        print()

        lang = os.environ.get('LANG')
        if not lang:
            print('rua error: broken $LANG, so fail')
            return 3

        if not lang.endswith('UTF-8'):
            print(
                "rua error: locale '{0}' is not UTF-8.  ".format(lang) +
                "quin needs UTF-8 to print Shibe.  Please set your system to "
                "use a UTF-8 locale."
            )
            return 2

        print(
            "rua error: Unknown unicode error.  Please report at "
            "https://github.com/journey-ad/quin/issues and include output from "
            "/usr/bin/locale"
        )
        return 1


# rua very main
if __name__ == "__main__":
    sys.exit(main())
