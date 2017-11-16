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

import sys
import argparse
import io
from os.path import split
from textwrap import wrap
from click import secho
from time import sleep
from pprint import pprint
import requests

from version import Gvars
from aw.init import supportedapis, minapi_saml
from aw.parse import convertaw
from aw.exceptions import IdpListError

def parseargs():
    """
    args - build the argument parser, parse the command line and
           run the respective functions.
    """

    mainparser = argparse.ArgumentParser()
    mainparser.add_argument('--version', action='version',
                            version="%(prog)s: {0}\n".format(Gvars.Version))
    mainparser.add_argument('-d', dest='debug', action='store_true',
                            default=False,
                            help='enable debugging output '
                                 '(ugly and a bit chatty!)')
    mainparser.add_argument('--idp', dest='idps', action='store_true',
                            default=False,
                            help='list available identity providers and exit')
    mainparser.add_argument('--api', dest='api', choices=supportedapis,
                            default=None,
                            help='force using a specific FS&S API version')
    mainparser.add_argument('--nossl', dest='nossl', action='store_true',
                            default=False,
                            help='disable SSL (most likely, this won\'t work, '
                                 'as HCP Anywhere requires SSL encryption)')
    mainparser.add_argument('--saml', dest='saml', default=None,
                            help='use a specifc SAML IDP')
    mainparser.add_argument(dest='aw_server', nargs='?', default='',
                            help='the HCP Anywhere system to connect '
                                 '([user[:password]@]anywhere.your.domain)')

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


def calcByteSize(nBytes, formLang=False):
    '''
    Return a given no. of Bytes in a human readable format.
    '''
    sz = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
    szl = ["Byte", "Kilobyte", "Megabyte", "Gigabyte", "Terabyte",
           "Petabyte", "Exabyte", "Zettabyte", "Yottabyte"]
    i = 0
    neg = False
    if nBytes < 0:
        neg = True
        nBytes *= -1

    while nBytes > 1023:
                    nBytes = nBytes / 1024
                    i = i + 1
    if neg:
        nBytes *= -1
    if formLang:
        return "{0:.2f} {1:>3}".format(nBytes, szl[i])
    else:
        return "{0:.2f} {1:>3}".format(nBytes, sz[i])


def splitfilename(path):
    """
    Intelligently (???) split off the file name from a path.

    :param path:    the path to handle
    :return:        the file name or an empty string if there's no name
    """
    return split(path)[1]


def _print(*args, err=False, nl='\n'):
    """
    Print strings, first line as it is, following lines wrapped to 78 chars.
    If err is set to True, output will go to stderr and colored red.

    :param string:  the string to print
    """

    # print('args = {}'.format(args))
    _frst = True
    for l in args:
        if _frst:
            _frst = False
        else:
            l = '\n'.join(wrap(l, initial_indent='    ',
                               subsequent_indent='    '))

        if err:
            secho(l, fg='red', err=True, nl=nl)
        else:
            secho(l, nl=nl)


def _(string, width):
    """
    Return the string cut to num characters.

    :param string:  the string to work on
    :param width:   the number of characters wanted
    :return:        the cut string
    """
    string = string or ''
    return string if len(string) <= width else string[:width - 3] + '...'


class MonitoredReader(io.BufferedReader):

    def __init__(self, file, callback=None):
        '''
        Open file and provide a buffered reader.
        
        :param file: the file to read... 
        '''
        super().__init__(open(file, 'rb'), buffer_size=16384)
        self.callback = callback

    def read(self, size=0):
        '''
        Read and return <size> bytes from the file.
        
        :param size:    the bytes to read, or all available data if zero
        :return:        at max. the requested bytes
        '''
        data = super().read(8192)
        self.callback(len(data))
        return data

    def peek(self, size=0):
        raise NotImplementedError('read1 not allowd here')

    def read1(self, size=0):
        raise NotImplementedError('read1 not allowd here')

def listidps(aw_server=None, nossl=False):
    """
    List the identity providers offered by HCP Anywhere.

    :param aw_server:   the HCP Anywhere server from command line
    :param nossl:       if no ssl shall be used
    """
    aw = convertaw(aw_server, nossl=nossl)

    if not aw.netloc:
        raise IdpListError('no HCP Anywhere server given')

    session = requests.Session()
    session.verify = False

    try:
        r = session.post('://'.join([aw.scheme, aw.netloc]) + '/fss/public/provider/list',
                         headers={'Accept': 'application/json',
                                  'Content-Type': 'application/json',
                                  'X-HCPAW-FSS-API-VERSION': minapi_saml})
    except Exception as e:
        raise IdpListError('LIST IDP error - {}'.format(e))
    else:
        if r.status_code != 200:
            raise IdpListError('LIST IDP error ({} - {})'
                               .format(r.status_code, r.reason))
        for _idp in r.json()['providers']:
            _print('{:16}   {:20}'.format(_idp['type'],
                                          _idp['name']))

