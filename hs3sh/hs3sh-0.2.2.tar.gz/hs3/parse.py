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
from collections import OrderedDict

# Constants
PERMISSIONS = ['FULL_CONTROL', 'WRITE', 'WRITE_ACP', 'READ', 'READ_ACP']
B_CANNED = ['private', 'public-read', 'public-read-write', 'authenticated-read']
O_CANNED = ['private', 'public-read', 'public-read-write', 'aws-exec-read',
            'authenticated-read', 'bucket-owner-read',
            'bucket-owner-full-control']

BUCKET = 'b'
GRANT = 'g'
OBJECT = 'o'
SET = 's'

class AclReturn(object):
    'class holding the result of parse_acl'
    def __init__(self):
        self.isbucket = None    # True, if bucket, False if Object
        self.name = None        # the bucket's or object's name
        self.flags = []         # given flags
        self.pairs = []         # list of tuples of acl pairs
        self.canned = None      # a canned ACL

    def __str__(self):
        ret = []
        ret.append(' type: {}'
                   .format(None if self.isbucket == None else 'bucket' if self.isbucket else 'object'))
        ret.append(' name: {}'.format(self.name))
        ret.append('flags: {}'.format(self.flags))
        ret.append('grant: {}'.format(self.pairs))

        return '\n'.join(ret)


def parse_acl(args, debug=False):
    '''
    Parse the parameters for the acl command

    :param args:    a string holding the entire parameters
    :param debug:   turn of shlex debug output of True
    :return:        an AclReturn object
    '''
    s = shlex.shlex(args, posix=True)
    s.debug = 1 if debug else 0

    flags  = 'bgos'   # b=bucket, g = grant, o = object, s=set

    isfirst = newpair = True
    isflags = False
    p1 = p2 = None
    ret = AclReturn()

    while True:
        t = s.get_token()

        # end if there's no more token
        if not t:
            break

        # handle flags
        if isflags:
            for f in t:
                if f in flags:
                    ret.flags.append(f)
                    if f in [BUCKET, OBJECT]:
                        if ret.isbucket != None:
                            raise ValueError('-{} and -{} are exclusive'
                                             .format(BUCKET,OBJECT))
                        else:
                            ret.isbucket = True if f == BUCKET else False
                    elif f == SET:
                        x = s.get_token()
                        if x in (B_CANNED if ret.isbucket else O_CANNED):
                            ret.canned = x
                        else:
                            raise ValueError('argument following -{} ({}) must be one of {}'
                                             .format(SET, x, (B_CANNED if ret.isbucket else O_CANNED)))

                else:
                    raise ValueError('flag "{}" not acceptable'.format(f))
            isflags = False
            continue
        if t == '-':
            isflags = True
            continue

        # handle the first token (should be bucket or /object)
        if isfirst:
            # ret.isbucket = True if not t.startswith('/') else False
            ret.name = t
            isfirst = False
            continue

        # handle value pairs
        # if we find a comma or a semicolon, a new pair starts
        if t in [',', ';']:
            newpair = True
            p1 = p2 = None
            continue

        if newpair:
            if not p1:
                p1 = t
            elif not p2:
                if not t.upper() in PERMISSIONS:
                    raise ValueError("'{}':'{}'.upper() not in {}"
                                     .format(p1, t, PERMISSIONS))
                p2 = t.upper()
            else:
                raise ValueError('acl settings have to be grantee / permission'
                                 ' pairs ({} {} - bad: {})'.format(p1, p2, t))
            if p1 and p2:
                ret.pairs.append((p1,p2))
            continue

        # as we should never end up here, RAISE!
        raise Exception('we should never have gotten to this point...')

    # Not having 'o' or 'b' in flags is an error...
    if ret.isbucket == None:
        raise ValueError('use -{}|-{} to identify bucket or object'
                         .format(BUCKET,OBJECT))

    elif not GRANT in ret.flags and ret.pairs:
        raise ValueError('use -{} if you want to set ACLs'.format(GRANT))

    elif GRANT in ret.flags and not ret.pairs:
        raise ValueError('-{} requires user/permission pair(s)'.format(GRANT))


    return ret



