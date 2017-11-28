import math
import time
import hashlib
import email.utils
import strict_rfc3339
from markupsafe import Markup
from ..compiler import write_render_opt_aliases
from ..engine import SafeString
from ..ext import Extension, StatementNode
from ..lexer import (
    TOKEN_ID_IDENTIFIER, TOKEN_ID_STATEMENT_BEGIN,
    TOKEN_ID_STRING_SINGLE_QUOTES, TOKEN_ID_STRING_DOUBLE_QUOTES,
    TOKEN_ID_SYMBOL, TOKEN_ID_INTEGER, TOKEN_ID_FLOAT)
from ..parser import ParserError
from ..nodes.const import StringNode, FloatNode, IntegerNode


class CoreExtension(Extension):
    def getStatementNodes(self):
        return [
            IfStatementNode,
            ForStatementNode,
            SetStatementNode,
            IncludeStatementNode,
            ExtendsStatementNode,
            BlockStatementNode,
            MacroStatementNode,
            ImportStatementNode,
            AutoEscapeStatementNode,
            RawStatementNode
        ]

    def getGlobals(self):
        return {
            'now': get_now_date,
            'fail': raise_exception
        }

    def getFilters(self):
        return {
            'abs': abs,
            'capitalize': filter_capitalize,
            'center': filter_center,
            'escape': filter_escape,
            'safe': filter_safe,
            'keys': filter_get_dict_keys,
            'sort': filter_sort,
            'reverse': filter_reverse,
            'values': filter_get_dict_values,
            'join': filter_join,
            'wordcount': filter_get_word_count,
            'titlecase': filter_title_case,
            'uppercase': filter_upper_case,
            'lowercase': filter_lower_case,
            'md5': filter_make_md5,
            'xmldate': filter_make_xml_date,
            'emaildate': filter_make_email_date,
            'date': filter_make_date,
        }

    def getTests(self):
        return {
            'divisibleby': test_divisible_by
        }


def get_now_date():
    return time.time()


def raise_exception(msg):
    raise Exception(msg)


def filter_capitalize(val):
    return val[0].upper() + val[1:].lower()


def filter_center(val, width=80):
    l = len(val)
    if l > width:
        return val
    margin_left = math.floor((width - l) / 2.0)
    margin_right = math.ceil((width - l) / 2.0)
    return (' ' * margin_left) + val + (' ' * margin_right)


def filter_escape(val):
    return Markup(val)


def filter_safe(val):
    return SafeString(val)


def filter_get_dict_keys(value):
    if isinstance(value, list):
        return [i[0] for i in value]
    return value.keys()


def filter_sort(value, reverse=False):
    return sorted(value, reverse=reverse)


def filter_reverse(value):
    return reversed(value)


def filter_get_dict_values(value):
    if isinstance(value, list):
        return [i[1] for i in value]
    return value.values()


def filter_join(value, separator=' '):
    return separator.join([str(v) for v in value])


def filter_get_word_count(value):
    return len(value.split())


def filter_title_case(value):
    return value.title()


def filter_lower_case(value):
    return value.lower()


def filter_upper_case(value):
    return value.upper()


def filter_make_md5(value):
    return hashlib.md5(value.lower().encode('utf8')).hexdigest()


def filter_make_xml_date(value):
    """ Formats timestamps like 1985-04-12T23:20:50.52Z
    """
    if value == 'now':
        value = time.time()
    return strict_rfc3339.timestamp_to_rfc3339_localoffset(int(value))


def filter_make_email_date(value, localtime=False):
    """ Formats timestamps like Fri, 09 Nov 2001 01:08:47 -0000
    """
    if value == 'now':
        value = time.time()
    return email.utils.formatdate(value, localtime=localtime)


def filter_make_date(value, fmt):
    if value == 'now':
        value = time.time()
    return time.strftime(fmt, time.localtime(value))


def test_divisible_by(value, div):
    return (value % div) == 0


