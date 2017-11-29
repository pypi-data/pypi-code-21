# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

import os
import sys
import socket
import builtins

from collections import defaultdict

import takoshell.jobs
import takoshell.tools
import takoshell.aliases

class Settings(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.manually_set = set()

    def __getattr__(self, attr):
        try:
            return self.__getitem__(attr.upper())
        except KeyError:
            raise AttributeError('Settings object has no attribute %s' % attr)

    def __setattr__(self, attr, val):
        self.__setitem__(attr.upper(), val)
        self.manually_set.add(attr.upper())

    def __delattr__(self, attr):
        self.__delitem__(self, attr)
        self.manually_set.remove(attr.upper())

    def is_manually_set(self, name):
        return name.upper() in self.manually_set

    def __repr__(self):
        return 'Settings(%r)' % {k:v for k,v in self.items() if k != 'MANUALLY_SET'}

    def __iter__(self):
        for key in self.keys():
            if key != 'MANUALLY_SET':
                yield key

DEFAULT_PROMPT = ('{BOLD_GREEN}{user}@{hostname}'
                  '{BOLD_BLUE} {cwd} {prompt_end}{NO_COLOR} ')

DEFAULT_TITLE = '{current_job}{user}@{hostname}: {cwd} | tako'


def _replace_home(x):
   home = builtins.__tako_env__['HOME']
   if x.startswith(home):
       x = x.replace(home, '~', 1)
   return x

def _collapsed_pwd():
    sep = os.sep
    pwd = PROMPT_FIELDS['cwd']().split(sep)
    l = len(pwd)
    leader = sep if l>0 and len(pwd[0])==0 else ''
    base = [i[0] if ix != l-1 else i for ix,i in enumerate(pwd) if len(i) > 0]
    return leader + sep.join(base)


def _current_job():
    j = takoshell.jobs.get_next_task()
    if j is not None:
        if not j['bg']:
            cmd = j['cmds'][-1]
            s = cmd[0]
            if s == 'sudo' and len(cmd) > 1:
                s = cmd[1]
            return '{} | '.format(s)
    return ''

PROMPT_FIELDS = dict(
    user=os.environ.get('USER', '<user>'),
    prompt_end='#' if takoshell.tools.IS_SUPERUSER else '$',
    hostname=socket.gethostname().split('.', 1)[0],
    cwd=lambda: _replace_home(builtins.__tako_env__['PWD']),
    cwd_dir=lambda: os.path.dirname(PROMPT_FIELDS['cwd']()),
    cwd_base=lambda: os.path.basename(PROMPT_FIELDS['cwd']()),
    short_cwd=_collapsed_pwd,
    current_job=_current_job,
)

defaults = {
    'AUTO_CD': False,
    'AUTO_PUSHD': False,
    'CASE_SENSITIVE_COMPLETIONS': True,
    'DIRSTACK_SIZE': 20,
    'EXPAND_ENV_VARS': True,
    'FUZZY_PATH_COMPLETION': False,
    'IGNOREEOF': False,
    'INDENT': '    ',
    'MULTILINE_PROMPT': '.',
    'NUMBER_MODE': 'hybrid',
    'PRETTY_PRINT_RESULTS': True,
    'PROMPT': DEFAULT_PROMPT,
    'PUSHD_MINUS': False,
    'PUSHD_SILENT': False,
    'RAISE_SUBPROC_ERROR': False,
    'SUBSEQUENCE_PATH_COMPLETION': True,
    'SUGGEST_COMMANDS': True,
    'SUGGEST_MAX_NUM': 5,
    'SUGGEST_THRESHOLD': 3,
    'TITLE': DEFAULT_TITLE,
    'UPDATE_OS_ENVIRON': False,
    'CACHE_SCRIPTS': True,
    'CACHE_EVERYTHING': False,
    'CONFIG_DIR': os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser(os.path.join('~', '.config'))), 'tako'),
    'DATA_DIR': os.path.join(os.environ.get('XDG_DATA_HOME', os.path.expanduser(os.path.join('~', '.local', 'share'))), 'tako'),
    'ENCODING': sys.getdefaultencoding(),
    'ENCODING_ERRORS': 'surrogateescape',
    'SHOW_TRACEBACK': False,
    'TRACEBACK_LOGFILE': None,
    'STORE_STDIN': False,
    'ALIASES': takoshell.aliases.Aliases(takoshell.aliases.default_aliases),
    'PROMPT_FIELDS': PROMPT_FIELDS,
    'BASH_COMPLETIONS': ('/etc/bash_completion',
                         '/usr/share/bash-completion',
                         '/usr/share/bash-completion/completions'),
    'HISTORY_SIZE': 8128,
    'SHELL_TYPE': 'readline',
    'PLUGINS': Settings(),
    'HOOKS': defaultdict(list),
}

defaults['HISTORY_FILE'] = os.path.join(defaults['DATA_DIR'], 'history')

for i in (defaults['CONFIG_DIR'], defaults['DATA_DIR']):
    if not os.path.isdir(i):
        os.makedirs(i)

tako_settings = Settings(defaults)
