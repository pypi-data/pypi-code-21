from ..compiler import write_render_opt_aliases
from ..lexer import (
    TOKEN_ID_TEXT, TOKEN_ID_COMMENT, TOKEN_ID_WHITESPACE,
    TOKEN_ID_IDENTIFIER,
    TOKEN_ID_EXPRESSION_BEGIN, TOKEN_ID_EXPRESSION_END,
    TOKEN_ID_STATEMENT_BEGIN, TOKEN_ID_STATEMENT_END)
from .base import SingleChildParserNode, MultiChildrenParserNode, ParserError
from .expression import ExpressionWrapperNode
from .text import TextNode, CommentNode


class WrapperNode(MultiChildrenParserNode):
    def __init__(self):
        super().__init__()
        self.stop_on_statement = None

    def parse(self, parser):
        # Loop optimization.
        parser_read = parser.read
        parser_peek = parser.peek
        parser_skip = parser.skip
        parser_expect = parser.expect
        self_add = self.add
        self_recurseInto = self.recurseInto

        while True:
            t = parser_read()
            if t is not None:
                line_num, token_id, value = t
                if token_id == TOKEN_ID_TEXT:
                    self_add(TextNode(value))
                elif token_id == TOKEN_ID_EXPRESSION_BEGIN:
                    parser_skip(TOKEN_ID_WHITESPACE)
                    self_recurseInto(parser, ExpressionWrapperNode())
                    parser_skip(TOKEN_ID_WHITESPACE)
                    parser_expect(TOKEN_ID_EXPRESSION_END)
                elif token_id == TOKEN_ID_STATEMENT_BEGIN:
                    parser_skip(TOKEN_ID_WHITESPACE)
                    sos = self.stop_on_statement
                    if sos is not None:
                        _, tid, v = parser_peek()
                        if tid == TOKEN_ID_IDENTIFIER and v in sos:
                            break
                    swn = StatementWrapperNode()
                    self_recurseInto(parser, swn)
                    if not swn.own_close:
                        parser_skip(TOKEN_ID_WHITESPACE)
                        parser_expect(TOKEN_ID_STATEMENT_END)
                elif token_id == TOKEN_ID_COMMENT:
                    self_add(CommentNode(value))
                else:
                    raise ParserError(
                        line_num,
                        "unexpected token: %s (%d)" % (value, token_id))
            else:
                break


class TemplateNode(WrapperNode):
    def compile(self, ctx, out):
        ctx.startScope()
        out.write('def render_template(ctx, data, out_write):\n')
        out.push(False)
        write_render_opt_aliases(out)
        for c in self.children:
            c.compile(ctx, out)
        out.pull()
        ctx.endScope()


class StatementWrapperNode(SingleChildParserNode):
    @property
    def own_close(self):
        return self.child.own_close

    def parse(self, parser):
        statement_name = parser.expect(TOKEN_ID_IDENTIFIER)
        node = self._getStatementNode(
            parser.line_num, statement_name, parser.engine)
        parser.skipWhitespace()
        self.recurseInto(parser, node)

    def render(self, ctx, data, out):
        self.child.render(ctx, data, out)

    def compile(self, ctx, out):
        self.child.compile(ctx, out)

    def _getStatementNode(self, lineno, name, engine):
        if engine is None:
            raise ParserError(
                lineno,
                "can't parse statement '%s', no engine active." % name)

        for e in engine.extensions:
            for nc in e.getStatementNodes():
                if nc.name is None:
                    raise Exception(
                        "StatementNode '%s' doesn't define a name." % nc)
                if nc.name == name:
                    node = nc()
                    return node
        raise ParserError(lineno, "unknown statement '%s'." % name)


class StatementBodyNode(WrapperNode):
    def __init__(self, until):
        super().__init__()
        if not isinstance(until, list):
            until = [until]
        self.stop_on_statement = until
