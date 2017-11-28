from ..lexer import (
    TOKEN_ID_WHITESPACE,
    TOKEN_ID_IDENTIFIER, TOKEN_ID_INTEGER, TOKEN_ID_FLOAT,
    TOKEN_ID_STRING_SINGLE_QUOTES, TOKEN_ID_STRING_DOUBLE_QUOTES,
    TOKEN_ID_SYMBOL)
from .base import (
    ParserError, ParserNode, MultiChildrenParserNode)
from .const import (
    StringNode, FloatNode, IntegerNode, ListNode, const_identifiers)
from .filters import FilterNode
from .operators import (
    NotOperatorNode, binary_operator_nodes, misc_operator_nodes)


class InvalidOperatorError(Exception):
    def __init__(self, value_node, op_name):
        super().__init__("Invalid operator: %s" % op_name)
        self.value_node = value_node
        self.op_name = op_name


class ExpressionNode(ParserNode):
    def __init__(self, with_tail=True):
        super().__init__()
        self.child = None
        self.with_tail = with_tail

    def iterChildren(self):
        yield self.child

    def add(self, node):
        if self.child is None:
            self.child = node
        else:
            raise Exception("This node already has a child: %s" % self.child)

    def parse(self, parser):
        parser_read = parser.read
        parser_peek = parser.peek
        parser_expect = parser.expect
        parser_skip = parser.skip

        _, token_id, value = parser_peek()
        if token_id == TOKEN_ID_SYMBOL and value == '(':
            parser_read()
            parser_skip(TOKEN_ID_WHITESPACE)
            self.recurseInto(parser, ExpressionNode())
            parser_skip(TOKEN_ID_WHITESPACE)
            parser_expect(TOKEN_ID_SYMBOL, ')')
            parser_skip(TOKEN_ID_WHITESPACE)
            if self.with_tail:
                self._parseTail(parser)
            return

        if token_id == TOKEN_ID_SYMBOL and value == '[':
            parser_read()
            parser_skip(TOKEN_ID_WHITESPACE)
            self.recurseInto(parser, ListNode())
            parser_skip(TOKEN_ID_WHITESPACE)
            parser_expect(TOKEN_ID_SYMBOL, ']')
            parser_skip(TOKEN_ID_WHITESPACE)
            if self.with_tail:
                self._parseTail(parser)
            return

        if token_id == TOKEN_ID_IDENTIFIER and value == 'not':
            parser_read()
            parser_skip(TOKEN_ID_WHITESPACE)
            self.recurseInto(parser, NotOperatorNode())
            parser_skip(TOKEN_ID_WHITESPACE)
            if self.with_tail:
                self._parseTail(parser)
            return

        self.child = self._parseValueWithFilter(parser)
        parser_skip(TOKEN_ID_WHITESPACE)
        if self.with_tail:
            self._parseTail(parser)

    def _parseValueWithFilter(self, parser):
        parser_read = parser.read
        parser_skip = parser.skip
        parser_isNext = parser.isNext

        # Start with the value, a context query or a string.
        value_node = self._parseValue(parser)

        # Now see if there are any filters.
        expr_root_node = value_node
        parser_skip(TOKEN_ID_WHITESPACE)
        while parser_isNext(TOKEN_ID_SYMBOL, '|'):
            parser_read()
            parser_skip(TOKEN_ID_WHITESPACE)

            flt_node = FilterNode()
            flt_node.add(expr_root_node)
            flt_node.parse(parser)
            expr_root_node = flt_node

            parser_skip(TOKEN_ID_WHITESPACE)

        return expr_root_node

    def _parseValue(self, parser):
        parser_readValue = parser.readValue
        parser_isNext = parser.isNext
        parser_peek = parser.peek

        # A context query, a string, a number, a list, a dictionary,
        # a tuple, or true/false.
        value_node = None
        if parser_isNext(TOKEN_ID_IDENTIFIER):
            _, _, idval = parser_peek()
            value_node = const_identifiers.get(idval)
            if value_node is None:
                value_node = ContextQueryNode()
                value_node.parse(parser)
            else:
                parser.read()
        elif (parser_isNext(TOKEN_ID_STRING_SINGLE_QUOTES) or
              parser_isNext(TOKEN_ID_STRING_DOUBLE_QUOTES)):
            value_node = StringNode(parser_readValue())
        elif parser_isNext(TOKEN_ID_FLOAT):
            value_node = FloatNode(float(parser_readValue()))
        elif parser_isNext(TOKEN_ID_INTEGER):
            value_node = IntegerNode(int(parser_readValue()))
        elif parser_isNext(TOKEN_ID_SYMBOL, '-'):
            parser_readValue()
            if parser_isNext(TOKEN_ID_FLOAT):
                value_node = FloatNode(-float(parser_readValue()))
            elif parser_isNext(TOKEN_ID_INTEGER):
                value_node = IntegerNode(-int(parser_readValue()))
            else:
                line_num, _, value = parser.peek()
                raise ParserError(line_num, "unexpected token '%s'." % value)
        else:
            line_num, _, value = parser_peek()
            raise ParserError(line_num, "unexpected token '%s'." % value)

        return value_node

    def _parseTail(self, parser):
        # See if the expression continue... in which case we wrap
        # our current child into a bigger expression.
        parser_read = parser.read
        parser_peek = parser.peek
        parser_skip = parser.skip

        child_op_prec = getattr(self.child, '__op_precedence__', None)
        child_is_binary_op = getattr(self.child, '__op_type__', 0) == 2

        line_num, token_id, value = parser_peek()
        if token_id == TOKEN_ID_IDENTIFIER:
            op_node_cls = misc_operator_nodes.get(value)
            if op_node_cls is not None:
                # Test or boolean operator.
                parser_read()
                parser_skip(TOKEN_ID_WHITESPACE)

                if op_node_cls.__op_type__ != 2:
                    raise Exception("Unexpected unary operator: %s" %
                                    op_node_cls)

                as_tail = False
                if child_is_binary_op:
                    as_tail = (
                        child_op_prec < op_node_cls.__op_precedence__)

                op_node = op_node_cls()
                if as_tail:
                    op_node.add(self.child.child2)
                    self.child.child2 = op_node
                    op_node.parse(parser)
                else:
                    op_node.add(self.child)
                    self.child = op_node
                    op_node.parse(parser)
                parser_skip(TOKEN_ID_WHITESPACE)
                self._parseTail(parser)
                return

        elif token_id == TOKEN_ID_SYMBOL:
            op_name = None
            # Binary operators are 1 or 2 characters... see if any operator
            # matches this first character.
            for k in binary_operator_nodes.keys():
                if k[0] == value:
                    op_name = value
                    break
            if op_name:
                # Yep, it matched. Now see if there's a 2nd character too.
                parser_read()
                _, token_id, value = parser_peek()
                if token_id == TOKEN_ID_SYMBOL:
                    # Try matching a 2-character operator. If nothing matches,
                    # go back to the one character operator.
                    #
                    # This can happen for instance with:
                    # {{ a /(2 + b) }}
                    #      ^^
                    #     2-chars!
                    #
                    if (op_name + value) in binary_operator_nodes:
                        op_name += value
                        parser_read()

                op_node_cls = binary_operator_nodes.get(op_name)
                if op_node_cls is not None:
                    # Binary operator.
                    parser_skip(TOKEN_ID_WHITESPACE)

                    as_tail = False
                    if child_is_binary_op:
                        as_tail = (
                            child_op_prec < op_node_cls.__op_precedence__)

                    op_node = op_node_cls()
                    if as_tail:
                        op_node.add(self.child.child2)
                        self.child.child2 = op_node
                        op_node.parse(parser)
                    else:
                        op_node.add(self.child)
                        self.child = op_node
                        op_node.parse(parser)
                    parser_skip(TOKEN_ID_WHITESPACE)
                    self._parseTail(parser)
                    return

                else:
                    # Raise an exception because at this point we can't
                    # give back what we consumed.
                    raise InvalidOperatorError(self.child, op_name)

    def render(self, ctx, data, out):
        return self.child.render(ctx, data, out)

    def compile(self, ctx, out):
        self.child.compile(ctx, out)


