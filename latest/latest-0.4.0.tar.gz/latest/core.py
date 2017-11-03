""":mod:`core` contains core functions for templating.

"""

import pyparsing as pp

from .util import is_scalar, is_vector
from .config import config as Config
from .exceptions import PyExprSyntaxError, ContextError


class Context(dict):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.__dict__ = self


def listify(obj):
    return obj if is_vector(obj) else [obj]


def contextify(obj):

    if is_scalar(obj):
        return obj
    elif is_vector(obj):
        return [contextify(o) for o in obj]
    elif isinstance(obj, dict):
        return Context(dict((k, contextify(v)) for k, v in obj.items()))
    else:
        return obj


def resolve_context(glob, loc):
    if isinstance(loc, dict) or not loc:
        return loc
    elif is_vector(loc):
        return [ns if isinstance(ns, dict) else glob for ns in loc]
    else:
        return glob


class ParserHandler(object):

    def __init__(self, toks):
        self.toks = toks
        if hasattr(self, 'initialize'):
            self.initialize()


class GrammarHandler(ParserHandler):

    def eval(self, context, config=Config, **options):
        if context:
            join = options.get('join', config.join)
            ctx = listify(context)
            return join.join(str().join(tok.eval(ns) for tok in self.toks) for ns in ctx)
        else:
            return str()


class PyExprHandler(ParserHandler):

    def initialize(self):
        self.pyexpr = self.toks[0]

    def eval(self, context):
        try:
            return eval(self.pyexpr, contextify(context))
        except (NameError, AttributeError) as e:
            raise ContextError(e.__str__())
        except SyntaxError as e:
            raise PyExprSyntaxError(e.text)


class StrPyExprHandler(ParserHandler):

    def initialize(self):
        self.pyexpr = self.toks[0]

    def eval(self, context):
        result = self.pyexpr.eval(context)
        return str(result)


class OptHandler(ParserHandler):

    def initialize(self):
        self.key = self.toks[0]
        self.value = self.toks[1]

    def eval(self, context,):
        key, value = self.key, self.value.eval(context) if hasattr(self.value, 'eval') else self.value
        return (key, value)


class OptsHandler(ParserHandler):

    def initialize(self):
        self.opts = self.toks

    def eval(self, context):
        return dict(opt.eval(context) for opt in self.opts)


class EnvHandler(ParserHandler):

    def initialize(self):
        self.context, self.options, self.content = self.toks

    def eval(self, context):
        ctx = resolve_context(context, self.context.eval(context))
        opts = self.options.eval(context)
        return self.content.eval(ctx, **opts)


class TxtHandler(ParserHandler):

    def initialize(self):
        self.txt = self.toks[0]

    def eval(self, context):
        return self.txt


class Grammar(object):

    def __init__(self, config=Config):
        self.config = config
        self.grammar = pp.Forward()
        self.pyexpr_entry = pp.Regex(config.pyexpr_entry).suppress()
        self.pyexpr_exit = pp.Regex(config.pyexpr_exit).suppress()
        self.pyexpr = self.pyexpr_entry + pp.SkipTo(self.pyexpr_exit) + self.pyexpr_exit
        self.pyexpr.addParseAction(PyExprHandler)
        self.opt_key = pp.Word(pp.alphas)
        self.opt_value = self.pyexpr | pp.Word(pp.alphas)
        self.opt = self.opt_key + pp.Suppress('=') + self.opt_value
        self.opt.addParseAction(OptHandler)
        self.opts_list = pp.delimitedList(self.opt, delim=',')
        self.opts_entry = pp.Regex(config.opts_entry).suppress()
        self.opts_exit = pp.Regex(config.opts_exit).suppress()
        self.opts = pp.Optional(self.opts_entry + self.opts_list + self.opts_exit)
        self.opts.addParseAction(OptsHandler)
        self.str_pyexpr_entry = pp.Regex(config.str_pyexpr_entry).suppress()
        self.str_pyexpr_exit = pp.Regex(config.str_pyexpr_exit).suppress() if config.str_pyexpr_exit else pp.Empty()
        self.str_pyexpr = self.str_pyexpr_entry + self.pyexpr + self.str_pyexpr_exit
        self.str_pyexpr.addParseAction(StrPyExprHandler)
        self.opt_space = pp.Optional(pp.Regex(r'\s')).suppress()
        self.env_entry = pp.Regex(config.env_entry).suppress()
        self.env_exit = self.opt_space + pp.Regex(config.env_exit).suppress()
        self.env = self.env_entry + self.pyexpr + self.opts + self.opt_space + self.grammar + self.env_exit
        self.env.addParseAction(EnvHandler)
        self.keyword = self.env_entry | self.env_exit
        self.struct = self.str_pyexpr | self.env
        self.char = ~self.keyword + ~self.struct + pp.Regex(r'[\s\S]')
        self.chars = pp.OneOrMore(self.char)
        self.txt = pp.Combine(self.chars)
        self.txt.addParseAction(TxtHandler)
        self.struct.leaveWhitespace()
        self.txt.leaveWhitespace()
        self.element = self.struct | self.txt
        self.grammar << pp.ZeroOrMore(self.element)
        self.grammar.addParseAction(GrammarHandler)

    def eval(self, template, context):
        toks = self.grammar.parseString(template)
        ast = toks[0]
        return ast.eval(context, self.config)
