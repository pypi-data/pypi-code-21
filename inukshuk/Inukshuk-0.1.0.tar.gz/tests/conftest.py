import os.path
import re
import pprint
import itertools
import traceback
import collections
import pytest
import yaml
from yaml.constructor import ConstructorError
from inukshuk import compiler, engine, lexer, loader, nodes, parser
from inukshuk.ext import core, Extension, StatementNode

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


def pytest_collect_file(parent, path):
    if path.ext == '.yaml' and path.basename.startswith("test"):
        return InukshukTestFile(path, parent)
    return None


class InukshukTestFile(pytest.File):
    def collect(self):
        test_type = 'template'
        needs_engine = False
        spec = yaml.load_all(
            self.fspath.open(encoding='utf8'),
            Loader=InukshukSpecLoader)
        for i, item in enumerate(spec):
            if i == 0 and 'test_type' in item:
                test_type = item.get('test_type')
                needs_engine = item.get('needs_engine', False)
                continue

            name = '%s_%d' % (self.fspath.basename, i)
            if 'test_name' in item:
                name += '_%s' % item['test_name']
            item['test_type'] = test_type
            item['needs_engine'] = needs_engine
            yield InukshukTestItem(name, self, item)


class InukshukTestItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent)
        self.spec = spec

    def runtest(self):
        test_type = self.spec.get('test_type')
        if test_type == 'lexer':
            self._runLexerTest()
        elif test_type == 'parser':
            self._runParserTest()
        elif test_type == 'template':
            self._runTemplateTest(False)
            self._runTemplateTest(True)
        else:
            raise Exception("Unknown test type: %s" % test_type)

    def reportinfo(self):
        return self.fspath, 0, "template test: %s" % self.name

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, ExpectedParserNodeTreeError):
            return ('\n'.join(
                ['Unexpected parser node tree.'] +
                ['', 'Actual tree:'] +
                list(print_nodes(excinfo.value.args[0])) +
                ['', 'Expected tree:'] +
                list(print_nodes(excinfo.value.args[1]))))
        elif isinstance(excinfo.value, ParserErrorWithContext):
            ex = excinfo.value
            l = lexer.Lexer()
            tokens = list(l.tokenize(excinfo.value.text))
            return ('\n'.join(
                ['Parser error raised:'] +
                traceback.format_exception(type(ex), ex, ex.__traceback__) +
                ['',
                 'Lexical tokens:'] +
                [', '.join(repr_tokens(tokens))]))
        elif isinstance(excinfo.value, SyntaxErrorWithContext):
            bad_code = [str(type(excinfo.value.inner))]
            if isinstance(excinfo.value.inner, compiler.InMemorySyntaxError):
                bad_code += ['', 'Generated code:', '']
                bad_code += ['%d %s' % (num, line)
                             for num, line
                             in zip(
                                 itertools.count(1),
                                 excinfo.value.inner.source_code.split('\n'))]
            return ('\n'.join(
                ['Syntax error raised on generated template:',
                 str(excinfo.value)] +
                bad_code))
        elif isinstance(excinfo.value, ErrorWithContext):
            ex = excinfo.value.inner
            fmt_ex = traceback.format_exception(
                type(ex), ex, ex.__traceback__)
            if not excinfo.value.tpl._compiled:
                return ('\n'.join(fmt_ex))

            c = compiler.Compiler(excinfo.value.tpl._engine)
            try:
                bad_code = c.getCompileUnit(excinfo.value.tpl._root_node)
            except Exception as e:
                bad_code = ("CAN'T GET COMPILED CODE:\n" +
                            str(e))
            return ('\n'.join(
                fmt_ex +
                ['', 'Generated code:', ''] +
                ['%d %s' % (num, line)
                 for num, line in zip(
                         itertools.count(1), bad_code.split('\n'))]))

        return super().repr_failure(excinfo)

    def _runLexerTest(self):
        intext = self.spec.get('in')
        expected = self.spec.get('out')
        if intext is None or expected is None:
            raise Exception("No 'in' or 'out' specified.")

        l = lexer.Lexer()
        actual = l.tokenize(intext)
        assert list(actual) == list(make_tokens(expected))

    def _runParserTest(self):
        intext = self.spec.get('in')
        expected = self.spec.get('out')
        if intext is None or expected is None:
            raise Exception("No 'in' or 'out' specified.")

        expected_nodes = make_parser_nodes(expected)

        l = lexer.Lexer()
        p = parser.Parser()
        if self.spec.get('needs_engine', False):
            from inukshuk.engine import Engine
            p.engine = Engine()
            p.engine.extensions.append(TestExtension())

        actual = p.parse(l.tokenize(intext))
        assert_parser_node_tree_are_equal(actual, expected_nodes)

    def _runTemplateTest(self, compiled):
        intext = self.spec.get('in')
        expected = self.spec.get('out')
        if intext is None or expected is None:
            raise Exception("No 'in' or 'out' specified.")

        cache_dir = None
        if compiled:
            cache_dir = os.path.join(os.path.dirname(__file__),
                                     '__inukcache__')

        data = self.spec.get('data')
        others = self.spec.get('others')
        autoescape = self.spec.get('autoescape', False)

        tpl_root_name = '__%s_root__' % self.name
        ldr_root = loader.StringsLoader({tpl_root_name: intext})
        ldr_others = loader.StringsLoader(others)
        ldr = loader.CompositeLoader([ldr_root, ldr_others])
        eng = engine.Engine(loader=ldr,
                            autoescape=autoescape,
                            compile_cache_dir=cache_dir)
        eng.extensions.append(TestExtension())

        tpl = eng.getTemplate(tpl_root_name, compiled=compiled)
        try:
            actual = tpl.render(data)
        except parser.ParserError as e:
            raise ParserErrorWithContext(e, intext)
        except (compiler.InMemorySyntaxError, SyntaxError) as e:
            raise SyntaxErrorWithContext(e, tpl)
        except Exception as e:
            raise ErrorWithContext(e, tpl)

        try:
            assert actual == expected
        except:
            print("Parser Nodes:")
            for n in print_nodes(tpl._root_node):
                print(n)

            if compiled:
                print("")
                print("Generated code:")
                print("")

                _print_template_code(tpl)
                print("")
                _print_templates_code(eng)
            else:
                print("")
                print("Using direct rendering.")
            raise


