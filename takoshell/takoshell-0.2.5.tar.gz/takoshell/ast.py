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
"""The tako abstract syntax tree node."""
# These are imported into our module namespace for the benefit of parser.py.
# pylint: disable=unused-import
from ast import (Module, Num, Expr, Str, Bytes, UnaryOp, UAdd, USub, Invert,
    BinOp, Add, Sub, Mult, Div, FloorDiv, Mod, Pow, Compare, Lt, Gt,
    LtE, GtE, Eq, NotEq, In, NotIn, Is, IsNot, Not, BoolOp, Or, And,
    Subscript, Load, Slice, ExtSlice, List, Tuple, Set, Dict, AST, NameConstant,
    Name, GeneratorExp, Store, comprehension, ListComp, SetComp, DictComp,
    Assign, AugAssign, BitXor, BitAnd, BitOr, LShift, RShift, Assert, Delete,
    Del, Pass, Raise, Import, alias, ImportFrom, Continue, Break, Yield,
    YieldFrom, Return, IfExp, Lambda, arguments, arg, Call, keyword,
    Attribute, Global, Nonlocal, If, While, For, withitem, With, Try,
    ExceptHandler, FunctionDef, ClassDef, Starred, NodeTransformer, NodeVisitor,
    Interactive, Expression, Index, literal_eval, dump, walk, increment_lineno,
    parse)
from ast import Ellipsis  # pylint: disable=redefined-builtin
# pylint: enable=unused-import
import textwrap
import itertools

from takoshell.tools import subproc_toks, find_next_break
from takoshell.platform import PYTHON_VERSION_INFO

if PYTHON_VERSION_INFO >= (3, 5, 0):
    # pylint: disable=unused-import
    # pylint: disable=no-name-in-module
    from ast import MatMult, AsyncFunctionDef, AsyncWith, AsyncFor, Await
else:
    MatMult = AsyncFunctionDef = AsyncWith = AsyncFor = Await = None

STATEMENTS = (FunctionDef, ClassDef, Return, Delete, Assign, AugAssign, For,
              While, If, With, Raise, Try, Assert, Import, ImportFrom, Global,
              Nonlocal, Expr, Pass, Break, Continue)


def leftmostname(node):
    """Attempts to find the first name in the tree."""
    if isinstance(node, Name):
        rtn = node.id
    elif isinstance(node, (BinOp, Compare)):
        rtn = leftmostname(node.left)
    elif isinstance(node, (Attribute, Subscript, Starred, Expr)):
        rtn = leftmostname(node.value)
    elif isinstance(node, Call):
        rtn = leftmostname(node.func)
    elif isinstance(node, UnaryOp):
        rtn = leftmostname(node.operand)
    elif isinstance(node, BoolOp):
        rtn = leftmostname(node.values[0])
    elif isinstance(node, Assign):
        rtn = leftmostname(node.targets[0])
    elif isinstance(node, (Str, Bytes)):
        # handles case of "./my executable"
        rtn = leftmostname(node.s)
    elif isinstance(node, Tuple) and len(node.elts) > 0:
        # handles case of echo ,1,2,3
        rtn = leftmostname(node.elts[0])
    else:
        rtn = None
    return rtn


def get_lineno(node, default=0):
    """Gets the lineno of a node or returns the default."""
    return getattr(node, 'lineno', default)


def min_line(node):
    """Computes the minimum lineno."""
    node_line = get_lineno(node)
    return min(map(get_lineno, walk(node), itertools.repeat(node_line)))


def max_line(node):
    """Computes the maximum lineno."""
    return max(map(get_lineno, walk(node)))


def get_col(node, default=-1):
    """Gets the col_offset of a node, or returns the default"""
    return getattr(node, 'col_offset', default)


def min_col(node):
    """Computes the minimum col_offset."""
    return min(map(get_col, walk(node), itertools.repeat(node.col_offset)))


def max_col(node):
    """Returns the maximum col_offset of the node and all sub-nodes."""
    col = getattr(node, 'max_col', None)
    if col is None:
        col = max(map(get_col, walk(node)))
    return col


def get_id(node, default=None):
    """Gets the id attribute of a node, or returns a default."""
    return getattr(node, 'id', default)


def has_elts(x):
    """Tests if x is an AST node with elements."""
    return isinstance(x, AST) and hasattr(x, 'elts')


def tako_call(name, args, lineno=None, col=None):
    """Creates the AST node for calling a function of a given name."""
    return Call(func=Name(id=name, ctx=Load(), lineno=lineno, col_offset=col),
                args=args, keywords=[], starargs=None, kwargs=None,
                lineno=lineno, col_offset=col)


def isdescendable(node):
    """Deteremines whether or not a node is worth visiting. Currently only
    UnaryOp and BoolOp nodes are visited.
    """
    return isinstance(node, (UnaryOp, BoolOp))


