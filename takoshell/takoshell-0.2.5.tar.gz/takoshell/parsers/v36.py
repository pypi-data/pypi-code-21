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
"""Implements the tako parser for Python v3.6."""
from takoshell import ast
from takoshell.parsers.v35 import Parser as ThreeFiveParser
from takoshell.parsers.base import store_ctx, ensure_has_elts


class Parser(ThreeFiveParser):
    """A Python v3.6 compliant parser for the tako language."""

    def p_comp_for(self, p):
        """comp_for : FOR exprlist IN or_test comp_iter_opt"""
        targs, it, p5 = p[2], p[4], p[5]
        if len(targs) == 1:
            targ = targs[0]
        else:
            targ = ensure_has_elts(targs)
        store_ctx(targ)
        # only difference with base should be the is_async=0
        comp = ast.comprehension(target=targ, iter=it, ifs=[], is_async=0)
        comps = [comp]
        p0 = {'comps': comps}
        if p5 is not None:
            comps += p5.get('comps', [])
            comp.ifs += p5.get('if', [])
        p[0] = p0

