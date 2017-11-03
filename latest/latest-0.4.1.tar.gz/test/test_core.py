import pytest
import yaml

from latest.core import *


@pytest.fixture(scope='module')
def grammar():
    return Grammar()


@pytest.fixture(scope='module')
def context(data_file):
    with open(data_file, 'r') as f:
        data = yaml.load(f)
        return contextify(data)


@pytest.fixture(params=[
    # expr, result
    (' 2 * 2 ', 4),
    (' 2 * data.scalar ', 6),
    (' sum(data.vector) ', 6),
    (' data.vector ', [1, 2, 3]),
    (' data.tensor.true + data.tensor.false ', 1),
    (' * ', PyExprSyntaxError),
    (' x ', ContextError),
])
def pyexpr_data(request):
    return request.param


def test_pyexpr(grammar, context, pyexpr_data):
    pyexpr, result = r'{$' + pyexpr_data[0] + r'$}', pyexpr_data[1]
    toks = grammar.pyexpr.parseString(pyexpr)
    handler = toks[0]
    try:
        assert handler.eval(context) == result
    except Exception as e:
        assert e.__class__ == result


@pytest.fixture(params=[
    (' 2 * 2 ', '4'),
    (' data.scalar ', '3'),
    (' * ', PyExprSyntaxError),
    (' x ', ContextError),
])
def str_pyexpr_data(request):
    return request.param


def test_str_pyexpr(grammar, context, str_pyexpr_data):
    str_pyexpr, result = r'\latest{$' + str_pyexpr_data[0] + r'$}', str_pyexpr_data[1]
    toks = grammar.str_pyexpr.parseString(str_pyexpr)
    handler = toks[0]
    try:
        assert handler.eval(context) == result
    except Exception as e:
        assert e.__class__ == result


@pytest.fixture(params=[
    # context, options, content, result
    (r'\begin{latest}{$ data $}\latest{$ scalar $}\end{latest}', '3'),
    (r'\begin{latest}{$ [{"n": n} for n in data.vector] $}\latest{$ n $}\end{latest}', '123'),
])
def env_data(request):
    return request.param


def test_env(grammar, context, env_data):
    env, result = env_data
    toks = grammar.env.parseString(env)
    handler = toks[0]
    try:
        assert handler.eval(context) == result
    except Exception as e:
        assert e.__class__ == result


@pytest.fixture(params=[
    (r'scalar = \latest{$ data.scalar $}', 'scalar = 3'),
    (r'\begin{latest}{$ [{"n": n} for n in data.vector] $}\latest{$ n $}\end{latest}, bla', '123, bla'),
])
def grammar_data(request):
    return request.param


def test_grammar(grammar, context, grammar_data):
    (g, result) = grammar_data
    toks = grammar.grammar.parseString(g)
    handler = toks[0]
    try:
        assert handler.eval(context) == result
    except Exception as e:
        assert e.__class__ == result