class IfStatementNode(StatementNode):
    name = 'if'

    def parse(self, parser):
        parser.parseExpression(self)
        parser.skipWhitespace()
        parser.expectStatementEnd()
        parser.parseUntilStatement(self, ['else', 'endif'])

        has_else = False
        val = parser.peekValue()
        if val == 'else':
            parser.expectIdentifier('else')
            parser.skipWhitespace()
            parser.expectStatementEnd()
            parser.parseUntilStatement(self, 'endif')
            val = parser.peekValue()
            has_else = True

        parser.expectIdentifier('endif')

        assert len(self.children) == (3 if has_else else 2)

    def render(self, ctx, data, out):
        expr_value = self.children[0].render(ctx, data, out)
        if expr_value:
            return self.children[1].render(ctx, data, out)
        else:
            if len(self.children) > 2:
                return self.children[2].render(ctx, data, out)
            return None

    def compile(self, ctx, out):
        self.children[0].compile(ctx, out)
        expr_value = ctx.popvar()
        out.indent().write('if %s:\n' % expr_value)

        ctx.startScope()
        out.push(False)
        self.children[1].compile(ctx, out)
        out.pull()
        ctx.endScope()

        if len(self.children) > 2:
            out.indent().write('else:\n')
            ctx.startScope()
            out.push(False)
            self.children[2].compile(ctx, out)
            out.pull()
            ctx.endScope()


class ForStatementNode(StatementNode):
    name = 'for'
    compiler_imports = ['from inukshuk.ext.core import ForStatementNode']

    class _LoopVar:
        def __init__(self, seq):
            self.seq = seq
            self.length = -1
            if hasattr(seq, '__len__'):
                self.length = len(seq)

            self.index = 1
            self.index0 = 0
            self.revindex = -1
            self.revindex0 = -1
            self.first = True
            self.last = False

        def setIndex0(self, idx):
            self.index = idx + 1
            self.index0 = idx
            self.first = (idx == 0)
            length = self.length
            if length >= 0:
                self.revindex = length - idx
                self.revindex0 = length - idx - 1
                self.last = (idx == length - 1)

        def cycle(self, *args):
            index = self.index0 % len(args)
            return args[index]

    def __init__(self):
        super().__init__()
        self.it_name = None

    def parse(self, parser):
        self.it_name = parser.expectIdentifier()
        parser.skipWhitespace()
        parser.expectIdentifier('in')
        parser.skipWhitespace()
        parser.parseExpression(self)
        parser.skipWhitespace()

        if parser.isNext(TOKEN_ID_IDENTIFIER, 'if'):
            parser.read()
            parser.skipWhitespace()
            parser.parseExpression(self)
            parser.skipWhitespace()

        parser.expectStatementEnd()

        parser.parseUntilStatement(self, ['endfor'])
        parser.expectIdentifier('endfor')

        assert len(self.children) == 2 or len(self.children) == 3

    def render(self, ctx, data, out):
        has_condition = len(self.children) == 3
        body_index = 2 if has_condition else 1

        iterand = self.children[0].render(ctx, data, out)
        loop = ForStatementNode._LoopVar(iterand)
        ctx.pushLocalVariable(self.it_name, None)
        ctx.pushLocalVariable('loop', loop)
        for index, item in enumerate(iterand):
            ctx.locals[self.it_name] = item
            loop.setIndex0(index)
            if has_condition:
                cond = self.children[1].render(ctx, data, out)
                if not cond:
                    continue
            self.children[body_index].render(ctx, data, out)
        ctx.popLocalVariable(self.it_name)
        ctx.popLocalVariable('loop')

    def compile(self, ctx, out):
        self.children[0].compile(ctx, out)
        iterand = ctx.popvar()

        loop = ctx.varname('loop')
        index = ctx.varname('index')
        item = ctx.varname('item')
        ctx.cacheQuery(self.it_name, item)
        ctx.cacheQuery('loop', loop)

        out.indent().write('%s = ForStatementNode._LoopVar(%s)\n' %
                           (loop, iterand))
        out.indent().writePushLocalVariable(self.it_name, 'None')
        out.indent().writePushLocalVariable('loop', loop)
        out.indent().write('set_%s_index0 = %s.setIndex0\n' % (loop, loop))
        out.indent().write('for %s, %s in enumerate(%s.seq):\n' %
                           (index, item, loop))

        ctx.startScope()
        out.push(False)
        out.indent().writeSetLocalVariable(self.it_name, item)
        out.indent().write('set_%s_index0(%s)\n' % (loop, index))

        has_condition = len(self.children) == 3
        if has_condition:
            self.children[1].compile(ctx, out)
            out.indent().write('if %s:\n' % ctx.popvar())
            out.push(False)
            self.children[2].compile(ctx, out)
            out.pull()
        else:
            self.children[1].compile(ctx, out)

        out.pull()
        ctx.endScope()

        out.indent().writePopLocalVariable(self.it_name)
        out.indent().writePopLocalVariable("loop")
        ctx.uncacheQuery(self.it_name)
        ctx.uncacheQuery('loop')


