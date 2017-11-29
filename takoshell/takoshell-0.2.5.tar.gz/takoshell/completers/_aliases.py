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

import builtins

from collections import OrderedDict

from takoshell.completers.tools import justify
from takoshell.completers.bash import complete_from_bash, update_bash_completion

VALID_ACTIONS = frozenset({'add', 'remove', 'list', 'bash'})


def _add_one_completer(name, func, loc='end'):
    new = OrderedDict()
    if loc == 'start':
        new[name] = func
        for (k, v) in builtins.__tako_completers__.items():
            new[k] = v
    elif loc == 'end':
        for (k, v) in builtins.__tako_completers__.items():
            new[k] = v
        new[name] = func
    else:
        direction, rel = loc[0], loc[1:]
        found = False
        for (k, v) in builtins.__tako_completers__.items():
            if rel == k and direction == '<':
                new[name] = func
                found = True
            new[k] = v
            if rel == k and direction == '>':
                new[name] = func
                found = True
        if not found:
            new[name] = func
    builtins.__tako_completers__.clear()
    builtins.__tako_completers__.update(new)


def _bash_completer(args, stdin=None):
    if len(args) != 1:
        return None, 'completer bash takes exactly 1 argument.\n', 1
    if args[0] == 'enable':
        update_bash_completion()
        _add_one_completer('bash', complete_from_bash, '<man')
        return 'Bash completion enabled.\n'
    elif args[0] == 'disable':
        return _remove_completer(['bash'], stdin)
    else:
        return 'Valid arguments are: "enable" or "disable".\n'


def _list_completers(args, stdin=None):
    o = "Registered Completer Functions: \n"
    _comp = builtins.__tako_completers__
    ml = max((len(i) for i in _comp), default=0)
    _strs = []
    for c in _comp:
        if _comp[c].__doc__ is None:
            doc = 'No description provided'
        else:
            doc = ' '.join(_comp[c].__doc__.split())
        doc = justify(doc, 80, ml + 3)
        _strs.append('{: >{}} : {}'.format(c, ml, doc))
    return o + '\n'.join(_strs) + '\n'


def _remove_completer(args, stdin=None):
    err = None
    if len(args) != 1:
        err = "completer remove takes exactly 1 argument."
    else:
        name = args[0]
        if name not in builtins.__tako_completers__:
            err = ("The name %s is not a registered "
                   "completer function.") % name
    if err is None:
        del builtins.__tako_completers__[name]
        return
    else:
        return None, err + '\n', 1


def _register_completer(args, stdin=None):
    err = None
    if len(args) not in {2, 3}:
        err = ("completer add takes either 2 or 3 arguments.\n"
               "For help, run:  completer help add")
    else:
        name = args[0]
        func = args[1]
        if name in builtins.__tako_completers__:
            err = ("The name %s is already a registered "
                   "completer function.") % name
        else:
            if func in builtins.__tako_ctx__:
                if not callable(builtins.__tako_ctx__[func]):
                    err = "%s is not callable" % func
            else:
                err = "No such function: %s" % func
    if err is None:
        position = "start" if len(args) == 2 else args[2]
        func = builtins.__tako_ctx__[func]
        _add_one_completer(name, func, position)
    else:
        return None, err + '\n', 1


def completer_alias(args, stdin=None):
    err = None
    if len(args) == 0 or args[0] not in (VALID_ACTIONS | {'help'}):
        err = ('Please specify an action.  Valid actions are: '
               '"add", "remove", "list", "bash", or "help".')
    elif args[0] == 'help':
        if len(args) == 1 or args[1] not in VALID_ACTIONS:
            return ('Valid actions are: add, remove, list, bash.  For help with a '
                    'specific action, run: completer help ACTION\n')
        elif args[1] == 'add':
            return COMPLETER_ADD_HELP_STR
        elif args[1] == 'remove':
            return COMPLETER_REMOVE_HELP_STR
        elif args[1] == 'list':
            return COMPLETER_LIST_HELP_STR
        elif args[1] == 'bash':
            return COMPLETER_BASH_HELP_STR

    if err is not None:
        return None, err + '\n', 1

    if args[0] == 'add':
        func = _register_completer
    elif args[0] == 'remove':
        func = _remove_completer
    elif args[0] == 'list':
        func = _list_completers
    elif args[0] == 'bash':
        func = _bash_completer
    return func(args[1:], stdin=stdin)

COMPLETER_BASH_HELP_STR = """
completer bash: enable/disable tab completion using Bash

Usage:
    completer bash enable
    completer bash disable
""".lstrip()

COMPLETER_LIST_HELP_STR = """
completer list: list the active completers, in order

Usage:
    completer list
""".lstrip()

COMPLETER_REMOVE_HELP_STR = """
completer remove: removes a completer from takoshell

Usage:
    completer remove NAME

NAME is a unique name of a completer (run "completer list" to see the current
     completers in order)
""".lstrip()

COMPLETER_ADD_HELP_STR = """
completer add: adds a new completer to tako

Usage:
    completer add NAME FUNC [POS]

NAME is a unique name to use in the listing (run "completer list" to see the
     current completers in order)

FUNC is the name of a completer function to use.  This should be a function
     of the following arguments, and should return a set of valid completions
     for the given prefix.  If this completer should not be used in a given
     context, it should return an empty set or None.

     Arguments to FUNC:
       * prefix: the string to be matched
       * line: a string representing the whole current line, for context
       * begidx: the index at which prefix starts in line
       * endidx: the index at which prefix ends in line
       * ctx: the current Python environment

     If the completer expands the prefix in any way, it should return a tuple
     of two elements: the first should be the set of completions, and the
     second should be the length of the modified prefix (for an example, see
     takoshell.completers.path.complete_path).

POS (optional) is a position into the list of completers at which the new
     completer should be added.  It can be one of the following values:
       * "start" indicates that the completer should be added to the start of
                 the list of completers (it should be run before all others)
       * "end" indicates that the completer should be added to the end of the
               list of completers (it should be run after all others)
       * ">KEY", where KEY is a pre-existing name, indicates that this should
                 be added after the completer named KEY
       * "<KEY", where KEY is a pre-existing name, indicates that this should
                 be added before the completer named KEY

     If POS is not provided, the default value is "start"
""".lstrip()
