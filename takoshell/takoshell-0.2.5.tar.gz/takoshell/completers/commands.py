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
import builtins

from takoshell.tools import executables_in
from takoshell.completers.tools import get_filter_function

SKIP_TOKENS = {'sudo', 'time', 'timeit', 'which', 'showcmd', 'man'}
END_PROC_TOKENS = {'|', '||', '&&', 'and', 'or'}


def complete_command(cmd, line, start, end, ctx):
    """
    Returns a list of valid commands starting with the first argument
    """
    space = ' '
    out = {s + space
           for s in builtins.__tako_commands_cache__
           if get_filter_function()(s, cmd)}
    base = os.path.basename(cmd)
    if os.path.isdir(base):
        out |= {os.path.join(base, i)
                for i in executables_in(base)
                if i.startswith(cmd)}
    return out


def complete_skipper(cmd, line, start, end, ctx):
    """
    Skip over several tokens (e.g., sudo) and complete based on the rest of the
    line.
    """
    parts = line.split(' ')
    skip_part_num = 0
    for i, s in enumerate(parts):
        if s in END_PROC_TOKENS:
            skip_part_num = i + 1
    while len(parts) > skip_part_num:
        if parts[skip_part_num] not in SKIP_TOKENS:
            break
        skip_part_num += 1

    if skip_part_num == 0:
        return set()

    if len(parts) == skip_part_num + 1:
        comp_func = complete_command
    else:
        comp = builtins.__tako_shell__.shell.completer
        comp_func = comp.complete

    skip_len = len(' '.join(line[:skip_part_num])) + 1
    return comp_func(cmd,
                     ' '.join(parts[skip_part_num:]),
                     start - skip_len,
                     end - skip_len,
                     ctx)