class CtxAwareTransformer(NodeTransformer):
    """Transforms a tako AST based to use subprocess calls when
    the first name in an expression statement is not known in the context.
    This assumes that the expression statement is instead parseable as
    a subprocess.
    """

    def __init__(self, parser):
        """Parameters
        ----------
        parser : takoshell.Parser
            A parse instance to try to parse suprocess statements with.
        """
        super(CtxAwareTransformer, self).__init__()
        self.parser = parser
        self.input = None
        self.contexts = []
        self.lines = None
        self.mode = None
        self._nwith = 0

    def ctxvisit(self, node, inp, ctx, mode='exec'):
        """Transforms the node in a context-dependent way.

        Parameters
        ----------
        node : ast.AST
            A syntax tree to transform.
        input : str
            The input code in string format.
        ctx : dict
            The root context to use.

        Returns
        -------
        node : ast.AST
            The transformed node.
        """
        self.lines = inp.splitlines()
        self.contexts = [ctx, set()]
        self.mode = mode
        self._nwith = 0
        node = self.visit(node)
        del self.lines, self.contexts, self.mode
        self._nwith = 0
        return node

    def ctxupdate(self, iterable):
        """Updated the most recent context."""
        self.contexts[-1].update(iterable)

    def ctxadd(self, value):
        """Adds a value the most recent context."""
        self.contexts[-1].add(value)

    def ctxremove(self, value):
        """Removes a value the most recent context."""
        for ctx in reversed(self.contexts):
            if value in ctx:
                ctx.remove(value)
                break

    def try_subproc_toks(self, node, strip_expr=False):
        """Tries to parse the line of the node as a subprocess."""
        line = self.lines[node.lineno - 1]
        if self.mode == 'eval':
            mincol = len(line) - len(line.lstrip())
            maxcol = None
        else:
            mincol = min_col(node)
            maxcol = max_col(node)
            if mincol == maxcol:
                maxcol = find_next_break(line, mincol=mincol,
                                         lexer=self.parser.lexer)
            else:
                maxcol += 1
        spline = subproc_toks(line,
                              mincol=mincol,
                              maxcol=maxcol,
                              returnline=False,
                              lexer=self.parser.lexer)
        if spline is None:
            return node
        try:
            newnode = self.parser.parse(spline, mode=self.mode)
            newnode = newnode.body
            if not isinstance(newnode, AST):
                # take the first (and only) Expr
                newnode = newnode[0]
            increment_lineno(newnode, n=node.lineno - 1)
            newnode.col_offset = node.col_offset
        except SyntaxError:
            newnode = node
        if strip_expr and isinstance(newnode, Expr):
            newnode = newnode.value
        return newnode

    def is_in_scope(self, node):
        """Determines whether or not the current node is in scope."""
        names = gather_names(node)
        if not names:
            return True
        inscope = False
        for ctx in reversed(self.contexts):
            names -= ctx
            if not names:
                inscope = True
                break
        return inscope

    #
    # Replacement visitors
    #

    def visit_Expression(self, node):
        """Handle visiting an expression body."""
        if isdescendable(node.body):
            node.body = self.visit(node.body)
        body = node.body
        inscope = self.is_in_scope(body)
        if not inscope:
            node.body = self.try_subproc_toks(body)
        return node

    def visit_Expr(self, node):
        """Handle visiting an expression."""
        if isdescendable(node.value):
            node.value = self.visit(node.value)  # this allows diving into BoolOps
        if self.is_in_scope(node):
            return node
        else:
            newnode = self.try_subproc_toks(node)
            if not isinstance(newnode, Expr):
                newnode = Expr(value=newnode,
                               lineno=node.lineno,
                               col_offset=node.col_offset)
                if hasattr(node, 'max_lineno'):
                    newnode.max_lineno = node.max_lineno
                    newnode.max_col = node.max_col
            return newnode

    def visit_UnaryOp(self, node):
        """Handle visiting an unary operands, like not."""
        if isdescendable(node.operand):
            node.operand = self.visit(node.operand)
        operand = node.operand
        inscope = self.is_in_scope(operand)
        if not inscope:
            node.operand = self.try_subproc_toks(operand, strip_expr=True)
        return node

    def visit_BoolOp(self, node):
        """Handle visiting an boolean operands, like and/or."""
        for i in range(len(node.values)):
            val = node.values[i]
            if isdescendable(val):
                val = node.values[i] = self.visit(val)
            inscope = self.is_in_scope(val)
            if not inscope:
                node.values[i] = self.try_subproc_toks(val, strip_expr=True)
        return node

    #
    # Context aggregator visitors
    #

    def visit_Assign(self, node):
        """Handle visiting an assignment statement."""
        ups = set()
        for targ in node.targets:
            if isinstance(targ, (Tuple, List)):
                ups.update(leftmostname(elt) for elt in targ.elts)
            elif isinstance(targ, BinOp):
                newnode = self.try_subproc_toks(node)
                if newnode is node:
                    ups.add(leftmostname(targ))
                else:
                    return newnode
            else:
                ups.add(leftmostname(targ))
        self.ctxupdate(ups)
        return node

    def visit_Import(self, node):
        """Handle visiting a import statement."""
        for name in node.names:
            if name.asname is None:
                self.ctxadd(name.name)
            else:
                self.ctxadd(name.asname)
        return node

    def visit_ImportFrom(self, node):
        """Handle visiting a "from ... import ..." statement."""
        for name in node.names:
            if name.asname is None:
                self.ctxadd(name.name)
            else:
                self.ctxadd(name.asname)
        return node

    def visit_With(self, node):
        """Handle visiting a with statement."""
        for item in node.items:
            if item.optional_vars is not None:
                self.ctxupdate(gather_names(item.optional_vars))
        self._nwith += 1
        self.generic_visit(node)
        self._nwith -= 1
        return node

    def visit_For(self, node):
        """Handle visiting a for statement."""
        targ = node.target
        if isinstance(targ, (Tuple, List)):
            self.ctxupdate(leftmostname(elt) for elt in targ.elts)
        else:
            self.ctxadd(leftmostname(targ))
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        """Handle visiting a function definition."""
        self.ctxadd(node.name)
        self.contexts.append(set())
        args = node.args
        argchain = [args.args, args.kwonlyargs]
        if args.vararg is not None:
            argchain.append((args.vararg,))
        if args.kwarg is not None:
            argchain.append((args.kwarg,))
        self.ctxupdate(a.arg for a in itertools.chain.from_iterable(argchain))
        self.generic_visit(node)
        self.contexts.pop()
        return node

    def visit_ClassDef(self, node):
        """Handle visiting a class definition."""
        self.ctxadd(node.name)
        self.contexts.append(set())
        self.generic_visit(node)
        self.contexts.pop()
        return node

    def visit_Delete(self, node):
        """Handle visiting a del statement."""
        for targ in node.targets:
            if isinstance(targ, Name):
                self.ctxremove(targ.id)
        self.generic_visit(node)
        return node

    def visit_Try(self, node):
        """Handle visiting a try statement."""
        for handler in node.handlers:
            if handler.name is not None:
                self.ctxadd(handler.name)
        self.generic_visit(node)
        return node

    def visit_Global(self, node):
        """Handle visiting a global statement."""
        self.contexts[1].update(node.names)  # contexts[1] is the global ctx
        self.generic_visit(node)
        return node


