from frasco.testsuite import FrascoTestCase
from frasco.expression import Parser, Expression
from frasco.utils import AttrDict


class ExpressionTestCase(FrascoTestCase):
    def assert_nodes(self, results, nodes):
        if len(nodes) != len(results):
            raise AssertionError("Nodes lists are not of the same length")
        for i in xrange(0, len(nodes)):
            if nodes[i] != repr(results[i]):
                raise AssertionError("Node do not match, got '%s', expected '%s'" % (repr(results[i]), nodes[i]))

    def test_parser(self):
        p = Parser()
        self.assert_nodes(p.parse("hello world"), ["DataNode(hello world)"])
        self.assert_nodes(p.parse("$foo"), ["VarNode(foo)"])
        self.assert_nodes(p.parse("$foo str"), ["VarNode(foo)", "DataNode( str)"])
        self.assert_nodes(p.parse("\$foo str"), ["DataNode($foo str)"])
        self.assert_nodes(p.parse("hello${foo}world"), ["DataNode(hello)", "VarNode(foo)", "DataNode(world)"])
        self.assert_nodes(p.parse("$foo.bar"), ["GetAttrNode(VarNode(foo), bar)"])
        self.assert_nodes(p.parse("$foo[bar]"), ["GetItemNode(VarNode(foo), bar)"])
        self.assert_nodes(p.parse("$foo.bar[baz]"), ["GetItemNode(GetAttrNode(VarNode(foo), bar), baz)"])
        self.assert_nodes(p.parse("$foo[bar].baz"), ["GetAttrNode(GetItemNode(VarNode(foo), bar), baz)"])
        self.assert_nodes(p.parse("!$foo"), ["NotNode(VarNode(foo))"])
        self.assert_nodes(p.parse("$foo|20"), ["DefaultNode(VarNode(foo), '20')"])
        self.assert_nodes(p.parse("$foo|$bar"), ["DefaultNode(VarNode(foo), VarNode(bar))"])
        self.assert_nodes(p.parse("$foo && $bar"), ["AndNode(VarNode(foo), VarNode(bar))"])
        self.assert_nodes(p.parse("$foo || $bar"), ["OrNode(VarNode(foo), VarNode(bar))"])
        self.assert_nodes(p.parse("$foo || $bar && $baz"), ["OrNode(VarNode(foo), AndNode(VarNode(bar), VarNode(baz)))"])
        self.assert_nodes(p.parse("$foo && !$bar"), ["AndNode(VarNode(foo), NotNode(VarNode(bar)))"])
        self.assert_nodes(p.parse("$foo && $bar|20"), ["AndNode(VarNode(foo), DefaultNode(VarNode(bar), '20'))"])
        self.assert_nodes(p.parse("{{ 2 + 2 }}"), ["EvalNode(2 + 2)"])

    def test_compile(self):
        p = Parser()
        self.assert_isinstance(p.compile("hello world"), str)
        self.assert_isinstance(p.compile("hello $name"), Expression)

    def test_eval_expression(self):
        p = Parser()
        c = {"foo": "hello", "t": True, "f": False, "data": AttrDict({"a": "aa", "b": {"c": "cc"}})}
        self.assert_equal(p.compile("$foo").eval(c), "hello")
        self.assert_equal(p.compile("$data.a").eval(c), "aa")
        self.assert_equal(p.compile("$data[a]").eval(c), "aa")
        self.assert_equal(p.compile("$data.b[c]").eval(c), "cc")
        self.assert_false(p.compile("!$t").eval(c))
        self.assert_false(p.compile("$t && $f").eval(c))
        self.assert_true(p.compile("$t || $f").eval(c))
        self.assert_equal(p.compile("{{ 2 + 2 }}").eval(c), 4)
        self.assert_equal(p.compile("$undefined|hi").eval(c), "hi")