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

# -*- coding: utf-8 -*-
"""A (tab-)completer for takoshell."""
import builtins

from collections import Sequence

class Completer(object):
    """This provides a list of optional completions for the tako shell."""
    def complete(self, prefix, line, begidx, endidx, ctx=None):
        """Complete the string, given a possible execution context.

        Parameters
        ----------
        prefix : str
            The string to match
        line : str
            The line that prefix appears on.
        begidx : int
            The index in line that prefix starts on.
        endidx : int
            The index in line that prefix ends on.
        ctx : Iterable of str (ie dict, set, etc), optional
            Names in the current execution context.

        Returns
        -------
        rtn : list of str
            Possible completions of prefix, sorted alphabetically.
        lprefix : int
            Length of the prefix to be replaced in the completion
        """
        ctx = ctx or {}
        for func in builtins.__tako_completers__.values():
            try:
                out = func(prefix, line, begidx, endidx, ctx)
            except StopIteration:
                return set(), len(prefix)
            if isinstance(out, Sequence):
                res, lprefix = out
            else:
                res = out
                lprefix = len(prefix)
            if res is not None and len(res) != 0:
                return tuple(sorted(res)), lprefix
        return set(), lprefix
