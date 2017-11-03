import pytest
try:
    import configparser
except:
    import ConfigParser as configparser

from latest.util import *


@pytest.fixture(params=[
    (bool(), True, False, False),
    (int(), True, False, False),
    (float(), True, False, False),
    (complex(), True, False, False),
    (str(), True, False, False),
    (list(), False, True, False),
    (tuple(), False, True, False),
    (set(), False, True, False),
    (frozenset(), False, True, False),
    (dict(), False, False, True),
    (object(), False, False, True),
])
def typecheck_data(request):
    return request.param


def test_typecheck(typecheck_data):
    obj, isscalar, isvector, istensor = typecheck_data
    assert is_scalar(obj) == isscalar
    assert is_vector(obj) == isvector
    assert is_tensor(obj) == istensor


@pytest.fixture(params=[
    ('.', os.getcwd()),
    ('~', os.path.expanduser('~')),
])
def path_data(request):
    return request.param


def test_path(path_data):
    loc, result = path_data
    assert path(loc) == result


@pytest.fixture
def parser(config_file):
    parser = configparser.RawConfigParser()
    parser.read(config_file)
    return parser


@pytest.fixture(params=[
    # section, key, default, result
    ('section', 'key', 'default', 'value'),
    ('section', 'false_key', 'default', 'default'),
    ('false_section', 'key', 'default', 'default'),
])
def getopt_data(request):
    return request.param


def test_getopt(parser, getopt_data):
    section, key, default, result = getopt_data
    assert getopt(parser, section, key, default=default) == result
