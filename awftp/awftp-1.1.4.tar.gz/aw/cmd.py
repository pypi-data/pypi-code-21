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

import cmd
import logging
import os
import stat
from os.path import normpath, join, split
from glob import glob
import sys
import time
from urllib.parse import quote, urlparse
import requests
import click
from requests.packages.urllib3 import disable_warnings
from collections import OrderedDict
from json import dumps
from pprint import pprint
from bs4 import BeautifulSoup

from aw.exceptions import SamlAuthError
from aw.tools import (calctime, calcByteSize, splitfilename, _print, _,
                      MonitoredReader)
from aw.init import INTRO, no_redir_cmds, supportedapis
from aw.parse import paramcheck, convertaw
from aw.auth import samlauth

PIPE = '|'  # output shall be piped
OUTFILE = '>'  # output shall be written to a file
EXTENDFILE = '>>'  # output shall extend a file
S_IFDIR =  0o040000 # used to identify a directory...


# noinspection PyUnresolvedReferences
class Awftpshell(cmd.Cmd):
    intro = INTRO

    prompt = 'awftp> '

    def __init__(self, *args, target='', nossl=False, api=None, saml=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        # if awftp was called with an HCP Anywhere system, we split it up into
        # the various components later used to connect.
        if 'target':
            aw = convertaw(target, nossl=nossl)
            self.aw = aw.netloc
            self.scheme = aw.scheme
            self.user = aw.user
            self.password = aw.password
        else:
            self.aw = ''
            self.user = ''
            self.expires = ''
            self.scheme = 'http' if nossl else 'https'
        self.nossl = nossl
        self.logger = logging.getLogger(__name__)
        self._prompt = 'awftp> '
        self.preventopen = False
        self.connected = False  # indicates that we are connected
        self.api = '2.1.1'      # the API version we start with
        self.saml = saml        # the SAML IDP to use
        self.forceapi = api     # API version forced by the user
        self.progress = True    # per default, show a progress meter
        self.cwd = '/'
        self.snapshots = None   # available Restore Points
        self.snapshot = None    # the snapshot to use now
        self.links = None       # dict of existing links

    def cmdloop(self, intro=None):
        """
        This is to allow to interrupt running commands via KeyboardInterrupt
        (CTRL-C); this will kill the commandloop, so we make sure it is 
        restarted right away.
        """
        while True:
            try:
                super(Awftpshell, self).cmdloop(intro=intro)
                break
            except (KeyboardInterrupt, click.exceptions.Abort):
                _print("^C", err=True)
            except AttributeError as e:
                _print('error: invalid command...',
                       'hint: {}' .format(e), err=True)
            except requests.exceptions.ConnectionError as e:
                _print('error: lost connection to {} - try again to re-connect'
                       .format(self.aw,),
                       'hint: {}' .format(e), err=True)
            except BrokenPipeError as e:
                # In case we started an external command through a pipe, and
                # this one failed we end up with a broken pipe. We need to work
                # around this to get back into a stable state using stdout.
                _print('error: running external command failed',
                       'hint: {}' .format(e), err=True)
                self.postcmd(False, '')


    def preloop(self):
        # disable SSL certificate verification warning
        if not self.preventopen:
            self.preventopen = True
            self.intro = None
            disable_warnings()

            if self.aw and self.scheme:
                self.cmdqueue.append('open -x')

    def precmd(self, arg):
        """
        This overwrites the pre-command hook to strip off redirections from a
        command and sys.stdout accordingly accordingly.

        We are relying on everything being printed to sys.std. We realize
        redirections by simply mapping sys.stdout to a different file handle.

        :param arg:     the parameters given with the command
        :return:        the command w/o the redirection or an empty string
                        if parsing failed
        """

        # detect EOF
        if arg == 'EOF':
            return('bye')

        # first let's see if we need to look for pipe/outfile
        redir_type = redir_arg = None
        try:
            if arg.find(EXTENDFILE) != -1:
                redir_type = EXTENDFILE
                arg, redir_arg = arg.split(EXTENDFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(OUTFILE) != -1:
                redir_type = OUTFILE
                arg, redir_arg = arg.split(OUTFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(PIPE) != -1:
                redir_type = PIPE
                arg, redir_arg = arg.split(PIPE)
                redir_arg = redir_arg.strip()
        except Exception as e:
            _print('error: parsing redirction failed...',
                   'hint: {}'.format(e), err=True)
            return ''

        if redir_type and arg.split()[0] in no_redir_cmds:
            _print('error: no redirection for command "{}"...'
                  .format(arg.split()[0]), err=True)
            return ''

        if redir_type and not redir_arg:
            _print('error: redirection without arguments...', err=True)
            return ''

        if redir_type == PIPE:
            self.logger.debug('will pipe to "{}"'.format(redir_arg))
            try:
                sys.stdout = os.popen(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e), err=True)
                return ''
        elif redir_type == OUTFILE:
            self.logger.debug('will output to "{}"'.format(redir_arg))
            try:
                sys.stdout = open(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e), err=True)
                return ''
        elif redir_type == EXTENDFILE:
            self.logger.debug('will append to "{}"'.format(redir_arg))
            try:
                sys.stdout = open(redir_arg, 'a')
            except Exception as e:
                _print('redirection error...',
                       'hint: {}'.format(e), err=True)
                return ''

        return arg

    def postcmd(self, stop, line):
        """
        This overwrites the post-command hook to reset sys.stdout to what it
        should be after a command with redirection was executed.
        """

        # In case we started an external command through a pipe, and this one
        # failed we end up with a broken pipe. We need to work around this to
        # get back into a stable state using stdout.

        # make sure we flush the file handle to which sys.stdout points to at
        # the moment.
        try:
            print('', end='', flush=True)
        except BrokenPipeError:
            pass
        if sys.stdout != sys.__stdout__:
            try:
                sys.stdout.close()
            except BrokenPipeError:
                pass
            sys.stdout = sys.__stdout__
        return stop

    def emptyline(self):
        """Disable repetition of last command by pressing Enter"""
        pass

    def do_bye(self, args):
        'bye\n'\
        '    terminate awftp session and exit'
        self.logger.info('--> called "bye {}" --> forwarded to "quit"'
                         .format(args))
        return self.do_quit(args)

    def do_cd(self, args):
        'cd [remote-directory]\n'\
        '    Change remote working directory to remote-directory, if given,\n'\
        '    otherwise to /\n'
        self.logger.info('--> called "cd {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) > 1:
                _print('error: at max 1 parameter is allowed...',
                            err=True)
                return
            else:
                if len(para.args):
                    cwd = normpath(join(self.cwd, para.args[0]))
                else:
                    cwd = '/'

                # test the new current directory for existence
                req = {'path': cwd}

                r = self.session.post('://'.join(
                    [self.scheme, self.aw]) + '/fss/public/path/info/get',
                                      json=req)
                if r.status_code == 200:
                    if self.snapshot:
                        # As we can't be sure that a folder exists in a
                        # snapshot, we do a workaround and try to list the
                        # folder within the snapshot to be sure that it exists.
                        req = {'path': cwd,
                               'viewAtTime': self.snapshot,
                               'pageSize': 1}

                        r = self.session.post('://'.join(
                            [self.scheme,
                             self.aw]) + '/fss/public/folder/entries/list',
                                              json=req)
                        if r.status_code != 200:
                            _print('CWD to {} failed ({} {})'
                                   .format(cwd, r.status_code, r.reason),
                                   err=True)
                            return

                    self.cwd = cwd
                    _print('CWD command successful.')
                else:
                    _print('CWD to {} failed ({} {})'
                           .format(cwd, r.status_code, r.reason),
                           err=True)

    def do_cdup(self, args):
        'cdup\n'\
        '    change remote working directory to parent directory.'
        self.logger.info('--> called "cdup {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        if self.cwd == '/':
            _print('CWD command successful.')
        else:
            cwd = normpath(join(self.cwd, '..'))
            req = {'path': cwd}
            r = self.session.post('://'.join(
                [self.scheme, self.aw]) + '/fss/public/path/info/get',
                                  json=req)
            if r.status_code == 200:
                self.cwd = cwd
                _print('CWD command successful.')
            else:
                _print('CWD to {} failed ({} {})'
                       .format(cwd, r.status_code, r.reason),
                       err=True)

    def do_clear(self, args):
        'clear\n'\
        '    clear the screen'
        self.logger.info('--> called "clear {}"'.format(args))
        click.clear()


    def do_close(self, args):
        'close\n'\
        '    terminate the session with HCP Anywhere, but stay in awftp'
        self.logger.info('--> called "close {}"'.format(args))
        if self.connected:
            self.session.close()
            self.session = None
            self.connected = False
            self.expires = ''
            self.password = ''
            self.prompt = self._prompt
            _print('Disconnected from {}.'.format(self.aw))
        else:
            _print('error: not connected', err=True)


    def do_dir(self, args):
        'dir [-1] [-d] [remote-path]\n'\
        '    list contents of remote path\n'\
        '    -1 display one name per line\n'\
        '    -d show deleted files, too'
        self.logger.info('--> called "dir {}" --> forwarded to "ls"'
                         .format(args))
        self.do_ls(args)

    def do_exit(self, args):
        'exit\n'\
        '    terminate awftp session and exit'
        self.logger.info('--> called "exit {}" --> forwarded to "quit"'
                         .format(args))
        return self.do_quit(args)

    def _do_find300(self, args):
        'find [-1] [-d] [-s <snap_id>] <pattern>\n' \
        '    search for files/folders containing <pattern> in their name,\n'\
        '    starting at the current directory (in realtime or the active\n'\
        '    snapshot)\n'\
        '    -1 display one name per line\n'\
        '    -d search for deleted files, too\n'\
        '    -s search in specific snapshot <snap_id> (from snap -l)\n'\
        '\n'\
        '    <pattern> is the string to search for, min. 3 characters'
        self.logger.info('--> called "find300 {}" --> forwarded to "search300"'
                         .format(args))
        self.do_search(args)

    def do_get(self, args):
        'get remote-file [local-file]\n'\
        '    receive file\n'
        self.logger.info('--> called "get {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) not in [1, 2]:
                _print('error: one or two parameters are required...',
                       err=True)
                return
            elif len(para.args) == 1:
                src = normpath(join(self.cwd, para.args[0]))
                tgt = splitfilename(para.args[0])
            else:  # len(para.args) == 2
                src = normpath(join(self.cwd, para.args[0]))
                tgt = para.args[1]

        self.logger.debug('get from src = {} to tgt = {}'.format(src, tgt))

        # get the source file size
        meta = self.__getmeta(src)
        if not meta:
            _print('error: can\'t get hold of {}'.format(src), err=True)
            return
        _size = meta['size'] or 0
        _etag = meta['etag']

        req = {'path': src,
               'etag': _etag,
                'forceDownload': True
               }

        try:
            with open(tgt, 'wb') as tgthdl:
                r = self.session.post('://'.join(
                    [self.scheme, self.aw]) + '/fss/public/file/stream/read',
                                      json=req,
                                      headers={
                                          'Accept': 'application/octet-stream'},
                                      stream=self.progress)
                if r.status_code == 200:
                    self.logger.debug('GET {} to {} successful.'
                                      .format(src, tgt))
                    if self.progress:
                        with click.progressbar(label="GET {} ".format(src),
                                               length=_size) as bar:
                            for chunk in r.iter_content(chunk_size=None):
                                bar.update(len(chunk))
                                tgthdl.write(chunk)
                    else:
                        tgthdl.write(r.content)
                    _print('GET command successful.')
                else:
                    _print('GET {} {} failed ({} {}){}'
                           .format(src, tgt, r.status_code, r.reason,
                                   '\n'+r.text if r.status_code == 400 else ''),
                           err=True)
        except Exception as e:
            _print('GET command failed...', 'hint: {}'.format(e), err=True)
            return

    def _do_hist300(self, args):
        'hist <file>\n'\
        '    show the history of a file'
        self.logger.info('--> called "hist300 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) != 1:
                _print('error: exactly one parameter is allowed...',
                       err=True)
                return

        req = {'path': normpath(join(self.cwd, para.args[0])),
               # ok, we should paginate, but we shpuld be fine with this...
               'pageSize': 1000,
               'showPrivate': 'true'
               }

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/file/version/list',
                              json=req)
        if r.status_code == 200:
            res = r.json()
        else:
            self.logger.debug('HIST failed ({} {})'.format(r.status_code,
                                                              r.reason))
            return None

        for i in res['entries']:
            _print('{:>12}  {}  -  {} ({})'
                   .format(calcByteSize(i['size']),
                           time.strftime('%Y/%m/%d %H:%M:%S',
                                         time.localtime(i['timestamp'] / 1000)),
                           i['event'].split('.')[-1],
                           i['username']))

    def do_lcd(self, args):
        'lcd [local-directory]\n'\
        '    change the local working directory to local-directory (or to\n'\
        '    home directory, if local-directory isn\'t given)'
        self.logger.info('--> called "lcd {}"'.format(args))
        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) > 1:
                _print('error: at max 1 parameter is allowed...',
                       err=True)
                return
            else:
                newd = para.args[0] if len(para.args) else os.path.expanduser("~")
                try:
                    os.chdir(newd)
                except Exception as e:
                    _print('LCWD failed: {}'.format(e), err=True)
                    return
                _print('LCWD command{}successful.'
                       .format(' to {} '.format(newd) if not len(para.args) else ' '))

    def _do_link211(self, args):
        'link [-a] -i|-p -r|-u|-ru [expiration_days] file|folder\n'\
        '    create a link to share a file or folder\n'\
        '    -a add an access code\n'\
        '    -i force creating an internal link\n'\
        '    -p force creating a public link\n'\
        '    -r the link is good for view and download of files\n'\
        '    -u the link allows to upload into the linked folder\n'\
        '       (at least one of -r and -u is required)\n'\
        '    if expiration_date (an integer) is not given, a link with the\n'\
        '    default expiration will be created\n'
        self.logger.info('--> called "link211 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return
        elif self.snapshot:
            _print('can\'t link to a file within a snapshot',
                   err=True)
            return

        try:
            para = paramcheck(args, flags='aipru')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if 'i' in para.flags and 'p' in para.flags:
                _print('error: you can\'t force both internal and public...',
                       err=True)
                return
            elif len(para.args) < 1 or len(para.args) > 2:
                _print('error: one or two parameter required...',
                       err=True)
                return
            elif not 'r' in para.flags and not 'u' in para.flags:
                _print('error: at least one of -r and -u is required...',
                       err=True)
                return

            req = {'permissions': []}
            # care for expiration days, if given
            if len(para.args) == 2:
                try:
                    req['expirationDays'] = int(para.args[0])
                except ValueError:
                    _print('error: expiration_days needs to be integer...',
                           err=True)
                    return

            # care for the path to link
            if para.args[-1].startswith('/'):
                req['path'] = para.args[-1]
            else:
                req['path'] = normpath(join(self.cwd, para.args[-1]))

            # care for the flags
            if 'a' in para.flags:
                req['accessCode'] = True
            if 'i' in para.flags:
                req['public'] = False
            if 'p' in para.flags:
                req['public'] = True
            if 'r' in para.flags:
                req['permissions'].append('READ')
            if 'u' in para.flags:
                req['permissions'].append('UPLOAD')

            r = self.session.post('://'.join(
                [self.scheme, self.aw]) + '/fss/public/link/create',
                                  json=req)
            if r.status_code == 200:
                res = r.json()
                _print('Link for {} created:'.format(res['path']))
                _print('    link:          {}'.format(res['url']))
                _print('    visibility:    {}'
                            .format('public' if res['public'] else 'internal'))
                _print('    accessCode:    {}'
                       .format(
                    res['accessCode'] if 'accessCode' in res.keys() else'-'))
                _print('    permission(s): {}'
                            .format(','.join(res['permissions'])))
                _print('    expires:       {}'
                       .format(time.strftime('%Y/%m/%d %H:%M:%S',
                                             time.localtime(res[
                            'expirationDate'] / 1000))
                                if 'expirationDate' in res else 'unlimited'))
                # now we delete the list of links to make sure that the
                # user will always be forced to get a actual list
                self.links = None
            elif r.status_code == 403:
                _print('CLNK failed for {} ({} {})\nuse the "user" '
                       'command to check your permissions...'
                       .format(req['path'], r.status_code, r.reason), err=True)
            elif r.status_code == 404:
                _print('CLNK failed for {} ({} {})\nmake sure the file/'
                       'folder to be shared exists...'
                       .format(req['path'], r.status_code, r.reason), err=True)
            else:
                _print('CLNK failed for {} ({} {})'
                       .format(req['path'], r.status_code, r.reason), err=True)

    def _do_link300(self, args):
        'link [-a] -i|-p -r|-u|-ru [expiration_days] file|folder\n'\
        '    create a link to share a file or folder\n'\
        '    -a add an access code\n'\
        '    -i force creating an internal link\n'\
        '    -p force creating a public link\n'\
        '    -r the link is good for view and download of files\n'\
        '    -u the link allows to upload into the linked folder\n'\
        '       (at least one of -r and -u is required)\n'\
        '    if expiration_date (an integer) is not given, an unlimited\n'\
        '    link will be created\n'\
        '\n'\
        'link -d <id>\n'\
        '    -d delete link with <id>, where <id> is the leftmost integer\n'\
        '       displayed by the links command'
        self.logger.info('--> called "link300 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='daipru')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return

        # here we will handle the 'delete a link' fork, only
        if 'd' in para.flags:
            if len(para.flags) > 1:
                _print('error: -d is an exclusive flag...', err=True)
                return
            if len(para.args) != 1:
                _print('error: -d needs exactly one <id>...', err=True)
                return
            else:
                try:
                    _id = int(para.args[0])
                except ValueError:
                    _print('error: -d needs exactly one integer(!) <id>...',
                           err=True)
                    return
            if not self.links:
                _print('error: use the links command to get a list of '
                       'existing links', err=True)
                return
            else:
                if _id not in self.links.keys():
                    _print('error: link with <id> {} doesn\'t exist'
                           .format(_id), err=True)
                    return

            req = {'path': self.links[_id]['path'],
                   'url': self.links[_id]['url']}
            r = self.session.post('://'.join([self.scheme, self.aw]) +
                                  '/fss/public/link/delete', json=req)
            if r.status_code == 204:
                _print('CLNK deleted link with <id> {} to {}'
                       .format(_id, self.links[_id]['path']))
                del self.links[_id]
            else:
                _print('CLNK delete failed for <id> {} ({} {})'
                       .format(_id, r.status_code, r.reason), err=True)
        else:
            self.logger.info('--> called "link300 {}" --> forwarded to '
                             '"link211"'.format(args))
            self._do_link211(args)

    def _do_links300(self, args):
        'links\n'\
        '    list all active links\n'
        self.logger.info('--> called "links300 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
        else:
            req = {}
            cont = True
            res = {}
            cnt = 1

            while cont:
                r = self.session.post('://'.join(
                    [self.scheme,
                     self.aw]) + '/fss/public/link/list',
                                      json=req)
                if r.status_code != 200:
                    _print('CLNKS failed ({} {})'
                           .format(r.status_code, r.reason), err=True)
                    return
                else:
                    c = r.json()
                    if 'pageToken' in c.keys():
                        req['pageToken'] = c['pageToken']
                    else:
                        cont = False

                    for f in c['links']:
                        res[cnt] = {'url': f.get('url'),
                                    'expirationDate': f.get('expirationDate'),
                                    'public': f.get('public'),
                                    'permissions': f.get('permissions'),
                                    'token': f.get('token'),
                                    'path': f.get('path'),
                                    'itemName': f.get('itemName'),
                                    'accessCode': f.get('accessCode'),
                                    'type': f.get('type')}
                        cnt += 1

            self.links = OrderedDict()
            for f in sorted(res.keys()):
                # 10: {'accessCode': '8ba.B4Uk',
                #      'expirationDate': None,
                #      'itemName': 'ulp',
                #      'path': '/test/ulp',
                #      'permissions': ['READ', 'UPLOAD'],
                #      'public': True,
                #      'token': 'kG7E0oLuxNyCbsTS',
                #      'type': 'FOLDER',
                #      'url': 'https://snomis.ddns.net/u/kG7E0oLuxNyCbsTS/ulp?l'},
                _print('{:>3}: {:7}: {}'
                       .format(f, res[f]['type'], res[f]['path']))
                _print('     URL    : {}'.format(res[f]['url']))
                _print('     expires: {};  {}; {}; {}{}{}'
                       .format(time.strftime('%Y/%m/%d %H:%M:%S',
                                             time.localtime(res[f]['expirationDate'] / 1000)) if res[f]['expirationDate'] else 'no',
                               'public' if res[f]['public'] else 'internal',
                               ','.join(res[f]['permissions']),
                               'access code: "' if res[f]['accessCode'] else '',
                               res[f]['accessCode'] or '',
                               '"' if res[f]['accessCode'] else ''))
                self.links[f] = {'path': res[f]['path'],
                                 'url': res[f]['url']}

    def do_lpwd(self, args):
        'lpwd\n'\
        '    Print the local working directory.'
        self.logger.info('--> called "lpwd {}"'.format(args))
        _print('Local directory: {}'.format(self.__getcwd()))

    def do_lls(self, arg):
        'lls [local-path]\n'\
        '    list contents of local path'
        self.logger.info('--> called "lls {}"'.format(arg))
        try:
            para = paramcheck(arg)
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) > 1:
                _print('error: at max one parameter required...', err=True)
                return
            else:
                if len(para.args):
                    try:
                        isdir = True if os.stat(para.args[0]).st_mode & S_IFDIR == S_IFDIR else False
                    except FileNotFoundError:
                        cwd = para.args[0]
                    else:
                        cwd = join(para.args[0], '*') if isdir else para.args[0]
                else:
                    cwd = '*'

        for f in glob(cwd):
            # drwxr-xr-x   1 root  users   4096 May  9 14:47 hcp_a
            # -rwxrwxrwx   1 admin users  14656 May 04  2015 2013 IP-Umstellung.ods
            st = os.stat(f)
            _print('{} {:>4} {:8} {:8} {:>12} {} {}'
                   .format(self.__mode(st.st_mode),
                           st.st_nlink,
                           os.getuid(),
                           os.getuid(),
                           calcByteSize(st.st_size),
                           time.strftime('%Y/%m/%d %H:%M:%S',
                                         time.localtime(st.st_mtime)),
                           f))

    def do_ls(self, arg):
        'ls [-1] [-d] [-u] [remote-path]\n'\
        '    list contents of remote path\n'\
        '    -1 display one name per line\n'\
        '    -d show deleted files, too\n'\
        '    -u show names URL-encoded'
        self.logger.info('--> called "ls {}"'.format(arg))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(arg, flags='1du')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if 'd' in para.flags and self.snapshot:
                _print('error: LS for deleted files not available in '
                       'snapshots...', err=True)
                return
            if len(para.args) > 1:
                _print('error: at max one parameter required...', err=True)
                return
            else:
                if len(para.args):
                    cwd = normpath(join(self.cwd, para.args[0]))
                else:
                    cwd = self.cwd

        req = {'path': cwd}
        if 'd' in para.flags:
            req['includeDeleted'] = True
        if self.snapshot:
            req['viewAtTime'] = self.snapshot

        # To make sure that we can show deleted files whos names have been
        # overwritten by folder names, we run the requests twice if '-u' given
        res = {}

        cont = True
        while cont:
            r = self.session.post('://'.join(
                [self.scheme, self.aw]) + '/fss/public/folder/entries/list',
                                  json=req)
            if r.status_code != 200:
                # maybe cwd is a single file?
                if r.status_code == 404 and not res:
                    c = self.__getmeta(cwd)
                    if c:
                        if not (c['name'], 0) in res.keys():
                            res[(c['name'], 0)] = {'type': c['type'],
                                                   'size': c['size']
                                                   if 'size' in c.keys() else 0,
                                                   'changeTime': c['changeTime'],
                                                   'state': c['state'],
                                                   'access': c['access'],
                                                   'sharetype': c['sharing']['type'][0] if 'sharing' in c.keys() else '',
                                                   'backup': True if 'backup' in c.keys() else False,
                                                   }
                        break
                    else:
                        _print('LS failed ({} {})'
                               .format(r.status_code, r.reason), err=True)
                        return
                else:
                    if r.status_code == 400:
                        _print('LS failed ({} {})'.format(r.status_code,
                                                          r.reason),
                               r.text, err=True)
                    else:
                        pprint(r.headers)
                        pprint(r.text)
                        _print('LS failed ({} {})'
                               .format(r.status_code, r.reason), err=True)
                    return
            else:
                c = r.json()
                if 'pageToken' in c.keys():
                    req['pageToken'] = c['pageToken']
                    del req['path']
                else:
                    cont = False

                for f in c['entries']:
                    _pos = 0 if (f['name'], 0) not in res.keys() else 1
                    res[(f['name'], _pos)] = {'type': f['type'],
                                              'size': f['size'] if 'size' in f.keys() else 0,
                                              'changeTime': f['changeTime'],
                                              'state': f['state'],
                                              'access': f['access'],
                                              'sharetype': f['sharing']['type'][0] if 'sharing' in f.keys() else '',
                                              'backup': True if 'backup' in f.keys() else False,
                                              }

        if '1' in para.flags:
            for f in sorted(res.keys()):
                click.echo('{} {}'
                           .format(f[0],
                                   click.style('(deleted)', fg='white', bg='red') if
                                   res[f]['state'].upper() == 'DELETE' else ''))
        else:
            for f in sorted(res.keys()):
                S_IS = stat.S_IFDIR if res[f]['type'] == 'FOLDER' else 0
                if res[f]['access'] == 'NO ACCESS':
                    S_IS = 0 | S_IS
                if res[f]['access'] == 'VIEWER':
                    S_IS = stat.S_IRUSR | S_IS
                if res[f]['access'] == 'COLLABORATOR':
                    S_IS = stat.S_IRUSR | stat.S_IWUSR | S_IS
                if not 'u' in para.flags:
                    # _filename = join(para.args[0], f) if len(para.args) else f
                    _filename = f[0]
                else:
                    # _filename = quote(join(para.args[0], f) if len(para.args) else f, safe='/.-_')
                    _filename = quote(f[0], safe='/.-_')

                click.echo('{:1} {:>3} {:7} {:>12} {} {}'
                           .format('B' if 'backup' in res[f].keys() and res[f]['backup'] else res[f]['sharetype'],
                                   self.__mode(S_IS)[:3],
                                   click.style('deleted', fg='white', bg='red') if res[f]['state'].upper() == 'DELETE' else ' ',
                                   calcByteSize(res[f]['size']) if 'size' in res[f].keys() else '',
                                   time.strftime('%Y/%m/%d %H:%M:%S',
                                                 time.localtime(res[f]['changeTime'] / 1000)),
                                   _filename))

    def do_mkdir(self, args):
        'mkdir [-R] directory-name\n'\
        '    make directory on the remote machine.\n'\
        '    -R recursively make parent directories if required.'
        self.logger.info('--> called "mkdir {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return
        elif self.snapshot:
            _print('can\'t create a folder within a snapshot', err=True)
            return

        try:
            para = paramcheck(args, flags='R')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if not len(para.args):
                _print('error: exactly one parameter required...', err=True)
                return
            else:
                if para.args[0].startswith('/'):
                    newd = para.args[0]
                else:
                    newd = normpath(join(self.cwd, para.args[0]))

        req = {'path': newd,
               'createParents': True if 'R' in para.flags else False}

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/folder/create',
                              json=req)
        if r.status_code == 201:
            _print('RMD command successful.')
        else:
            _print('RMD {} failed ({} {})'
                   .format(newd, r.status_code, r.reason), err=True)

    def do_mv(self, args):
        'mv [-R] old_name new_name\n'\
        '    move a file or directory to a new name or position\n'\
        '    -R recursively make parent directories if required.'
        self.logger.info('--> called "mv {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return
        elif self.snapshot:
            _print('can\'t move a file/folder within a snapshot', err=True)
            return

        try:
            para = paramcheck(args, flags='R')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) != 2:
                _print('error: exactly two parameters required...', err=True)
                return
            elif para.args[0] == '/':
                _print('error: / can\'t be moved, as you should know!',
                       err=True)
                return
            elif para.args[1].endswith('/') and para.args[1] != '/':
                _print('error: move target may not end with /!', err=True)
                return

        # get sources etag and type
        req = {
            'path': para.args[0] if para.args[0].startswith('/') else normpath(
                join(self.cwd, para.args[0]))}
        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/info/get',
                              json=req)
        if r.status_code == 200:
            srcres = r.json()
        elif r.status_code == 404:
            _print('error: {} doesn\'t exist...'.format(para.args[0]),
                   err=True)
            return
        else:
            _print('error: failed to stat {} ({} {})...'
                   .format(para.args[0], r.status_code, r.reason), err=True)
            return

        # check target
        req = {
            'path': para.args[1] if para.args[1].startswith('/') else normpath(
                join(self.cwd, para.args[1]))}
        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/info/get',
                              json=req)
        if r.status_code == 200:
            tgtres = r.json()
        elif r.status_code != 404:
            _print('error: failed to stat {} ({} {})...'
                   .format(para.args[1], r.status_code, r.reason), err=True)
            return

        # if the move target is an existing folder, make sure we move the
        # source into the folder with the source name
        _target = para.args[1] if para.args[1].startswith('/') else normpath(join(self.cwd, para.args[1]))
        if r.status_code == 200 and tgtres['type'] == 'FOLDER':
            _target = join(_target, split(para.args[0])[1])

        req = {'sourcePath': para.args[0] if para.args[0].startswith('/') else normpath(join(self.cwd, para.args[0])),
               'destinationPath': _target,
               'etag': srcres['etag'],
               'createParents': True if 'R' in para.flags else False}

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/move',
                              json=req)
        if r.status_code == 200:
            _print('MV command successful.')
        else:
            _print('MV {} {} failed ({} {})'
                   .format(para.args[0], para.args[1],
                           r.status_code, r.reason),
                   err=True)

    def do_open(self, arg):
        'open [[user[:password]@]hcpanywhere-name]\n'\
        '    connect to an HCP Anywhere server\n'\
        'Be aware that there is a history file - think if you want to store\n'\
        'your passowrd in it...'
        self.logger.info('--> called "open {}"'.format(arg))
        # make sure we are not connected, yet
        if self.connected:
            _print('error: already connected to {} - use "close" to '
                   'disconnect.'.format(self.aw), err=True)
            return

        if arg:
            if arg != '-x':
                aw = convertaw(arg, nossl=self.nossl)
                self.aw = aw.netloc
                self.scheme = aw.scheme
                self.user = aw.user
                self.password = aw.password

        if not self.aw:
            # request aw server
            while True:
                aw = input('open server: ')
                if not aw and self.aw:
                    aw = self.aw
                if aw:
                    break
            self.aw = aw

        # session setup
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({'Accept': 'application/json',
                                     'Content-Type': 'application/json'})

        # request user, if not already known
        _print('About to connect to {}.'.format(self.aw))

        # self.user = self.user or getuser()
        if not self.user:
            while True:
                user = input('User : ')
                if user:
                    self.user = user
                    break

        # request the password
        if not self.password:
            while True:
                password = click.prompt('Password required for {}'
                                        .format(self.user),
                                        hide_input=True, type=str)
                if password:
                    self.password = password
                    break

        # this is for AD authentication
        if not self.saml:
            # w/o SAML, we start with FS&S API 2.1.1
            self.session.headers.update({'X-HCPAW-FSS-API-VERSION':
                                             supportedapis[0]})

            auth = OrderedDict([('username', self.user),
                                ('password', self.password),
                                ('grant_type', 'urn:hds:oauth:negotiate-client')])

            try:
                r = self.session.post('://'.join([self.scheme, self.aw])+'/fss/public/login/oauth',
                                      data=dumps(auth))
            except requests.exceptions.ConnectionError as e:
                _print('Connection to {} failed...'.format(self.aw),
                       'hint: {}'.format(e).format(self.aw, e))
            else:
                if r.status_code == 200:
                    rr = r.json()

                    self.api = self.forceapi or sorted(
                        r.headers['X-HCPAW-SUPPORTED-FSS-API-VERSIONS'].split(','),
                        reverse=True)[0]
                    if self.api not in supportedapis:
                        _print('[Anywhere offers yet unknown api v{}, '
                               'falling back to v{}]'
                               .format(self.api, supportedapis[-1]))
                        self.api = supportedapis[-1]
                    self.session.headers.update({'X-HCPAW-FSS-API-VERSION': self.api,
                                                 'Authorization': '{} {}'
                                                .format(rr['token_type'],
                                                        rr['access_token'])})
                    self.expires = time.strftime('%Y/%m/%d %H:%M:%S',
                                                 time.localtime(time.time() +
                                                                rr['expires_in']))
                    self.__setapi(self.api)
                    self.connected = True
                    self.logger.debug('acquire_token returned: {} {} {}'
                                      .format(r.status_code, r.reason, r.elapsed))
                else:
                    self.password = None
                    _print('Login incorrect ({} {}).'
                           .format(r.status_code, r.reason), err=True)
                    _print('awftp: Login failed', err=True)

        # this is for SAML based authentication
        else:
            try:
                self.api = samlauth(session=self.session,anywhere='://'.join([self.scheme,
                                                                              self.aw]),
                                    idp=self.saml, user=self.user, password=self.password,
                                    forceapi=self.forceapi)
            except SamlAuthError as e:
                _print('SAML authentication failed',
                       str(e), err=True)
                return
            else:
                self.__setapi(self.api)
                self.connected = True
                self.expires = None

        _print('User {} logged in.'.format(self.user))
        _print('Remote system type is HCP Anywhere, FS&S API is v{}'
               .format(self.api))
        _print('Using binary mode to transfer files.')

    # def do_progress(self, args):
    #     'progress\n'\
    #     '    toggle showing a progress meter'
    #     self.logger.info('--> called "progress {}"'.format(args))
    #     self.progress = False if self.progress else True
    #     _print('Progress meter will {}be shown'
    #            .format('' if self.progress else 'not '))

    def do_put(self, args):
        'put [-u] local-file [remote-file]\n'\
        '    send (upload) a file.\n'\
        '    -u update an existing file'
        self.logger.info('--> called "put {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return
        elif self.snapshot:
            _print('error: can\'t put a file into a snapshot', err=True)
            return

        try:
            para = paramcheck(args, flags='u')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) not in [1, 2]:
                _print('error: one or two parameters are required...',
                       err=True)
                return
            elif para.args[0].endswith('/') or para.args[0].endswith('\\'):
                _print('error: PUT src can\'t be a folder...', err=True)
                return
            elif len(para.args) == 1:
                src = para.args[0]
                tgt = normpath(join(self.cwd, splitfilename(src)))
            else: # len(para.args) == 2
                src = para.args[0]
                tgt = para.args[1] if para.args[1].startswith('/') else normpath(join(self.cwd, para.args[1]))

            if len(para.args) in [1,2]:
                _meta = self.__getmeta(tgt)
                # if the put target is an existing folder, make sure we move
                # the source into the folder with the source name
                if _meta:
                    if _meta['type'] == 'FOLDER':
                        tgt = join(_target, splitfilename(para.args[0]))
                else:
                    if 'u' in para.flags:
                        _print('error: PUT can\'t update a non-existent '
                               'file...', err=True)
                        return

        self.logger.debug('put from src = {} to tgt = {}'.format(src, tgt))

        try:
            _size = os.stat(src).st_size
        except Exception as e:
            _print('error: failed to stat {}...'.format(src),
                   'hint: {}'.format(e), err=True)
            return

        if self.progress:
            with click.progressbar(length=_size,
                                   label="PUT {} ".format(src)) as bar:

                try:
                    sendhdl = MonitoredReader(src, callback=bar.update)
                except Exception as e:
                    _print('error: failed to open {}...'.format(src),
                           'hint: {}'.format(e), err=True)
                    return

                try:
                    tgt = normpath(join(self.cwd, tgt))
                    r = self.session.post('://'.join(
                        [self.scheme, self.aw]) + '/fss/public/file/stream/{}'
                                          .format('update' if 'u' in para.flags else 'create'),
                                          data=sendhdl,
                                          params={'path': tgt,
                                                  'createParents': False},
                                          headers={'Content-Type':
                                                       'application/octet-stream',
                                                   'If-Match': _meta['etag'] if _meta else ''})
                except Exception as e:
                    _print('PUT command failed...',
                           'hint: {}'.format(e), err=True)
                    return
                finally:
                    sendhdl.close()
                    _print('')  # the progressbar ends w/o a linefeed...

                if r.status_code in [200, 201]:
                    _print('PUT command successful.')
                else:
                    _print('error: PUT {} {} failed ({} {})'
                           .format(src, tgt, r.status_code, r.reason),
                           err=True)

    def do_pwd(self, args):
        'pwd\n'\
        '    Print the remote working directory.'
        self.logger.info('--> called "pwd {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        _print('Remote directory: {}'.format(self.cwd))

    def do_quit(self, arg):
        'quit\n'\
        '    terminate awftp session and exit.'
        self.logger.info('--> called "quit {}"'.format(arg))

        _print('Goodbye.')
        return True

    def _do_restore300(self, args):
        'restore [-d] remote-name\n'\
        '    make the version of a file or folder within the active\n'\
        '    snapshot the current version (restore it to "now").\n'\
        '    -d restore a deleted file'
        self.logger.info('--> called "restore300 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='d')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.args) != 1:
                _print('error: exactly one parameter required...', err=True)
                return
            else:
                _restf = para.args[0]

            if self.snapshot:
                if 'd' in para.flags:
                    _print('can\'t restore deleted "{}" while in an active '
                           'snapshot'.format(_restf), err=True)
                    return
                else:
                    # restore a file from a snapshot
                    _print('noop')
            else:
                if not 'd' in para.flags:
                    _print('can\'t restore "{}" without an active snapshot'
                           .format(_restf), err=True)
                    return
                else:
                    # restore a deleted file
                    req = {'path': normpath(join(self.cwd, _restf))}

                    r = self.session.post('://'.join(
                        [self.scheme, self.aw]) + '/fss/public/file/restore',
                                          json=req)
                    if r.status_code == 200:
                        _print('RST command successful.')
                    else:
                        _print('error: RST {} failed ({} {})'
                               .format(_restf, r.status_code, r.reason),
                               err=True)

    def do_rmdir(self, args):
        'rmdir [-R] remote-folder\n'\
        '    remove a remote folder\n'\
        '    -R recursively delete a folder and *all* its content.'
        self.logger.info('--> called "rmdir {}" --> forwarded to "rm -d"'
                         .format(args))
        self.do_rm('-d ' + args)

    def do_rm(self, args):
        'rm [-d [-R]] remote-name\n'\
        '    remove a remote file or folder\n'\
        '    -d remove a folder\n'\
        '    -R recursively delete a folder and *all* its content.'
        self.logger.info('--> called "rm {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return
        elif self.snapshot:
            _print('can\'t remove within a snapshot', err=True)
            return

        try:
            para = paramcheck(args, flags='dR')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if not len(para.args):
                _print('error: exactly one parameter required...', err=True)
                return
            else:
                if para.args[0] == '/':
                    _print('error: can\'t delete /', err=True)
                    return
                if para.args[0].startswith('/'):
                    rmd = para.args[0]
                else:
                    rmd = normpath(join(self.cwd, para.args[0]))

        _meta = self.__getmeta(rmd)

        if not _meta:
            _print('error: {} is non-existant'.format(rmd), err=True)
            return
        if 'd' in para.flags and _meta['type'] != 'FOLDER':
            _print('error: {} is a regular file'.format(rmd), err=True)
            return
        if _meta['type'] == 'FOLDER' and 'd' not in para.flags:
            _print('error: {} is a folder'.format(rmd), err=True)
            return
        if 'R' in para.flags and not 'd' in para.flags:
            _print('error: impossible to recursively remove a regular file',
                   err=True)
            return

        if not _meta['etag']:
            _print('error: stat({}) failed'.format(rmd), err=True)
            return

        req = {'path': rmd,
               'recursive': True if 'R' in para.flags else False,
               'etag': _meta['etag']}


        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/delete',
                              json=req)
        if r.status_code == 204:
            _print('RMD command successful.')
        else:
            if r.status_code == 400:
                _print('error: {}'.format(r.text), err=True)
            _print('RMD {} failed ({} {})'
                   .format(rmd, r.status_code, r.reason), err=True)

    # def do_run(self, arg):
    #     'run <script>\n' \
    #     '    Run a batch of commands stored in file <script>.'
    #     try:
    #         para = paramcheck(arg)
    #     except Exception as e:
    #         _print('error: parameters invalid...\nhint: {}'.format(e),
    #                err=True)
    #         return
    #     else:
    #         if not len(para.args):
    #             _print('error: at least one parameter required...',
    #                    err=True)
    #
    #     try:
    #         with open(para.args[0], 'r') as inhdl:
    #             for cmnd in inhdl.readlines():
    #                 cmnd = cmnd.strip()
    #                 # skip comments and empty lines
    #                 if cmnd and not cmnd.startswith('#'):
    #                     if cmnd.startswith('run'):
    #                         _print('skipping "{}"...'.format(cmnd))
    #                     else:
    #                         self.cmdqueue.append('_exec ' + cmnd.strip())
    #     except Exception as e:
    #         _print('error: running script "{}" failed...\nhint: {}'
    #                .format(para.args[0], e), err=True)

    def _do_search300(self, args):
        'search [-1] [-d] [-s <snap_id>] <pattern>\n' \
        '    search for files/folders containing <pattern> in their name,\n'\
        '    starting at the current directory (in realtime or the active\n'\
        '    snapshot)\n'\
        '    -1 display one name per line\n'\
        '    -d search for deleted files, too\n'\
        '    -s search in specific snapshot <snap_id> (from snap -l)\n'\
        '\n'\
        '    <pattern> is the string to search for, min. 3 characters'
        self.logger.info('--> called "search300 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='1ds')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if not 's' in para.flags:
                if len(para.args) != 1:
                    _print('error: parameters invalid...',
                           'hint: exactly one parameter required', err=True)
                    return
                elif len(para.args[0]) < 3:
                    _print('error: <pattern> "{}" too short'.format(para.args[0]),
                           'hint: at least 3 characters required', err=True)
                    return
                _substring = para.args[0]
                _snapshot = None
            else:
                if len(para.args) != 2:
                    _print('error: parameters invalid...',
                           'hint: exactly two parameter required', err=True)
                    return
                elif not self.snapshots:
                    _print('error: no snapshots known...',
                           'hint: run snap -l to see the available snapshots',
                           err=True)
                    return
                elif para.args[0] not in self.snapshots.keys():
                    _print('error: unknown snapshot "{}"...'
                           .format(para.args[0]),
                           'hint: run snap -l to see the available snapshots'
                           .format(para.args[0]), err=True)
                    return
                _substring = para.args[1]
                _snapshot = para.args[0]

        _print('it might take a while to search for "{}"...'
               .format(_substring))

        req = {'path': self.cwd,
               'substring': _substring}
        if 's' in para.flags:
            req['pointInTime'] = self.snapshots[_snapshot]
        elif self.snapshot:  # if we are in a snapshot, search there!
            req['pointInTime'] = self.snapshot
        if 'd' in para.flags:
            req['includeDeleted'] = 'true'
        res = {}

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/search',
                              json=req)
        if r.status_code != 200:
            _print('SRCH failed ({} {})'.format(r.status_code, r.reason),
                   err=True)
            return
        else:
            c = r.json()
            for f in c['entries']:
                _entry = join(f['parent'] if f['name'] != '/' else '',
                              f['name'])
                if f['type'].upper() == 'FOLDER':
                    _entry += '/'
                # as we only search starting at self.cwd, cut it of...
                if self.cwd != '/' and _entry.startswith(self.cwd):
                    _entry = _entry[len(self.cwd)+1:]

                res[_entry] = {'type': f['type'],
                               'size': f['size'] if 'size' in f.keys() else 0,
                               'changeTime': f['changeTime'],
                               'state': f['state'],
                               'access': f['access']}

        if '1' in para.flags:
            for f in sorted(res.keys()):
                click.echo('{} {}'.format(f, click.style('(deleted)', fg='white', bg='red') if res[f]['state'].upper() == 'DELETE' else '' ))
        else:
            for f in sorted(res.keys()):
                S_IS = stat.S_IFDIR if res[f]['type'] == 'FOLDER' else 0
                if res[f]['access'] == 'NO ACCESS':
                    S_IS = 0 | S_IS
                if res[f]['access'] == 'VIEWER':
                    S_IS = stat.S_IRUSR | S_IS
                if res[f]['access'] == 'COLLABORATOR':
                    S_IS = stat.S_IRUSR | stat.S_IWUSR | S_IS
                _print('{:>10} {:>4} {:>8} {:>8} {:>12} {} {} {}'
                       .format(self.__mode(S_IS),
                               '-', # the number of hardlinks
                               '-', # the user
                               '-', # the group
                               calcByteSize(res[f]['size']) if 'size' in res[f].keys() else '',
                               time.strftime('%Y/%m/%d %H:%M:%S',
                                             time.localtime(res[f]['changeTime'] / 1000)),
                               f,
                               click.style('(deleted)', fg='white', bg='red') if res[f]['state'].upper() == 'DELETE' else '' ))

    def _do_snap300(self, args):
        'snap -l | -s <index> | -u\n' \
        '    work with restore points (snapshots)\n'\
        '    -l list available snapshots\n'\
        '    -s <index> work on this snapshot\n'\
        '    -u unset snapshot (return to "now")'\
        '\n'\
        '    Once a snapshot has been set, all operations will be based on it.'
        self.logger.info('--> called "snap300 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        try:
            para = paramcheck(args, flags='lsu')
        except Exception as e:
            _print('error: parameters invalid...',
                   'hint: {}'.format(e), err=True)
            return
        else:
            if len(para.flags) > 1:
                _print('error: parameters invalid...',
                       'hint: at max. one parameter required', err=True)
                return

            # show the actually set snapshot
            if not len(para.flags):
                if self.snapshot:
                    _print('working on snapshot of {}'
                        .format(time.asctime(time.localtime(self.snapshot))))
                else:
                    _print('not working on a snapshot')
                return
            # list available snapshots
            elif 'l' in para.flags:
                r = self.session.post('://'.join([self.scheme, self.aw]) +
                                      '/fss/public/user/restorePoints/list')
                if r.status_code == 200:
                    # {'restorePoints': [{'point': 1492120799999}]
                    rps = r.json()
                    self.snapshots = {str(x): y for x, y in zip(
                        range(1, len(rps['restorePoints']) + 1),
                        [i['point'] for i in rps['restorePoints']])}
                    txt = 'Available Snapshots:'
                    for i in sorted(self.snapshots.keys()):
                        # the restorepoint is given in milliseconds, that's why
                        # we need to convert it to seconds for use of the time
                        # funtions
                        _print('{:20} {:>3} - {}'
                               .format(txt, i,
                                       time.strftime('%a %Y/%m/%d %H:%M',
                                                     time.localtime(
                                                        self.snapshots[
                                                            i] / 1000))))
                        if txt.startswith('A'):
                            txt = ''
                else:
                    _print('SNAP failed ({} {})'
                           .format(r.status_code, r.reason), err=True)
                    return
            # set snapshot to use
            elif 's' in para.flags:
                if not self.snapshots:
                    _print('error: run snap -l first to get a list of '
                           'available snapshots', err=True)
                elif len(para.args) != 1:
                    _print('error: index of an available snapshot needed',
                           err=True)
                elif para.args[0] not in self.snapshots.keys():
                    _print('error: {} is not an index of an available snapshot'
                           .format(para.args[0]), err= True)
                else:
                    self.snapshot = self.snapshots[para.args[0]]
                    _print('now working on snapshot of {}'
                        .format(time.asctime(time.localtime(self.snapshot/1000))))
                    self.prompt = 'snap {}> '.format(
                        time.strftime('%Y/%m/%d %H:%M', time.localtime(
                            self.snapshots[para.args[0]] / 1000)))
            # un-set the snapshot to the actual data
            elif 'u' in para.flags:
                self.snapshot = None
                self.prompt = self._prompt
                _print('no more working on a snapshot')

    def do_status(self, arg):
        'status\n' \
        '    Show the session status.'
        self.logger.info('--> called "status {}"'.format(arg))
        if self.connected:
            _print('Connected to:       {}@{}'.format(self.user, self.aw))
            _print('Session expires:    {}'.format(self.expires or 'soon'))
            _print('Current')
            _print('  remote directory: {}'.format(self.cwd))
            _print('  local directory:  {}'.format(self.__getcwd()))
            _print('Progress meter:     {}'
                   .format('ON' if self.progress else 'OFF'))
        else:
            if self.aw:
                _print('Not connected, but preset to {}{}'
                       .format(self.user+'@', self.aw))
            else:
                _print('Not connected.', err=True)

    def do_time(self, arg):
        'time command [args]\n' \
        '    measure the time command takes to complete'
        self.logger.info('--> called "time {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        st = time.time()
        if command:
            try:
                result = eval('self.do_{}("{}")'.format(command, params))
            except Exception as e:
                _print('error: time command failed...',
                       'hint: {}'.format(e), err=True)
            else:
                time.sleep(.25)
                _print('[time: {}]'.format(calctime(time.time() - st)),
                       err=True)
                return result
        else:
            _print('error: time command failed - no command given...',
                   err=True)

    def _do_user211(self, args):
        'user\n'\
        '    get information about the user\'s settings in HCP Anywhere.'
        self.logger.info('--> called "user211 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/user/get')
        if r.status_code == 200:
            res = r.json()
            _print('User:  {} ({})'.format(res['username'], res['email']))
            _print('usage: {} of {}'.format(calcByteSize(res['usageBytes']),
                                            calcByteSize(res['quotaBytes'])))
            _print('Settings:')
            if 'sharingEnabled' in res['linkSettings']:
                _print('    Sharing enabled: {} (public sharing {}allowed)'.format(
                     'yes' if res['linkSettings']['sharingEnabled'] else 'no',
                     '' if res['linkSettings']['publicSharingEnabled'] else 'not '))
            elif 'sharingEnabled' in res.keys():
                _print('    Sharing enabled: {} (public sharing {}allowed)'.format(
                     'yes' if res['sharingEnabled'] else 'no',
                     '' if res['linkSettings']['publicSharingEnabled'] else 'not '))
            _print('    Upload enabled:  {} (public upload {}allowed)'.format(
                 'yes' if res['linkSettings']['uploadEnabled'] else 'no',
                 '' if res['linkSettings']['publicUploadEnabled'] else 'not '))
            _print('    default is {} sharing'.format(
                 'public' if res['linkSettings'][
                     'sharingDefaultPublic'] else 'internal'))
            _print('    {} days to share per default, max. {} days'.format(
                 res['linkSettings']['defaultDaysToShare'],
                 res['linkSettings']['maxDaysToShare']))
        else:
            _print('USR command failed ({} {})'
                   .format(r.status_code, r.reason), err=True)

    def _do_user300(self, args):
        'user\n'\
        '    get information about the user\'s settings in HCP Anywhere.'
        self.logger.info('--> called "user300 {}"'.format(args))
        if not self.connected:
            _print('Not connected.', err=True)
            return

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/user/get')
        if r.status_code == 200:
            res = r.json()
            _print('User:  {} ({} - {})'.format(res['username'],
                                                res['displayName'],
                                                res['email']))
            _print('usage: {} of {}'.format(calcByteSize(res['usageBytes']),
                                            calcByteSize(res['quotaBytes'])))
            _print('       {} dirs, {} files, {} conflicts'
                   .format(res['directoryCount'], res['fileCount'],
                           res['conflicts']))
            _print('Settings:')
            _print('    Sharing enabled: {} '
                   .format('yes' if res['sharingEnabled'] else 'no'))
            if res['sharingEnabled']:
                _print('   internal sharing: read - {} / upload - {}'
                    .format(
                     'yes' if res['linkSettings']['readEnabled'] else 'no',
                     'yes' if res['linkSettings']['uploadEnabled'] else 'no'))
                _print('     public sharing: read - {} / upload - {}'
                       .format('yes' if res['linkSettings'][
                    'publicReadEnabled'] else 'no',
                    'yes' if res['linkSettings'][
                        'publicUploadEnabled'] else 'no'))
            _print('                     default is {} sharing'.format(
                 'public' if res['linkSettings'][
                     'sharingDefaultPublic'] else 'internal'))
            _print('    {} days to share per default, max. {} days'.format(
                 res['linkSettings']['defaultDaysToShare'],
                 ('unlimited' if res['linkSettings'][
                     'allowLinksWithoutExpiration'] else
                  res['linkSettings']['maxDaysToShare'])))
        else:
            _print('USR command failed ({} {})'
                   .format(r.status_code, r.reason), err=True)

    def __exec(self, arg):
        # Run a command given as parameters, but make sure to print a prompt
        # before. This is for running scripted commands (~/.hs3shrc)

        self.logger.debug('--> called "__exec {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        if command:
            print(self.prompt + arg, flush=True)
            return eval('self.do_{}("{}")'.format(command, params))
        else:
            return

    def __getmeta(self, path):
        '''
        Get a files or directories metadata.

        :param path:    the file or directory to query
        :return:        the response json converted to dict
        '''
        self.logger.debug('--> called "__getmeta {}"'.format(path))
        req = {'path': path}
        if self.snapshot:
            req['viewAtTime'] = self.snapshot

        r = self.session.post('://'.join(
            [self.scheme, self.aw]) + '/fss/public/path/info/get',
                              json=req)
        if r.status_code == 200:
            return r.json()
        else:
            self.logger.debug('getmeta failed ({} {})'.format(r.status_code,
                                                              r.reason))
            return None

    def __mode(self, mode):
        '''
        From a st_mode Integer, calculate the ls-alike string

        :param mode:    a st_mode Integer
        :return:        a string
        '''
        self.logger.debug('--> called "__mode {}"'.format(mode))
        ret = 'd' if mode & S_IFDIR == S_IFDIR else '-'
        cnt = 0

        for i in str(bin(mode))[-9:]:
            # rwxr-xr-x
            if cnt in [0, 3, 6]:
                ret += 'r' if i == '1' else '-'
            elif cnt in [1, 4, 7]:
                ret += 'w' if i == '1' else '-'
            else:
                ret += 'x' if i == '1' else '-'
            cnt += 1

        return ret

    def __setapi(self, apiversion: str):
        """
        Configure this class for a specific AW API version.
        
        :param apiversion:   the api version ('2.1.1', '3.0.0')
        """
        self.logger.debug('configuring Awftpshell for FS&S API version {}'
                          .format(apiversion))

        #       API vers,  user cmd   mapped method
        apis = {'2.1.1': {'do_link': '_do_link211',
                          'do_user': '_do_user211'},
                '3.0.0': {'do_find': '_do_find300',
                          'do_hist': '_do_hist300',
                          'do_link': '_do_link300',
                          'do_links': '_do_links300',
                          'do_restore': '_do_restore300',
                          'do_snap': '_do_snap300',
                          'do_search': '_do_search300',
                          'do_user': '_do_user300'}
                }

        if apiversion not in apis.keys():
            raise AttributeError('api version {} unknown'.format(apiversion))

        for f in apis[apiversion].keys():
            exec('Awftpshell.{} = self.{}'.format(f, apis[apiversion][f]))

    def __getcwd(self):
        """
        Secure version of os.getcwd that doesn't traceback in case the current
        working directory isn't accessible (maybe deleted underneath?)

        :return:    the cwd
        """
        try:
            return os.getcwd()
        except FileNotFoundError as e:
            return str(e)
