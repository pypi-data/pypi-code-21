#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division


import ast
import operator

from .tools import p3_str


OP = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.BitXor: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def eval_node(node):
    try:
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return OP[type(node.op)](eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return OP[type(node.op)](eval_node(node.operand))
    except KeyError:
        pass

    raise NotImplementedError(node)


def eval_expr(text):
    node = ast.parse(text.strip(), mode="eval")

    return eval_node(node.body)


def wikieval(text):
    """
    Evaluate an arithmetic expression
    """
    text = text.strip()

    if not text:
        return ""

    out = eval_expr(text)

    out = round(out, 14)

    int_out = int(out)

    if int_out == out:
        out = int_out

    return p3_str(out)
