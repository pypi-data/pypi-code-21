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

import atexit
import os
import sys
import logging
from requests.packages.urllib3 import disable_warnings
try:
    import readline
except ImportError:
    readline = False

import aw


def main():
    opts = aw.tools.parseargs()

    # disable urllib3 warning caused by not verfying the hosts certs...
    disable_warnings()

    if opts.idps:
        try:
            aw.tools.listidps(aw_server=opts.aw_server, nossl=opts.nossl)
        except aw.exceptions.IdpListError as e:
            sys.exit('list IDPs failed\n\thint: {}'.format(e))
        else:
            sys.exit()

    if opts.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if readline:
        histfile = os.path.join(os.path.expanduser("~"), ".awftp_history")
        # noinspection PyBroadException
        _die = False
        while True:
            try:
                readline.read_history_file(histfile)
                # default history len is -1 (infinite), which may grow unruly
                readline.set_history_length(1000)
            except Exception as e:
                if _die:
                    print('error: open of history file failed ({})...\n\t'
                          'and creating it did\'t help at all.\n\t'
                          'That mean\'s we can\'t store command history, sorry.'
                          .format(e))
                    break

                # if this goes wrong, most likely the history file doesn't exist,
                # so let's try and create it
                try:
                    with open(os.path.join(os.path.expanduser("~"),
                                           ".awftp_history"), 'w') as histhdl:
                        pass
                except Exception as f:
                    print('error: open of history file failed ({})...\n\t'
                          'and creating it failed as well ({})\n\t'
                          'That mean\'s we can\'t store command history, sorry.'
                          .format(e, f))
                    break
                _die = True
            else:
                atexit.register(readline.write_history_file, histfile)
                break

    try:
        aw.cmd.Awftpshell(completekey='Tab',
                          target=opts.aw_server,
                          nossl=opts.nossl,
                          api=opts.api,
                          saml=opts.saml).cmdloop()
    except UnicodeEncodeError as e:
        fatal = ('Fatal: UnicodeEncodeError\n'
                 '\tMake sure you have your system language set to UTF-8\n'
                 '\tExample:\n'
                 '\t\t$ export LC_ALL=en_US.UTF-8\n'
                 '\n')
        sys.exit(fatal)

if __name__ == '__main__':
    main()
