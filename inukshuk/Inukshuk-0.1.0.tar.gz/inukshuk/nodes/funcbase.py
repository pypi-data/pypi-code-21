from ..lexer import TOKEN_ID_SYMBOL, TOKEN_ID_IDENTIFIER
from .base import MultiChildrenParserNode, ParserError


class FuncCallNode(MultiChildrenParserNode):
    def __init__(self):
        super().__init__()
        self.func_name = None
        self.kw_children = {}

    def parse(self, parser):
        self.func_name = parser.expect(TOKEN_ID_IDENTIFIER)
        _parse_args_kwargs(self, parser, self.children, self.kw_children)

    def render(self, ctx, data, out):
        arg_values = list([c.render(ctx, data, out) for c in self.children])
        kwarg_values = dict(
            {n: c.render(ctx, data, out)
             for n, c in self.kw_children.items()})
        func = self._getFunc(ctx, self.func_name)
        return ctx.invoke(data, out, func, *arg_values, **kwarg_values)

    def compile(self, ctx, out):
        args = []
        for c in self.children:
            c.compile(ctx, out)
            args.append(ctx.popvar())

        kwargs = {}
        for n, c in self.kw_children.items():
            c.compile(ctx, out)
            kwargs[n] = ctx.popvar()

        out.indent()
        fname = ctx.varname('func')
        out.write('%s = %s\n' %
                  (fname, self._compileGetFunc(self.func_name)))
        out.indent()
        val = ctx.varname('f_out')
        out.write('%s = ctx_invoke(data, out_write, %s' % (val, fname))
        if args:
            out.write(', ')
            out.write(', '.join(args))
        if kwargs:
            for n, a in kwargs.items():
                out.write(', %s=%s' % (n, a))
        out.write(')\n')
        ctx.pushvar(val)

    def _getFunc(self, name):
        raise NotImplementedError()

    def _compileGetFunc(self, name):
        raise NotImplementedError()


def _parse_args_kwargs(node, parser, arg_nodes, kwarg_nodes):
    from .expression import (
        InvalidOperatorError, ExpressionNode, ContextQueryNode)

    if parser.isNext(TOKEN_ID_SYMBOL, '('):
        line_num, _, _ = parser.read()
        parser.skipWhitespace()

        needs_comma = False
        has_first_kwarg = False
        while not parser.isNext(TOKEN_ID_SYMBOL, ')'):
            if needs_comma:
                parser.skipWhitespace()
                parser.expect(TOKEN_ID_SYMBOL, ',')
                parser.skipWhitespace()

            en = ExpressionNode()
            try:
                en.parse(parser)
            except InvalidOperatorError as ioe:
                # If we parsed a simple query expression up to an `=`
                # sign, this is actually a keyword argument.
                if ioe.op_name != '=':
                    raise
                query_node = ioe.value_node
                if not isinstance(query_node, ContextQueryNode):
                    raise
                if (query_node.query_type != ContextQueryNode.TYPE_PROPERTY or
                        query_node.has_tail):
                    raise

                # Keyword! Discard the expression node that failed (we grab
                # the keyword name directly from the exception), and
                # read that keyword argument's value.
                kwname = query_node.name

                en = ExpressionNode()
                en.parse(parser)
                kwarg_nodes[kwname] = en.child
                has_first_kwarg = True
            else:
                # Normal expression argument.
                if has_first_kwarg:
                    raise ParserError(
                        line_num,
                        "can't specify non-keyword argument after keyword "
                        "arguments have been specified")
                arg_nodes.append(en.child)

            needs_comma = True

        parser.expect(TOKEN_ID_SYMBOL, ')')