def _print_templates_code(engine):
    for name, tpl in engine._cache.items():
        print("Template '%s':" % name)
        print("")
        _print_template_code(tpl)


def _print_template_code(tpl):
    c = compiler.Compiler(tpl._engine)
    bad_code = c.getCompileUnit(tpl._root_node)
    for i, l in enumerate(bad_code.split('\n')):
        print("%d %s" % (i, l))


class InukshukSpecLoader(SafeLoader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_constructor('tag:yaml.org,2002:map',
                             type(self).construct_yaml_map)
        self.add_constructor('tag:yaml.org,2002:omap',
                             type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = collections.OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if not isinstance(node, yaml.MappingNode):
            raise ConstructorError(
                None, None,
                "expected a mapping node, but found %s" % node.id,
                node.start_mark)
        mapping = collections.OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, collections.Hashable):
                raise ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    "found unhashable key", key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


class FooStatementNode(StatementNode):
    name = 'foo'

    def parse(self, parser):
        parser.skipWhitespace()

    def render(self, ctx, data):
        yield 'FOO'


def filter_foo(val):
    return 'FOO' + val + 'FOO'


def filter_foo3(val, one, two='SUPER', three='AWESOME'):
    return 'THIS %s %s IS %s %s' % (one, val, two, three)


def test_foo(val, case_sensitive=True):
    if not case_sensitive:
        val = val.lower()
    return val.startswith('foo')


class TestExtension(Extension):
    def getFilters(self):
        return {'filterfoo': filter_foo,
                'filterfoo3': filter_foo3}

    def getTests(self):
        return {'testfoo': test_foo}

    def getStatementNodes(self):
        return [FooStatementNode]


def repr_tokens(tokens):
    for _, tid, value in tokens:
        out = str(value)
        yield out


def make_tokens(items):
    line_num = 1
    for i in items:
        t = make_token(i, line_num)
        line_num = t[0]
        yield t


re_token_desc = re.compile('(?P<type>[a-z]+)\:')


token_types = {
    'id': lexer.TOKEN_ID_IDENTIFIER,
    'ws': lexer.TOKEN_ID_WHITESPACE,
    's': lexer.TOKEN_ID_SYMBOL,
    'str': lexer.TOKEN_ID_STRING_SINGLE_QUOTES
}


def make_token(item, line_num):
    if isinstance(item, int):
        return (line_num, lexer.TOKEN_ID_INTEGER, str(item))
    if isinstance(item, float):
        return (line_num, lexer.TOKEN_ID_FLOAT, str(item))
    if isinstance(item, str):
        if item == '{{':
            return (line_num, lexer.TOKEN_ID_EXPRESSION_BEGIN, '{{')
        elif item == '}}':
            return (line_num, lexer.TOKEN_ID_EXPRESSION_END, '}}')
        elif item == '{%':
            return (line_num, lexer.TOKEN_ID_STATEMENT_BEGIN, '{%')
        elif item == '{%-':
            return (line_num, lexer.TOKEN_ID_STATEMENT_BEGIN, '{%-')
        elif item == '{%+':
            return (line_num, lexer.TOKEN_ID_STATEMENT_BEGIN, '{%+')
        elif item == '%}':
            return (line_num, lexer.TOKEN_ID_STATEMENT_END, '%}')
        elif item == '-%}':
            return (line_num, lexer.TOKEN_ID_STATEMENT_END, '-%}')
        elif item == '+%}':
            return (line_num, lexer.TOKEN_ID_STATEMENT_END, '+%}')
        elif item.startswith('{##}'):
            return (line_num, lexer.TOKEN_ID_COMMENT, item[4:])

        m = re_token_desc.match(item)
        if m:
            t = m.group('type')
            tid = token_types.get(t)
            if tid is not None:
                return (line_num, tid, item[m.end():])

        line_num += item.count("\n")
        return (line_num, lexer.TOKEN_ID_TEXT, item)
    raise Exception()


node_types = {
    'text': nodes.text.TextNode,
    'stw': nodes.wrapper.StatementWrapperNode,
    'stb': nodes.wrapper.StatementBodyNode,
    'stif': core.IfStatementNode,
    'stfor': core.ForStatementNode,
    'stfoo': FooStatementNode,
    'exprw': nodes.expression.ExpressionWrapperNode,
    'expr': nodes.expression.ExpressionNode,
    'query': nodes.expression.ContextQueryNode,
    'filter': nodes.filters.FilterNode,
    'test': nodes.tests.TestNode,
    'int': nodes.const.IntegerNode,
    'float': nodes.const.FloatNode,
    'string': nodes.const.StringNode,
    'not': nodes.operators.NotOperatorNode,
    'and': nodes.operators.AndBooleanNode,
    'or': nodes.operators.OrBooleanNode,
    'add': nodes.operators.AddOperatorNode,
    'sub': nodes.operators.SubtractOperatorNode,
    'div': nodes.operators.DivideOperatorNode,
    'divint': nodes.operators.DivideIntegerOperatorNode,
    'mod': nodes.operators.ModuloOperatorNode,
    'mult': nodes.operators.MultiplyOperatorNode,
    'pow': nodes.operators.PowerOperatorNode,
    'eq': nodes.operators.EqualOperatorNode,
    'neq': nodes.operators.InequalOperatorNode,
    'gt': nodes.operators.GreaterOperatorNode,
    'gte': nodes.operators.GreaterOrEqualOperatorNode,
    'lt': nodes.operators.LessOperatorNode,
    'lte': nodes.operators.LessOrEqualOperatorNode,
}


def _make_context_query_node(t, v):
    n = nodes.expression.ContextQueryNode()
    bits = v.split(',')
    n.name = bits[0]
    if len(bits) > 1:
        query_types = {
            '': nodes.expression.ContextQueryNode.TYPE_PROPERTY,
            'dict': nodes.expression.ContextQueryNode.TYPE_DICT_ITEM,
            'func': nodes.expression.ContextQueryNode.TYPE_FUNC_CALL}
        n.query_type = query_types.get(bits[1])
    if len(bits) > 2 and bits[2] == 't':
        n.has_tail = True
    return n


def _make_filter_node(t, v):
    n = nodes.filters.FilterNode()
    assert isinstance(v, str) and v
    n.func_name = v
    return n


def _make_test_node(t, v):
    n = nodes.tests.TestNode()
    assert isinstance(v, str) and v
    n.func_name = v
    return n


def _make_statement_body_node(t, v):
    n = nodes.wrapper.StatementBodyNode(v)
    return n


nodes.base.LeafParserNode.__test_factory__ = lambda t, v: t(v)
nodes.expression.ContextQueryNode.__test_factory__ = _make_context_query_node
nodes.filters.FilterNode.__test_factory__ = _make_filter_node
nodes.tests.TestNode.__test_factory__ = _make_test_node
nodes.wrapper.StatementBodyNode.__test_factory__ = _make_statement_body_node

nodes.base.LeafParserNode.__test_compare__ = ['value']
nodes.filters.FilterNode.__test_compare__ = ['func_name']
nodes.tests.TestNode.__test_compare__ = ['func_name']
nodes.wrapper.StatementBodyNode.__test_compare__ = ['stop_on_statement']
nodes.expression.ContextQueryNode.__test_compare__ = ['name', 'query_type',
                                                      'has_tail']


class ExpectedParserNodeTreeError(Exception):
    def __init__(self, actual, expected):
        super().__init__(actual, expected)


class ParserErrorWithContext(Exception):
    def __init__(self, inner, text):
        super().__init__(str(inner))
        self.text = text


class SyntaxErrorWithContext(Exception):
    def __init__(self, inner, tpl):
        super().__init__(str(inner))
        self.inner = inner
        self.tpl = tpl


class ErrorWithContext(Exception):
    def __init__(self, inner, tpl):
        super().__init__(str(inner))
        self.inner = inner
        self.tpl = tpl


def _default_test_factory(t, v):
    return t()


def make_parser_nodes(spec):
    root = nodes.wrapper.TemplateNode()
    _make_parser_nodes_recursive(spec, root)
    return root


num_suffix = re.compile('\d+$')


def _make_parser_nodes_recursive(spec, parent_node):
    for k, v in spec.items():
        if k == '_val':
            continue

        m = num_suffix.search(k)
        if m:
            k = k[:m.start()]

        node_type = node_types.get(k)
        if node_type is None:
            raise Exception("Unknown parser node spec: %s" % k)

        factory = getattr(node_type, '__test_factory__', None)
        if factory is None:
            factory = _default_test_factory

        node_value = v
        if isinstance(v, dict):
            node_value = v.get('_val', None)

        node = factory(node_type, node_value)
        parent_node.add(node)

        if isinstance(v, dict):
            _make_parser_nodes_recursive(v, node)


def print_nodes(root, level=0):
    root_dict = root.__dict__.copy()
    root_dict.pop('children', None)  # Usual list of children nodes.
    root_dict.pop('kw_children', None)
    for k in list(root_dict.keys()):
        if isinstance(root_dict[k], nodes.base.ParserNode):
            root_dict.pop(k)

    try:
        root_dict.pop('__test_difference_start__')
        diff_str = 'DIFFERENCE STARTS HERE'
    except KeyError:
        diff_str = ''

    indent = ' ' * level
    yield ('%s%s  %s %s' % (indent, root.__class__.__name__,
                            pprint.pformat(root_dict, indent=(level + 1)),
                            diff_str))
    for c in root.iterChildren():
        if c is not None:
            yield from print_nodes(c, level + 1)


def assert_parser_node_tree_are_equal(actual, expected):
    try:
        _do_assert_parser_node_tree_are_equal(actual, expected)
    except AssertionError:
        raise ExpectedParserNodeTreeError(actual, expected)


def _do_assert_parser_node_tree_are_equal(actual, expected):
    try:
        assert actual is not None
        assert expected is not None
        assert type(actual) == type(expected)
        assert actual.__class__ == expected.__class__
        attr_names = _get_test_compare_attr_names(actual.__class__)
        for an in attr_names:
            actual_attr_value = getattr(actual, an)
            expected_attr_value = getattr(expected, an)
            assert actual_attr_value == expected_attr_value

        actual_children = [c for c in actual.iterChildren()
                           if c is not None]
        expected_children = [c for c in expected.iterChildren()
                             if c is not None]
        assert len(actual_children) == len(expected_children)
    except AssertionError:
        actual.__test_difference_start__ = True
        raise

    for i, j in zip(actual_children, expected_children):
        _do_assert_parser_node_tree_are_equal(i, j)


def _get_test_compare_attr_names(cls):
    attr_names = []
    while cls:
        try:
            an = getattr(cls, '__test_compare__')
            attr_names += an
        except AttributeError:
            pass

        base_cls = cls.__bases__
        if not base_cls:
            break
        cls = base_cls[0]
    return attr_names
