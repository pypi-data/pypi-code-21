from .base import ParserNode, SingleChildParserNode
from .tests import TestNode


class UnaryOperatorNode(SingleChildParserNode):
    __op_precedence__ = -1
    __op_type__ = 1

    def parse(self, parser):
        en = parser.parseExpression(self, with_tail=False)
        self.child = en.child


class NotOperatorNode(UnaryOperatorNode):
    __op_precedence__ = 20

    def render(self, ctx, data, out):
        return not self.child.render(ctx, data, out)

    def compile(self, ctx, out):
        self.child.compile(ctx, out)
        ctx.pushvar('(not %s)' % ctx.popvar())


class BinaryOperatorNode(ParserNode):
    __op_precedence__ = -1
    __op_type__ = 2

    def __init__(self):
        super().__init__()
        self.child1 = None
        self.child2 = None

    def iterChildren(self):
        yield self.child1
        yield self.child2

    def add(self, node):
        if self.child1 is None:
            self.child1 = node
        elif self.child2 is None:
            self.child2 = node
        else:
            raise Exception("This binary operator already has 2 children.")

    def parse(self, parser):
        en = parser.parseExpression(self, with_tail=False)
        self.child2 = en.child

    def _getChildrenValues(self, ctx, data, out):
        a = self.child1.render(ctx, data, out)
        b = self.child2.render(ctx, data, out)
        return (a, b)

    def _getChildrenVarNames(self, ctx, out):
        self.child1.compile(ctx, out)
        self.child2.compile(ctx, out)
        b = ctx.popvar()
        a = ctx.popvar()
        return (a, b)


class ContainsNode(BinaryOperatorNode):
    __op_precedence__ = 10

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a in b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s in %s)' % (a, b))


class AndBooleanNode(BinaryOperatorNode):
    __op_precedence__ = 9

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a and b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s and %s)' % (a, b))


class OrBooleanNode(BinaryOperatorNode):
    __op_precedence__ = 8

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a or b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s or %s)' % (a, b))


class AddOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 1

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a + b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s + %s)' % (a, b))


class SubtractOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 1

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a - b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s - %s)' % (a, b))


class DivideOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 2

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a / b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s / %s)' % (a, b))


class DivideIntegerOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 2

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a // b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s // %s)' % (a, b))


class ModuloOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 3

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a % b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s %% %s)' % (a, b))


class MultiplyOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 2

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a * b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s * %s)' % (a, b))


class PowerOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 3

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a ** b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s ** %s)' % (a, b))


class EqualOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 20

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a == b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s == %s)' % (a, b))


class InequalOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 20

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a != b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s != %s)' % (a, b))


class GreaterOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 20

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a > b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s > %s)' % (a, b))


class GreaterOrEqualOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 20

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a >= b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s >= %s)' % (a, b))


class LessOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 20

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a < b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s < %s)' % (a, b))


class LessOrEqualOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 20

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return a <= b

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(%s <= %s)' % (a, b))


class StringConcatOperatorNode(BinaryOperatorNode):
    __op_precedence__ = 10

    def render(self, ctx, data, out):
        a, b = self._getChildrenValues(ctx, data, out)
        return str(a) + str(b)

    def compile(self, ctx, out):
        a, b = self._getChildrenVarNames(ctx, out)
        ctx.pushvar('(str(%s) + str(%s))' % (a, b))


binary_operator_nodes = {
    '+': AddOperatorNode,
    '-': SubtractOperatorNode,
    '/': DivideOperatorNode,
    '//': DivideIntegerOperatorNode,
    '%': ModuloOperatorNode,
    '*': MultiplyOperatorNode,
    '**': PowerOperatorNode,
    '==': EqualOperatorNode,
    '!=': InequalOperatorNode,
    '>': GreaterOperatorNode,
    '>=': GreaterOrEqualOperatorNode,
    '<': LessOperatorNode,
    '<=': LessOrEqualOperatorNode,
    '~': StringConcatOperatorNode
}


misc_operator_nodes = {
    'is': TestNode,
    'in': ContainsNode,
    'and': AndBooleanNode,
    'or': OrBooleanNode,
}
