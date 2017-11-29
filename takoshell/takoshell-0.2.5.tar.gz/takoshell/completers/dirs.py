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

from takoshell.completers.man import complete_from_man
from takoshell.completers.path import complete_dir


def complete_cd(prefix, line, start, end, ctx):
    """
    Completion for "cd", includes only valid directory names.
    """
    if start != 0 and line.split(' ')[0] == 'cd':
        return complete_dir(prefix, line, start, end, ctx, True)
    return set()


def complete_rmdir(prefix, line, start, end, ctx):
    """
    Completion for "rmdir", includes only valid directory names.
    """
    if start != 0 and line.split(' ')[0] == 'rmdir':
        opts = {i for i in complete_from_man('-', 'rmdir -', 6, 7, ctx)
                if i.startswith(prefix)}
        comps, lp = complete_dir(prefix, line, start, end, ctx, True)
        return comps | opts, lp
    return set()