class SetStatementNode(StatementNode):
    name = 'set'

    def __init__(self):
        super().__init__()
        self.var_name = None

    def parse(self, parser):
        self.var_name = parser.expectIdentifier()
        parser.skipWhitespace()
        parser.expectSymbol('=')
        parser.skipWhitespace()
        parser.parseExpression(self)

    def render(self, ctx, data, out):
        value = self.children[0].render(ctx, data, out)
        ctx.pushLocalVariable(self.var_name, value)

    def compile(self, ctx, out):
        self.children[0].compile(ctx, out)
        value = ctx.popvar()
        out.indent().writePushLocalVariable(self.var_name, value)


class IncludeStatementNode(StatementNode):
    name = 'include'

    def __init__(self):
        super().__init__()
        self.include_name = None
        self._pre_loaded_name = None

    def parse(self, parser):
        self.include_name = parser.expectAny(
            (TOKEN_ID_STRING_SINGLE_QUOTES, TOKEN_ID_STRING_DOUBLE_QUOTES))

    def render(self, ctx, data, out):
        t = ctx.engine.getTemplate(self.include_name)
        t._renderWithContext(ctx, data, out)

    def compile(self, ctx, out):
        if self._pre_loaded_name:
            out.indent().write('%s(ctx, data, out_write)\n' %
                               self._pre_loaded_name)
        else:
            tpl_var = ctx.varname('tpl')
            out.indent().write('%s = ctx_engine.getTemplate(%s)\n' %
                               (tpl_var, repr(self.include_name)))
            out.indent().write('%s._compileContent(True)\n' % tpl_var)
            mod_var = ctx.varname('tpl_mod')
            out.indent().write(
                '%s = importlib.import_module(%s._compiled_module_name)\n' %
                (mod_var, tpl_var))
            mod_rdr_func = ctx.varname('tpl_rdr_func')
            out.indent().write('%s = getattr(%s, "render_template")\n' %
                               (mod_rdr_func, mod_var))
            out.indent().write('%s(ctx, data, out_write)\n' % mod_rdr_func)


class BlockStatementNode(StatementNode):
    name = 'block'

    def __init__(self, is_child_block=False):
        super().__init__()
        self.block_name = None
        self.is_child_block = is_child_block

    def parse(self, parser):
        self.block_name = parser.expectIdentifier()
        parser.skipWhitespace()
        parser.expectStatementEnd()

        parser.parseUntilStatement(self, ['endblock'])
        parser.expectIdentifier('endblock')

    def render(self, ctx, data, out):
        # Use either the override block node, or ourselves.
        udkey = 'block:%s' % self.block_name
        block_node = ctx.user_data.get(udkey, self)
        for c in block_node.children:
            c.render(ctx, data, out)

    def compile(self, ctx, out):
        bf = ctx.varname('bf')
        udkey = 'block:%s' % self.block_name
        func_name = 'render_block_%s' % self.block_name
        out.indent().write('%s = ctx.user_data.get(%s, %s)\n' %
                           (bf, repr(udkey), func_name))
        out.indent().write('%s(ctx, data, out_write)\n' % bf)

        out.addPostCompiler(self._postCompile)

    def _postCompile(self, ctx, out):
        ctx.startScope()
        func_name = 'render_block_%s' % self.block_name
        out.write('def %s(ctx, data, out_write):\n' % func_name)
        out.push(False)
        write_render_opt_aliases(out)
        for c in self.children:
            c.compile(ctx, out)
        out.pull()
        ctx.endScope()


