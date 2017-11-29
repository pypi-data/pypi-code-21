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


def complete_completer(prefix, line, start, end, ctx):
    """
    Completion for "completer"
    """
    args = line.split(' ')
    if len(args) == 0 or args[0] != 'completer':
        return None
    curix = args.index(prefix)
    compnames = set(builtins.__tako_completers__.keys())
    if curix == 1:
        possible = {'list', 'help', 'add', 'remove', 'bash'}
    elif curix == 2:
        if args[1] == 'help':
            possible = {'list', 'add', 'remove', 'bash'}
        elif args[1] == 'remove':
            possible = compnames
        elif args[1] == 'bash':
            possible = {'enable', 'disable'}
        else:
            raise StopIteration
    else:
        if args[1] != 'add':
            raise StopIteration
        if curix == 3:
            possible = {i
                        for i, j in builtins.__tako_ctx__.items()
                        if callable(j)}
        elif curix == 4:
            possible = ({'start', 'end'} |
                        {'>' + n for n in compnames} |
                        {'<' + n for n in compnames})
        else:
            raise StopIteration
    return {i for i in possible if i.startswith(prefix)}
