from .lexer import (
    TOKEN_ID_WHITESPACE, TOKEN_ID_IDENTIFIER,
    TOKEN_ID_STRING_SINGLE_QUOTES, TOKEN_ID_STRING_DOUBLE_QUOTES,
    TOKEN_ID_SYMBOL, TOKEN_ID_STATEMENT_END)
from .nodes.base import ParserError
from .nodes.expression import ExpressionNode
from .nodes.wrapper import TemplateNode, StatementBodyNode


class Parser:
    def __init__(self, engine=None):
        self.engine = engine
        self._tokens = None
        self._line_num = -1
        self._peeked = None

    @property
    def line_num(self):
        return self._line_num

    def parse(self, tokens):
        if self._tokens is not None:
            raise Exception("The parser is already parsing!")

        self._tokens = iter(tokens)
        tb = TemplateNode()
        tb.parse(self)
        return tb

    def read(self):
        if self._peeked is None:
            try:
                r = next(self._tokens)
                self._line_num = r[0]
                return r
            except StopIteration:
                return None
        p = self._peeked
        self._peeked = None
        return p

    def readValue(self):
        _, _, value = self.read()
        return value

    def peek(self):
        if self._peeked is None:
            try:
                self._peeked = next(self._tokens)
            except StopIteration:
                return None
        return self._peeked

    def peekTokenId(self):
        p = self.peek()
        if p is not None:
            return p[1]
        return None

    def peekValue(self):
        p = self.peek()
        if p is not None:
            return p[2]
        return None

    def expect(self, expected_token_id, expected_value=None):
        tup = self.read()
        if tup is None:
            raise ParserError(self._line_num, "unexpected end of file")
        line_num, token_id, value = tup
        if token_id != expected_token_id:
            raise ParserError(line_num, "unexpected token '%s'" % value)
        if expected_value is not None and value != expected_value:
            raise ParserError(line_num, "unexpected token '%s', "
                              "expected '%s'." % (value, expected_value))
        return value

    def expectAny(self, expected_token_ids, expected_value=None):
        tup = self.read()
        if tup is None:
            raise ParserError(self._line_num, "unexpected end of file")
        line_num, token_id, value = tup
        if token_id not in expected_token_ids:
            raise ParserError(line_num, "unexpected token '%s'" % value)
        if expected_value is not None and value != expected_value:
            raise ParserError(line_num, "unexpected token '%s', "
                              "expected '%s'." % (value, expected_value))
        return value

    def isNext(self, token_id, value=None):
        p = self.peek()
        if p is None:
            return False
        if p[1] != token_id:
            return False
        if value is not None and p[2] != value:
            return False
        return True

    def skip(self, token_id):
        while True:
            p = self.peek()
            if p is not None:
                if p[1] == token_id:
                    self.read()
                    continue
            break

    def skipWhitespace(self):
        self.skip(TOKEN_ID_WHITESPACE)

    def expectIdentifier(self, value=None):
        return self.expect(TOKEN_ID_IDENTIFIER, value)

    def expectSymbol(self, value=None):
        return self.expect(TOKEN_ID_SYMBOL, value)

    def expectString(self, value=None):
        return self.expectAny(
            (TOKEN_ID_STRING_SINGLE_QUOTES, TOKEN_ID_STRING_DOUBLE_QUOTES),
            value)

    def expectStatementEnd(self):
        return self.expect(TOKEN_ID_STATEMENT_END)

    def parseExpression(self, parent_node, with_tail=True):
        en = ExpressionNode(with_tail)
        parent_node.add(en)
        en.parse(self)
        return en

    def parseUntilStatement(self, parent_node, name):
        bn = StatementBodyNode(name)
        parent_node.add(bn)
        bn.parse(self)
        return bn