class ExtendsStatementNode(StatementNode):
    name = 'extends'
    own_close = True
    compiler_imports = ['import importlib']

    def __init__(self):
        super().__init__()
        self.parent_name = None

    def parse(self, parser):
        self.parent_name = parser.expectAny(
            (TOKEN_ID_STRING_SINGLE_QUOTES, TOKEN_ID_STRING_DOUBLE_QUOTES))
        parser.skipWhitespace()
        parser.expectStatementEnd()

        while True:
            if not self._parseToNextBlock(parser):
                return
            self.recurseInto(parser, BlockStatementNode(is_child_block=True))
            parser.skipWhitespace()
            parser.expectStatementEnd()

    def _parseToNextBlock(self, parser):
        while True:
            tok = (None, None, None)
            while tok is not None and tok[1] != TOKEN_ID_STATEMENT_BEGIN:
                tok = parser.read()
            parser.skipWhitespace()
            tok = parser.peek()
            if (tok is not None and tok[1] == TOKEN_ID_IDENTIFIER and
                    tok[2] == 'block'):
                parser.read()
                parser.skipWhitespace()
                return True
            if tok is None:
                return False

    def render(self, ctx, data, out):
        added_user_data = []
        for c in self.children:
            udkey = 'block:%s' % c.block_name
            added_user_data.append(udkey)
            ctx.user_data[udkey] = c

        t = ctx.engine.getTemplate(self.parent_name)
        t._renderWithContext(ctx, data, out)

        for udkey in added_user_data:
            del ctx.user_data[udkey]

    def compile(self, ctx, out):
        block_names = [c.block_name for c in self.children]

        for n in block_names:
            udkey = 'block:%s' % n
            bf = 'render_block_%s' % n
            out.indent().write('ctx.user_data[%s] = %s\n' %
                               (repr(udkey), bf))

        tpl_var = ctx.varname('tpl')
        out.indent().write('%s = ctx_engine.getTemplate(%s)\n' %
                           (tpl_var, repr(self.parent_name)))
        out.indent().write('%s._compileContent(True)\n' % tpl_var)
        mod_var = ctx.varname('tpl_mod')
        out.indent().write(
            '%s = importlib.import_module(%s._compiled_module_name)\n' %
            (mod_var, tpl_var))
        mod_rdr_func = ctx.varname('tpl_rdr_func')
        out.indent().write('%s = getattr(%s, "render_template")\n' %
                           (mod_rdr_func, mod_var))
        out.indent().write('%s(ctx, data, out_write)\n' % mod_rdr_func)

        for n in block_names:
            udkey = 'block:%s' % n
            out.indent().write('del ctx.user_data[%s]\n' % repr(udkey))

        for c in self.children:
            out.addPostCompiler(c._postCompile)