def gather_names(node):
    ng = NameGatherer()
    ng.visit(node)
    ng.names.discard(None)
    return ng.names


class NameGatherer(NodeVisitor):
    def __init__(self):
        self.names = set()
        NodeVisitor.__init__(self)

    def generic_visit(self, node):
        self.names.add(get_id(node))
        NodeVisitor.generic_visit(self, node)

    def visit_ListComp(self, node):
        defined_names = set()
        needed_names = gather_names(node.elt)
        for g in node.generators:
            defined_names |= gather_names(g)
            for i in g.ifs:
                needed_names |= gather_names(i)
        self.names |= {i for i in needed_names if i not in defined_names}

    def visit_DictComp(self, node):
        defined_names = set()
        needed_names = gather_names(node.key)
        needed_names |= gather_names(node.value)
        for g in node.generators:
            defined_names |= gather_names(g)
            for i in g.ifs:
                needed_names |= gather_names(i)
        self.names |= {i for i in needed_names if i not in defined_names}

    visit_SetComp = visit_ListComp


def pdump(s, **kwargs):
    """performs a pretty dump of an AST node."""
    if isinstance(s, AST):
        s = dump(s, **kwargs).replace(',', ',\n')
    openers = '([{'
    closers = ')]}'
    lens = len(s) + 1
    if lens == 1:
        return s
    i = min([s.find(o)%lens for o in openers])
    if i == lens - 1:
        return s
    closer = closers[openers.find(s[i])]
    j = s.rfind(closer)
    if j == -1 or j <= i:
        return s[:i+1] + '\n' + textwrap.indent(pdump(s[i+1:]), ' ')
    pre = s[:i+1] + '\n'
    mid = s[i+1:j]
    post = '\n' + s[j:]
    mid = textwrap.indent(pdump(mid), ' ')
    if '(' in post or '[' in post or '{' in post:
        post = pdump(post)
    return pre + mid + post


def pprint(s, *, sep=None, end=None, file=None, flush=False, **kwargs):
    """Performs a pretty print of the AST nodes."""
    print(pdump(s, **kwargs), sep=sep, end=end, file=file, flush=flush)
