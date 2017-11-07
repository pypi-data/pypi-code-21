import re
from .utils import import_string
import datetime


class MissingVarError(Exception):
    pass


class Node(object):
    pass


class DataNode(Node):
    """An AST node representing some string data
    """
    def __init__(self, data):
        self.data = data

    def eval(self, context):
        return self.data

    def __repr__(self):
        return "DataNode(%s)" % self.data


class VarNode(Node):
    """An AST node representing a variable from the context
    """
    def __init__(self, name):
        self.name = name

    def eval(self, context):
        return context.get(self.name)

    def __repr__(self):
        return "VarNode(%s)" % self.name


class GetAttrNode(Node):
    """An AST node representing accessing an attribute of the child node
    """
    def __init__(self, node, attr):
        self.node = node
        self.attr = attr

    def eval(self, context):
        obj = self.node.eval(context)
        if obj:
            return getattr(obj, self.attr, None)

    def __repr__(self):
        return "GetAttrNode(%s, %s)" % (repr(self.node), self.attr)


class GetItemNode(Node):
    """An AST node representing accessing an item of the child node
    """
    def __init__(self, node, item):
        self.node = node
        self.item = item

    def eval(self, context):
        obj = self.node.eval(context)
        item = self.item
        if isinstance(item, Node):
            item = item.eval(context)
        try:
            return obj[item]
        except KeyError:
            pass

    def __repr__(self):
        return "GetItemNode(%s, %s)" % (repr(self.node), self.item)


class CallNode(Node):
    """An AST node representing calling a method of the child node
    """
    def __init__(self, node, method=None):
        self.node = node
        self.method = method

    def eval(self, context):
        obj = self.node.eval(context)
        if self.method is None:
            return obj()
        if not hasattr(obj, self.method):
            raise MissingVarError("Unknwon method '%' in option value" % self.method)
        return getattr(obj, self.method)()

    def __repr__(self):
        return "CallNode(%s, %s)" % (repr(self.node), self.method)


class DefaultNode(Node):
    """An AST node representing a default value for a missing variable
    """
    def __init__(self, node, default):
        self.node = node
        self.default = default

    def eval(self, context):
        try:
            value = self.node.eval(context)
            if value is not None:
                return value
        except:
            pass
        if isinstance(self.default, Node):
            return self.default.eval(context)
        return self.default

    def __repr__(self):
        return "DefaultNode(%s, %s)" % (repr(self.node), repr(self.default))


class NotNode(Node):
    """An AST node representing "not"
    """
    def __init__(self, node):
        self.node = node

    def eval(self, context):
        return not self.node.eval(context)

    def __repr__(self):
        return "NotNode(%s)" % repr(self.node)


class AndNode(Node):
    """An AST node representing "&&"
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, context):
        return self.left.eval(context) and self.right.eval(context)

    def __repr__(self):
        return "AndNode(%s, %s)" % (repr(self.left), repr(self.right))


class OrNode(Node):
    """An AST node representing "||"
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def eval(self, context):
        return self.left.eval(context) or self.right.eval(context)

    def __repr__(self):
        return "OrNode(%s, %s)" % (repr(self.left), repr(self.right))


class EvalNode(Node):
    """An AST node representing an eval expression.
    These expressions can use import(module_name) which will return
    a module.
    """
    import_regexp = re.compile(r"(import\(([a-z.]+)\))")

    def __init__(self, expr, catch_errors=True):
        self.expr = expr
        self.catch_errors = catch_errors
        for import_expr, name in self.import_regexp.findall(self.expr):
            self.expr = self.expr.replace(import_expr, "__import_module('%s')" % name)

    def eval(self, context):
        ctx = dict(context, __import_module=lambda n: import_string(n), datetime=datetime)
        try:
            return eval(self.expr, globals(), ctx)
        except:
            if not self.catch_errors:
                raise
            return None

    def __repr__(self):
        return "EvalNode(%s)" % self.expr


class ExpressionSyntaxError(Exception):
    pass


