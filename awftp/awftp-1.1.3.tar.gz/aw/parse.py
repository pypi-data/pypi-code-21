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

import logging
import shlex
from collections import namedtuple

from urllib.parse import urlparse, splituser, splitpasswd


class ParamReturn(object):
    'class holding the result of a paramcheck'

    PIPE = '|'          # output shall be piped
    OUTFILE = '>'       # output shall be written to a file
    EXTENDFILE = '>>'   # output shall extend a file

    def __init__(self):
        self.flags = []         # given flags
        self.args  = []         # remainings parameter

    def __str__(self):
        ret = []
        ret.append('flags     : {}'.format(self.flags))
        ret.append('args      : {}'.format(self.args))

        return '\n'.join(ret)


def paramcheck(arg, flags=''):
    '''
    Check the parameters given to a command:
        [-flags | -flags] arg [arg ...] [\| command | > file | >> file]
    :param arg:     the parameter string given to the cmd
    :param flags:   allowed flags
    :return:        a ParamReturn object
    '''
    ret = ParamReturn()
    if not arg:     # dummy on empty input
        return ret

    # parse the arguments given
    for i in shlex.split(arg):
        # filter out the flags, if any
        if i.startswith('-'):
            for j in i[1:]:
                if j in flags:
                    ret.flags.append(j)
                else:
                    raise ValueError('invalid flag: -{}'.format(j))
        else:
            ret.args.append(i)

    return ret

def convertaw(tgt, nossl=False):
    """
    Convert the AW server given by the user into its components.

    :param tgt:     the aw server given by the user
    :param nossl:   disable SSL if True
    :return:        a named tuple holding the components
    """
    logger = logging.getLogger(__name__)
    awconnect = namedtuple('awconnect', ['scheme','netloc','user','password'])

    if tgt.startswith('http://') and not nossl:
        tgt.replace('http://', 'https://', 1)

    if not tgt.startswith('https://'):
        tgt = ('http://' if nossl else 'https://') + tgt

    logger.debug('connection target = {}'.format(tgt))
    z = urlparse(tgt)
    logger.debug('    parsed as {}'.format(z))
    s_user, s_netloc = splituser(z.netloc)
    if s_user:
        s_user, s_password = splitpasswd(s_user)
    else:
        s_password = None

    ret = awconnect(scheme=z.scheme, netloc=s_netloc,
                    user=s_user, password=s_password)
    logger.debug('{}'.format(ret))

    return ret