class ParamReturn(object):
    'class holding the result of a paramcheck'

    PIPE = '|'          # output shall be piped
    OUTFILE = '>'       # output shall be written to a file
    EXTENDFILE = '>>'   # output shall extend a file

    def __init__(self):
        self.flags = []         # given flags
        self.args  = []         # remainings parameter
        self.metadict = {}      # metadata pairs
        self.redir_type = None  # either PIPE, OUTFILE or EXTENDFILE
        self.redir_arg = None   # either the outfile or the command to pipe to

    def __str__(self):
        ret = []
        ret.append('flags     : {}'.format(self.flags))
        ret.append('args      : {}'.format(self.args))
        ret.append('metadict  : {}'.format(self.metadict))
        ret.append('redir_type: {}'.format(self.redir_type))
        ret.append('redir_arg : {}'.format(self.redir_arg))

        return '\n'.join(ret)


def paramcheck(arg, flags='', meta=False):
    '''
    Check the parameters given to a command:
        [-flags | -f -l -a -g -s] arg [arg ...] [meta:data ...]
    :param arg:     the parameter string given to the cmd
    :param flags:   allowed flags
    :param meta:    if we shall look for metadata pairs
    :return:        a ParamReturn object
    '''
    ret = ParamReturn()
    if not arg:     # dummy on empty input
        return ret

    # first let's see if we need to look for pipe/outfile
    try:
        if arg.find(ParamReturn.EXTENDFILE) != -1:
            ret.redir_type = ParamReturn.EXTENDFILE
            arg, ret.redir_arg = arg.split(ParamReturn.EXTENDFILE)
            ret.redir_arg = ret.redir_arg.strip()
        elif arg.find(ParamReturn.OUTFILE) != -1:
            ret.redir_type = ParamReturn.OUTFILE
            arg, ret.redir_arg = arg.split(ParamReturn.OUTFILE)
            ret.redir_arg = ret.redir_arg.strip()
        elif arg.find(ParamReturn.PIPE) != -1:
            ret.redir_type = ParamReturn.PIPE
            arg, ret.redir_arg = arg.split(ParamReturn.PIPE)
            ret.redir_arg = ret.redir_arg.strip()
    except Exception as e:
        raise ValueError('parsing redirction failed ({}'.format(e))

    # crawl through the parameters
    inflags = searchargs = True
    for pa in arg.split():
        if inflags:     # make sure the flags given are allowed
            if pa.startswith('-'):
                for i in pa[1:]:
                    if i in flags:
                        ret.flags.append(i)
                    else:
                        raise ValueError('invalid flag: -{}'.format(i))
            else:
                inflags = False     # first param w/o '-' ends flag processing

        if not inflags: # now its about the params and metapairs
            if searchargs:
                if len(pa.split(':')) == 2:
                    searchargs = False
                else:
                    ret.args.append(pa)

            if not searchargs and meta:
                pas = pa.split(':')
                if len(pas) != 2:
                    raise ValueError('invalid metapair: {}'.format(pa))
                else:
                    ret.metadict[pas[0]] = pas[1]

    return ret

def aclcleanup(owner, grants):
    '''
    Cleanup the received dicts to make sure they comply to the XSD found at
    https://admin.<yourhcp>.<yourdomain>.<tld>/static/xsd/AmazonS3.xsd

    :param owner:   the owner dict
    :param grants:  the grants dict
    :returns:       cleaned (owner, grant) as OrderedDicts
    '''
    logger = logging.getLogger(__name__)
    _owner = OrderedDict()
    _grants = []

    # Cleanup owner
    for i in ['ID', 'DisplayName']:     # order is critical!
        if i in owner.keys():
            _owner[i] = owner[i]
    logger.debug('Owner = {}'.format(_owner))

    for i in grants:
        _g = OrderedDict()
        _g['Grantee'] = OrderedDict()
        for j in [ 'Type', 'ID', 'DisplayName', 'EmailAddress','URI']: # order is critical!
            if j in i['Grantee'].keys():
                _g['Grantee'][j] = i['Grantee'][j]

        _g['Permission'] = i['Permission']
        logger.info('Grantee = {}'.format(_g))
        _grants.append(_g)

    return(_owner, _grants)
