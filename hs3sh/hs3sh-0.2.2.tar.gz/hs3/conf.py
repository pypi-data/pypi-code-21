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
import time
import configparser
from os.path import expanduser

from hs3.init import TEMPLATE
from hs3.s3config import TYPES, BOOLTAGS, INTTAGS, REGIONREQUIRED, REQUIRED


def readconf():
    '''
    Read the configuration file, parse it and return a dict.

    :return:    a dict containing the various profiles
    '''
    confp = configparser.ConfigParser()
    if not confp.read([expanduser('~/.hs3sh.conf'), '.hs3sh.conf']):
        createtemplateconf()
        sys.exit()

    profs = {}
    errors = 0

    for p in confp.sections():
        profs[p] = {'type': confp.get(p, 'type', fallback='')}
        # make sure we get the required options for the type of S3 store
        # from .hs3sh.config
        try:
            t = confp.get(p, 'type', fallback='')
            if t not in TYPES.keys():
                errors += 1
                print('.hs3sh.conf: [{}]: "type" is invalid...'
                      .format(p), flush=True)
                continue
        except configparser.NoOptionError:
            print(sys.exc_info())
            errors += 1
            print('.hs3sh.conf: [{}]: "type" is missing...'
                  .format(p), flush=True)
            continue

        for o in TYPES[t].keys():
            if o in BOOLTAGS:
                try:
                    profs[p][o] = confp.getboolean(p, o, fallback=TYPES[t][o])
                except ValueError:
                    profs[p][o] = False
                    errors += 1
                    print('.hs3sh.conf: [{}]/{}: requires a boolean value...'
                          .format(p, o), flush=True)
                    continue
            elif o in INTTAGS:
                try:
                    profs[p][o] = confp.getint(p, o, fallback=TYPES[t][o])
                except ValueError:
                    profs[p][o] = -1
                    errors += 1
                    print('.hs3sh.conf: [{}]/{}: requires an integer value...'
                          .format(p, o), flush=True)
                    continue
            else:
                profs[p][o] = confp.get(p, o, fallback=TYPES[t][o])

        # check if we have all we need for this profile
        for req in REQUIRED:
            if req in BOOLTAGS:
                continue
            if not profs[p][req]:
                errors += 1
                print('.hs3sh.conf: [{}]/{}: requires a value...'
                      .format(p, req), flush=True)
        if profs[p]['type'] in REGIONREQUIRED and not profs[p]['region']:
            errors += 1
            print('.hs3sh.conf: [{}]/region: requires a value...'
                  .format(p), flush=True)

    if errors:
        time.sleep(.5)
        raise ValueError('parsing .hs3sh.conf showed {} errors - '
                         'please check...'.format(errors))

    return profs


def createtemplateconf():
    '''Ask the user if a template config file shall be created and do so...'''
    print('No configuration file (.hs3sh.conf) found.')
    answer = input('Do you want me to create a template file (y/n)? ')

    if answer in ['y', 'Y']:
        try:
            with open('.hs3sh.conf', 'w') as outhdl:
                for l in TEMPLATE:
                    print(l, file=outhdl)
        except Exception as e:
            sys.exit('fatal: failed to created template file...\n    hint: {}'
                     .format(e))
        else:
            print('\nA template file (.hs3sh.conf) has been created in the '
                  'current directory.')
            print('For best security, move it to you home directory and make\n'
                  'sure no other user can access it (chmod 600 ~/.hs3sh.conf).')
            print('Then edit it to fit your needs...')
            print()
