from ..lexer import TOKEN_ID_SYMBOL, TOKEN_ID_WHITESPACE
from .base import LeafParserNode, MultiChildrenParserNode


class StringNode(LeafParserNode):
    pass


class FloatNode(LeafParserNode):
    pass


class IntegerNode(LeafParserNode):
    pass


class BooleanNode(LeafParserNode):
    pass


class NoneNode(LeafParserNode):
    def __init__(self):
        super().__init__(None)


class ListNode(MultiChildrenParserNode):
    def parse(self, parser):
        needs_comma = False
        while not parser.isNext(TOKEN_ID_SYMBOL, ']'):
            if needs_comma:
                parser.expect(TOKEN_ID_SYMBOL, ',')
                parser.skip(TOKEN_ID_WHITESPACE)
            parser.parseExpression(self)
            parser.skip(TOKEN_ID_WHITESPACE)
            needs_comma = True

    def render(self, ctx, data, out):
        return [c.render(ctx, data, out) for c in self.children]

    def compile(self, ctx, out):
        val = '['
        for c in self.children:
            c.compile(ctx, out)
            val += '%s, ' % ctx.popvar()
        val += ']'
        ctx.pushvar(val)


const_identifiers = {
    'true': BooleanNode(True),
    'True': BooleanNode(True),
    'false': BooleanNode(False),
    'False': BooleanNode(False),
    'none': NoneNode(),
    'None': NoneNode()
}