class MacroStatementNode(StatementNode):
    name = 'macro'
    compiler_imports = ['from inukshuk.rendering import needs_context']

    def __init__(self):
        super().__init__()
        self.macro_name = None
        self.parameters = []

    def parse(self, parser):
        self.macro_name = parser.expectIdentifier()

        has_kwargs = False
        parser.expectSymbol('(')
        parser.skipWhitespace()

        while not parser.isNext(TOKEN_ID_SYMBOL, ')'):
            if len(self.parameters) > 0:
                parser.expectSymbol(',')

            parser.skipWhitespace()
            pn = parser.expectIdentifier()

            parser.skipWhitespace()
            if parser.isNext(TOKEN_ID_SYMBOL, '='):
                parser.read()
                parser.skipWhitespace()

                if (parser.isNext(TOKEN_ID_STRING_SINGLE_QUOTES) or
                        parser.isNext(TOKEN_ID_STRING_DOUBLE_QUOTES)):
                    param_val = StringNode(parser.readValue())
                elif parser.isNext(TOKEN_ID_FLOAT):
                    param_val = FloatNode(float(parser.readValue()))
                elif parser.isNext(TOKEN_ID_INTEGER):
                    param_val = IntegerNode(int(parser.readValue()))
                else:
                    raise ParserError(
                        parser.line_num,
                        "parameter '%s' must have a default value that's "
                        "a constant expression (string, int, or float)." %
                        pn)

                self.parameters.append((pn, param_val))
                parser.skipWhitespace()
                has_kwargs = True
            elif has_kwargs:
                raise ParserError(
                    parser.line_num,
                    "parameter '%s' must have a default value because "
                    "previous parameters have a default value." % pn)
            else:
                self.parameters.append((pn, None))

        parser.expectSymbol(')')
        parser.skipWhitespace()
        parser.expectStatementEnd()

        parser.parseUntilStatement(self, ['endmacro'])
        parser.expectIdentifier('endmacro')

    def render(self, ctx, data, out):
        def _callMacro(*args, **kwargs):
            params = list(self.parameters)
            pushed_vars = []

            # Push argument values.
            for i, a in enumerate(args):
                try:
                    pn, _ = params[i]
                except IndexError as ex:
                    raise Exception("Macro '%s' has %d arguments, but was "
                                    "given %d: %s" %
                                    (self.macro_name, len(self.parameters),
                                     len(args), args)) from ex
                ctx.pushLocalVariable(pn, a)
                pushed_vars.append(pn)
            params = params[len(args):]

            # Push keyword argument values.
            for kn, kv in kwargs.items():
                for i, p in params:
                    if p[0] == kn:
                        # Found it, there is such a keyword argument.
                        ctx.pushLocalVariable(kn, kv)
                        pushed_vars.append(kn)
                        params.pop(i)
                        break
                else:
                    # Didn't find it...
                    raise Exception("No argument '%s' in macro '%s'." %
                                    (kn, self.macro_name))

            # Push default (unspecified) argument values.
            for pn, pv_node in params:
                pv = pv_node.render(ctx, data, out)
                ctx.pushLocalVariable(pn, pv)
                pushed_vars.append(pn)

            # Render!
            for c in self.children:
                c.render(ctx, data, out)

            # Cleanup
            for pv in pushed_vars:
                ctx.popLocalVariable(pv)

        ctx.pushLocalVariable(self.macro_name, _callMacro)

    def compile(self, ctx, out):
        func_name = 'render_macro_%s' % self.macro_name
        out.addPostCompiler(self._postCompile)
        out.indent().writePushLocalVariable(self.macro_name, func_name)

    def _postCompile(self, ctx, out):
        ctx.startScope()
        out.write('@needs_context\n')
        out.write('def render_macro_%s(ctx, data, out_write' % self.macro_name)
        for pn, pv in self.parameters:
            out.write(', ')
            out.write(pn)
            if pv is not None:
                out.write('=')
                pv.compile(ctx, out)
                out.write(ctx.popvar())
        out.write('):\n')
        out.push(False)
        write_render_opt_aliases(out)

        for n, _ in self.parameters:
            out.indent().writePushLocalVariable(n, n)
        out.indent().write('\n')

        for c in self.children:
            c.compile(ctx, out)

        out.indent().write('\n')
        for n, _ in self.parameters:
            out.indent().writePopLocalVariable(n)

        out.pull()
        ctx.endScope()