class ExpressionWrapperNode(ExpressionNode):
    def render(self, ctx, data, out):
        # This is where we make sure things are converted to strings for
        # rendering the output.
        val = self.child.render(ctx, data, out)
        out(ctx.engine.escape(val))

    def compile(self, ctx, out):
        self.child.compile(ctx, out)

        val = ctx.popvar()
        out.indent().write('out_write_escaped(%s)\n' % val)


class ContextQueryNode(MultiChildrenParserNode):
    TYPE_PROPERTY = 0
    TYPE_ARRAY_ITEM = 1
    TYPE_DICT_ITEM = 2
    TYPE_FUNC_CALL = 3

    def __init__(self, name=None):
        super().__init__()
        self.name = name
        self.query_type = ContextQueryNode.TYPE_PROPERTY
        self.array_item_query = None
        self.is_head = True
        self.has_tail = False
        self.force_cache_query = False

    def parse(self, parser):
        parser_expect = parser.expect
        parser_isNext = parser.isNext
        parser_skip = parser.skip
        parser_read = parser.read

        self.name = parser_expect(TOKEN_ID_IDENTIFIER)

        # See if we have either a dictionary access or a function call.
        if parser_isNext(TOKEN_ID_SYMBOL, '['):
            parser_read()
            parser_skip(TOKEN_ID_WHITESPACE)

            if parser_isNext(TOKEN_ID_INTEGER):
                # Index or full slice or first-half-slice (array[i:]).
                is_slice = False
                index1 = int(parser_read()[2])
                index2 = None
                parser_skip(TOKEN_ID_WHITESPACE)

                if parser_isNext(TOKEN_ID_SYMBOL, ':'):
                    parser_read()
                    parser_skip(TOKEN_ID_WHITESPACE)
                    is_slice = True
                    if parser_isNext(TOKEN_ID_INTEGER):
                        index2 = int(parser_read()[2])

                self.array_item_query = (is_slice, index1, index2)
                self.query_type = ContextQueryNode.TYPE_ARRAY_ITEM

            elif parser_isNext(TOKEN_ID_SYMBOL, ':'):
                # Second-half-slice (array[:i]).
                parser_read()
                parser_skip(TOKEN_ID_WHITESPACE)
                index2 = parser_expect(TOKEN_ID_INTEGER)
                self.array_item_query = (True, None, int(index2))
                self.query_type = ContextQueryNode.TYPE_ARRAY_ITEM

            else:
                self.recurseInto(parser, ExpressionNode())
                self.query_type = ContextQueryNode.TYPE_DICT_ITEM

            parser_skip(TOKEN_ID_WHITESPACE)
            parser_expect(TOKEN_ID_SYMBOL, ']')

        elif parser_isNext(TOKEN_ID_SYMBOL, '('):
            self.query_type = ContextQueryNode.TYPE_FUNC_CALL
            parser_read()
            parser_skip(TOKEN_ID_WHITESPACE)

            needs_comma = False
            while not parser_isNext(TOKEN_ID_SYMBOL, ')'):
                if needs_comma:
                    parser_skip(TOKEN_ID_WHITESPACE)
                    parser_expect(TOKEN_ID_SYMBOL, ',')
                    parser_skip(TOKEN_ID_WHITESPACE)
                self.recurseInto(parser, ExpressionNode())
                needs_comma = True

            parser_expect(TOKEN_ID_SYMBOL, ')')

        # See if the context query continues.
        if parser_isNext(TOKEN_ID_SYMBOL, '.'):
            parser_read()
            self.has_tail = True
            tail = ContextQueryNode()
            tail.is_head = False
            self.recurseInto(parser, tail)

    def render(self, ctx, data, out):
        children = self.children
        if self.has_tail:
            children = self.children[:-1]

        if self.is_head:
            val = ctx.queryRoot(data, self.name)
        else:
            val = ctx.query(data, self.name)

        if self.query_type == ContextQueryNode.TYPE_ARRAY_ITEM:
            is_slice, index1, index2 = self.array_item_query
            if is_slice:
                valid_index1 = index1 is not None
                valid_index2 = index2 is not None
                if valid_index1 and valid_index2:
                    val = val[index1:index2]
                elif valid_index1:
                    val = val[index1:]
                elif valid_index2:
                    val = val[:index2]
                else:
                    raise Exception("Got slicing notation without indices!")
            else:
                val = val[index1]

        elif self.query_type == ContextQueryNode.TYPE_DICT_ITEM:
            key = children[0].render(ctx, data, out)
            val = val[key]

        elif self.query_type == ContextQueryNode.TYPE_FUNC_CALL:
            params = list(self._renderTheseChildren(children, ctx, data, out))
            if getattr(val, 'needs_context', False):
                val = val(ctx, data, out, *params)
            else:
                val = val(*params)

        elif self.query_type != ContextQueryNode.TYPE_PROPERTY:
            raise Exception("Unexpected query type: %s" % self.query_type)

        if self.has_tail:
            return self.children[-1].render(ctx, val, out)
        else:
            return val

    def _renderTheseChildren(self, children, ctx, data, out):
        for c in children:
            yield c.render(ctx, data, out)

    def compile(self, ctx, out):
        children = self.children
        if self.has_tail:
            children = self.children[:-1]

        data_name = 'data'
        if not self.is_head:
            data_name = ctx.popvar()

        if self.query_type == ContextQueryNode.TYPE_PROPERTY:
            val = self._cachedQueryVar(ctx, self.name)
            if val is None:
                val = self._newQuery(data_name, self.name)
                if self.force_cache_query:
                    cached_val = ctx.varname('cached_query')
                    out.indent().write('%s = %s\n' % (cached_val, val))
                    val = cached_val
                    ctx.cacheQuery(self.name, val)
            ctx.pushvar(val)

        elif self.query_type == ContextQueryNode.TYPE_ARRAY_ITEM:
            val = self._cachedQueryVar(ctx, self.name)
            if val is None:
                val = self._newQuery(data_name, self.name)
                if self.force_cache_query:
                    cached_val = ctx.varname('cached_query')
                    out.indent().write('%s = %s\n' % (cached_val, val))
                    val = cached_val
                    ctx.cacheQuery(self.name, val)

            is_slice, index1, index2 = self.array_item_query
            if is_slice:
                valid_index1 = index1 is not None
                valid_index2 = index2 is not None
                if valid_index1 and valid_index2:
                    expr = '%s[%s:%s]' % (val, index1, index2)
                elif valid_index1:
                    expr = '%s[%s:]' % (val, index1)
                elif valid_index2:
                    expr = '%s[:%s]' % (val, index2)
                else:
                    raise Exception("Got slicing notation without indices!")
            else:
                expr = '%s[%s]' % (val, index1)
            ctx.pushvar(expr)

        elif self.query_type == ContextQueryNode.TYPE_DICT_ITEM:
            dname = self._cachedQueryVar(ctx, self.name)
            if dname is None:
                dname = self._newQuery(data_name, self.name)
                if self.force_cache_query:
                    cached_dname = ctx.varname('cached_query')
                    out.indent().write('%s = %s\n' % (cached_dname, dname))
                    dname = cached_dname
                    ctx.cacheQuery(self.name, dname)

            children[0].compile(ctx, out)

            expr = '%s[%s]' % (dname, ctx.popvar())
            ctx.pushvar(expr)

        elif self.query_type == ContextQueryNode.TYPE_FUNC_CALL:
            fname = self._cachedQueryVar(ctx, self.name)
            if fname is None:
                fname = self._newQuery(data_name, self.name)
                if self.force_cache_query:
                    cached_fname = ctx.varname('cached_query')
                    out.indent().write('%s = %s\n' % (cached_fname, fname))
                    fname = cached_fname
                    ctx.cacheQuery(self.name, fname)

            param_names = []
            for c in children:
                c.compile(ctx, out)
                param_names.append(ctx.popvar())

            if param_names:
                val = ('ctx_invoke(data, out_write, %s, %s)' %
                       (fname, ', '.join(param_names)))
            else:
                val = 'ctx_invoke(data, out_write, %s)' % fname
            ctx.pushvar(val)

        else:
            raise Exception("Unexpected query type: %s" % self.query_type)

        if self.has_tail:
            self.children[-1].compile(ctx, out)

    def _cachedQueryVar(self, ctx, query):
        if self.is_head:
            return ctx.getCachedQuery(query)
        return None

    def _newQuery(self, dataname, query):
        if self.is_head:
            return 'ctx_queryRoot(%s, %s)' % (dataname, repr(query))
        else:
            return 'ctx_query(%s, %s)' % (dataname, repr(query))
