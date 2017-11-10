#!/usr/bin/env python3

# Copyright (C) 2017  Michał Góral
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import argparse
import asyncio
import signal
import unicodedata

try:
    import marquee._version as _version
    __version__ = _version.version
except ImportError:
    __version__ = '0.x'


loop = asyncio.get_event_loop()
next_display = None
prev_len = 0


def parse_args():
    parser = argparse.ArgumentParser(
        description='Scroll text from standard input.')

    parser.add_argument('-F', '--format', default='{}',
            help='Format string (default: "{}"). Only {} will be scrolled.')

    parser.add_argument('-n', '--newline', action='store_true',
        help='add a newline after each update')

    parser.add_argument('-l', '--length', type=int, default=10,
        help='length of text scroll')

    parser.add_argument('-f', '--fill', nargs='?', const=' ',
        help='fill shorter text to a given text length (optionally with a '
             'given character)')

    parser.add_argument('-s', '--separator', default=' -- ',
        help='text separator')

    parser.add_argument('-d', '--delay', type=float, default=0.4,
        help='delay between scroll updates')

    parser.add_argument('-S', '--scroll', action='store_true',
        help='always scroll')

    parser.add_argument('-r', '--reverse', action='store_true',
        help='reverse scroll (left-to-right)')

    parser.add_argument('--version', action='version',
        version='%(prog)s %(v)s' % dict(prog='%(prog)s', v=__version__))

    return parser.parse_args()


def excerpt(text, length):
    '''Returns part of text up to a given length. It takes into account visual
    length of unicode characters.'''
    EMPTY = ''
    SPACE = ' '  # what are we living for?

    vchars = []

    for ch in text:
        if len(vchars) >= length:
            break

        if unicodedata.east_asian_width(ch) in ('W', 'F'):
            if length - len(vchars) >= 2:
                vchars.extend((ch, EMPTY))
            elif length - len(vchars) == 1:
                vchars.append(SPACE)
        else:
            vchars.append(ch)
    return ''.join(vchars)


def vlen(text):
    vl = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ('W', 'F'):
            vl += 2
        else:
            vl += 1
    return vl


def rotate(text, args, start=False):
    global next_display
    global prev_len

    vl = vlen(text)

    if start:
        if args.fill and vl < args.length:
            text += (args.length - vl) * args.fill[0]
        elif args.separator and (vl > args.length or args.scroll):
            text += args.separator

    display = args.format.format(excerpt(text, args.length))

    # reset old characters
    if start:
        curr_len = vlen(display)
        if curr_len < prev_len:
            display += ' ' * (prev_len - curr_len)
        prev_len = curr_len

    if args.newline:
        print(display, flush=True)
    else:
        print(display, end='\r', flush=True)

    # scroll
    if vl > args.length or args.scroll:
        if args.reverse:
            ntext = text[-1] + text[:-1]
        else:
            ntext = text[1:] + text[0]
    else:
        ntext = text
    next_display = loop.call_later(args.delay, rotate, ntext, args)


def read_stdin(args):
    global next_display

    def _stop_reading():
        loop.remove_reader(sys.stdin.fileno())
        if not next_display:
            loop.stop()

    # not sure how this would happen, but let's check it anyway
    if sys.stdin.closed:
        return _stop_reading()

    line = sys.stdin.readline()

    # EOT/EOF (e.g. for redirected FIFO pipes)
    if not line:
        return _stop_reading()

    # remove a trailing newline
    line = line.splitlines()[0]

    if next_display:
        next_display.cancel()
    next_display = loop.call_soon(rotate, line, args, True)


def sigint_handler():
    loop.stop()


def main():
    args = parse_args()

    loop.add_signal_handler(signal.SIGINT, sigint_handler)
    loop.add_reader(sys.stdin.fileno(), read_stdin, args)
    loop.run_forever()

    return 0