class ImportStatementNode(StatementNode):
    name = 'import'

    def __init__(self):
        super().__init__()
        self.import_name = None
        self.alias = None

    def parse(self, parser):
        self.import_name = parser.expectAny(
            (TOKEN_ID_STRING_SINGLE_QUOTES, TOKEN_ID_STRING_DOUBLE_QUOTES))
        parser.skipWhitespace()
        parser.expectIdentifier('as')
        parser.skipWhitespace()
        self.alias = parser.expectIdentifier()

    def render(self, ctx, data, out):
        t = ctx.engine.getTemplate(self.import_name)
        child_ctx = ctx.createChildContext()
        t._renderWithContext(child_ctx, data, out)
        ctx.mergeChildContext(child_ctx, endpoint=self.alias)

    def compile(self, ctx, out):
        tpl_var = ctx.varname('tpl')
        out.indent().write('%s = ctx_engine.getTemplate(%s)\n' %
                           (tpl_var, repr(self.import_name)))
        out.indent().write('%s._compileContent(True)\n' % tpl_var)
        mod_var = ctx.varname('tpl_mod')
        out.indent().write(
            '%s = importlib.import_module(%s._compiled_module_name)\n' %
            (mod_var, tpl_var))
        mod_rdr_func = ctx.varname('tpl_rdr_func')
        out.indent().write('%s = getattr(%s, "render_template")\n' %
                           (mod_rdr_func, mod_var))

        child_ctx_var = ctx.varname('child_ctx')
        out.indent().write('%s = ctx.createChildContext()\n' %
                           child_ctx_var)
        out.indent().write('%s(%s, data, out_write)\n' %
                           (mod_rdr_func, child_ctx_var))
        out.indent().write('ctx.mergeChildContext(%s, endpoint=%s)\n' %
                           (child_ctx_var, repr(self.alias)))


class AutoEscapeStatementNode(StatementNode):
    name = 'autoescape'

    def __init__(self):
        super().__init__()
        self._previous = None
        self._value = None

    def parse(self, parser):
        val = parser.expectIdentifier()
        self._value = (val.lower() == 'true')
        parser.skipWhitespace()
        parser.expectStatementEnd()

        parser.parseUntilStatement(self, ['endautoescape'])
        parser.expectIdentifier('endautoescape')

    def render(self, ctx, data, out):
        self._previous = ctx.engine.autoescape
        ctx.engine.autoescape = self._value
        try:
            for c in self.children:
                c.render(ctx, data, out)
        finally:
            ctx.engine.autoescape = self._previous

    def compile(self, ctx, out):
        prev = ctx.varname('prev')
        out.indent().write('%s = out_write_escaped\n' % prev)
        out.indent().write('out_write_escaped = '
                           'ctx_engine._getWriteEscapeFunc(out_write, %s)\n' %
                           repr(self._value))
        for c in self.children:
            c.compile(ctx, out)
        out.indent().write('out_write_escaped = %s\n' % prev)


class RawStatementNode(StatementNode):
    name = 'raw'

    def __init__(self):
        super().__init__()
        self.text = None

    def parse(self, parser):
        parser.skipWhitespace()
        parser.expectStatementEnd()
        inner = []
        while True:
            token = parser.read()
            if token is None:
                raise ParserError(parser.line_num,
                                  "unexpected EOF while looking for `endraw`.")
            _, tid, val = token
            if tid == TOKEN_ID_STATEMENT_BEGIN:
                parser.skipWhitespace()
                if parser.isNext(TOKEN_ID_IDENTIFIER, 'endraw'):
                    parser.read()
                    break

            if tid == TOKEN_ID_STRING_SINGLE_QUOTES:
                inner.append("'%s'" % val)
            elif tid == TOKEN_ID_STRING_DOUBLE_QUOTES:
                inner.append('"%s"' % val)
            else:
                inner.append(val)
        self.text = ''.join(inner)

    def render(self, ctx, data, out):
        out(self.text)

    def compile(self, ctx, out):
        out.indent().write('out_write(%s)\n' % repr(self.text))
