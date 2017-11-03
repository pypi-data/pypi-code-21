# The MIT License (MIT)
#
# Copyright (c) 2016-2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
from textwrap import wrap

from hs3 import init



def parseargs():
    """
    args - build the argument parser, parse the command line and
           run the respective functions.
    """

    mainparser = argparse.ArgumentParser()
    mainparser.add_argument('--version', action='version',
                            version="%(prog)s: {0}\n"
                            .format(init.Gvars.Version))
    mainparser.add_argument('-d', dest='debug', action='store_true',
                            default=False,
                            help='enable debugging output '
                                 '(ugly and very chatty!)')

    result = mainparser.parse_args()
    return result


def calctime(t):
    """
    Calculate a string 'H:M:S.ms' out of a given no. of seconds.
    """
    msec = int("{0:.2f}".format(t % 1)[2:])
    minute = int(t // 60)
    sec = int(t % 60)
    hour = int(minute // 60)
    minute = int(minute % 60)
    return "{0:02}:{1:02}:{2:02}.{3}".format(hour, minute, sec, msec)


def _print(*args, **kwargs):
    """
    Print strings, first line as it is, following lines wrapped to 78 chars.

    :param string:  the string to print
    """

    strings = ' '.join(args).split('\n')
    print(strings[0], **kwargs)
    lines = wrap('\n'.join(strings[1:]),
                 initial_indent='    ', subsequent_indent='    ')
    for l in lines:
        print(l, **kwargs)


def _(string, width):
    """
    Return the string cut to num characters.

    :param string:  the string to work on
    :param width:   the number of characters wanted
    :return:        the cut string
    """
    string = string or ''
    return string if len(string) <= width else string[:width - 3] + '...'