class Parser(object):
    """Parses a string and generates an AST
    Variables can be used using the dollar sign in front of their name. Attributes
    and items can be accessed as usual. Item names do not need to be strings (ie. use [foo] instead of ["foo"]).
    It is also possible to eval python code enclosed in {{ }}.
    """
    vars_regexp = re.compile(r"(\!?(?<!\\)\$\{?([a-zA-Z0-9_]+)(\(\))*(((\.[a-zA-Z0-9_]+(\(\))*)*(\[\$*[a-zA-Z_.0-9]+\])*)*)\}?)")
    eval_regexp = re.compile(r"\{\{([^}]+)\}\}")
    getattr_regexp = re.compile(r"\.([a-zA-Z0-9_]+)")
    getitem_regexp = re.compile(r"\[(\$*[a-zA-Z_.0-9]+)\]")
    call_regexp = re.compile(r"\.([a-zA-Z0-9_]+)\(\)")
    default_regexp = re.compile(r"([a-zA-Z0-9]+)")
    operators_regexps = [(re.compile(r" && "), AndNode), (re.compile(r" \|\| "), OrNode)]
    special_chars = [('\$', '$'), ('\|\|', '||'), ('\&\&', '&&')]

    def __init__(self):
        self.regexps = [(self.eval_regexp, self.parse_eval), (self.vars_regexp, self.parse_var)]

    def compile(self, expr, force_expr=False):
        if isinstance(expr, list):
            return self.compile_list(expr, force_expr)
        if isinstance(expr, dict):
            return self.compile_dict(expr, force_expr)
        if not isinstance(expr, (str, unicode)):
            return expr

        ast = self.parse(expr)
        if not force_expr and len(ast) == 1 and isinstance(ast[0], DataNode):
            return expr
        return Expression(ast, expr)

    def compile_list(self, lst, force_expr=False):
        rv = []
        for item in lst:
            rv.append(self.compile(item, force_expr))
        return rv

    def compile_dict(self, dct, force_expr=False):
        rv = {}
        for k, v in dct.iteritems():
            rv[k] = self.compile(v, force_expr)
        return rv

    def parse(self, expr):
        self.expr = expr
        nodes = []
        while True:
            match = False
            for regexp, func in self.regexps:
                r = regexp.search(expr)
                if r:
                    before_expr = expr[:r.start()]
                    if before_expr != "":
                        nodes.append(DataNode(self.cleanup_special_chars(before_expr)))
                    node, expr = func(r, expr[r.end():])
                    nodes.append(node)
                    match = True
                    break
            if match:
                continue
            if expr != "":
                nodes.append(DataNode(self.cleanup_special_chars(expr)))
            break

        return nodes

    def cleanup_special_chars(self, expr):
        for a, b in self.special_chars:
            expr = expr.replace(a, b)
        return expr

    def parse_var(self, match, remaining=None):
        node = VarNode(match.group(2))
        if match.group(3) is not None:
            node = CallNode(node)
        access = match.group(4)
        if access != "":
            node = self.parse_accessors(access, node)
        if match.group(1).startswith("!"):
            node = NotNode(node)

        if remaining is None:
            return node

        if remaining.startswith("|"):
            remaining = remaining[1:]
            m = self.vars_regexp.match(remaining)
            if m:
                node = DefaultNode(node, self.parse_var(m))
                remaining = remaining[m.end():]
            else:
                m = self.default_regexp.match(remaining)
                if not m:
                    raise ExpressionSyntaxError("Missing default value after default operator in '%s'" % self.expr)
                node = DefaultNode(node, m.group(1))
                remaining = remaining[m.end():]

        for regexp, node_cls in self.operators_regexps:
            r = regexp.match(remaining)
            if r:
                remaining = remaining[r.end():]
                match = self.vars_regexp.match(remaining)
                if not match:
                    raise ExpressionSyntaxError("Operators can only be used between variables in '%s'" % self.expr)
                right_node, remaining = self.parse_var(match, remaining[match.end():])
                node = node_cls(node, right_node)

        return (node, remaining)

    def parse_accessors(self, expr, node):
        r = self.call_regexp.match(expr)
        if r:
            return self.parse_accessors(expr[r.end():], CallNode(node, r.group(1)))

        r = self.getattr_regexp.match(expr)
        if r:
            return self.parse_accessors(expr[r.end():], GetAttrNode(node, r.group(1)))

        r = self.getitem_regexp.match(expr)
        if r:
            item = r.group(1)
            if item.startswith("$"):
                item = self.parse_var(item)
            return self.parse_accessors(expr[r.end():], GetItemNode(node, item))

        return node

    def parse_eval(self, match, remaining):
        return (EvalNode(match.group(1).strip()), remaining)


class Expression(object):
    """Represents an option value which needs to be evald
    """
    def __init__(self, ast, expr=None):
        self.ast = ast
        self.expr = expr

    def eval(self, context, text_type=unicode):
        result = []
        for node in self.ast:
            result.append(node.eval(context))
        if len(result) == 1:
            return result[0]
        return text_type("").join(map(text_type, result))

    def __str__(self):
        return self.expr

    def __repr__(self):
        return "<Expression(%s)>" % self.expr


def compile_expr(expr):
    """Compiles an expression
    """
    return Parser().compile(expr)


def eval_expr(expr, context):
    """Recursively evaluates a compiled expression using the specified context.
    Dict instances can contain a "__kwargs" key which will be used to update the
    dict with its content
    """
    if isinstance(expr, list):
        rv = []
        for item in expr:
            rv.append(eval_expr(item, context))
        return rv
    if isinstance(expr, dict):
        rv = {}
        for k, v in expr.iteritems():
            rv[k] = eval_expr(v, context)
        kwargs = rv.pop("__kwargs", None)
        if kwargs:
            rv.update(kwargs)
        return rv
    if isinstance(expr, Expression):
        return expr.eval(context)
    return expr