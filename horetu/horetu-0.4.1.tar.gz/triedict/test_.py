import pytest
from . import triedict, AmbiguousKey, KeyNotFound

@pytest.fixture
def w():
    return triedict(key='value')

@pytest.fixture
def x():
    return triedict(chain=1, chainsaw=2, calque=3, loanword=4)

@pytest.fixture
def y():
    return triedict({
        (1, 2): 'a',
        (1, 2, 3): 'b',
        (10, 11, 12, 13): 'c',
    })

@pytest.fixture
def z():
    return triedict(a_b=1, a_bcdef=2, a_bbb=3, aaaaaaaaa=4, aaabb=5)

def test_key_str(x):
    assert x.key('lo') == 'loanword'
def test_key_tuple(y):
    assert y.key((10,)) == (10, 11, 12, 13)

@pytest.mark.parametrize('key, value', [
    ('a', AmbiguousKey),
    ('a_b', 1),
    ('a_bc', 2),
    ('aaxbb', KeyNotFound),
    ('aaaaaaa', 4),
    ('aaaaaaaaaaaaaaa', KeyNotFound),
])
def test_errors(z, key, value):
    if isinstance(value, type) and issubclass(value, Exception):
        with pytest.raises(value):
            z[key]
    else:
        assert z[key] == value

_argvalues = [
    ('aoeu', True),
    (b'aoeu', False),
    (1234, False),
]
@pytest.mark.parametrize('key, ok', _argvalues)
def test_check_type(x, key, ok):
    if ok:
        x._check_type(key)
    else:
        with pytest.raises(TypeError):
            x._check_type(key)

def test_repr(x):
    assert 'triedict(' in repr(x)
    assert 'chainsaw\', 2' in repr(x)

def test_getitem(x):
    assert x['chain'] == 1
    with pytest.raises(AmbiguousKey):
        x['chai']
    assert x['calque'] == 3
    assert x['l'] == 4

def test_setitem(x):
    x['aoeu'] = 9
    x._trie['a']['o']['e']['u'][None] == 9

def test_delitem(x):
    with pytest.raises(NotImplementedError):
        del(x['printer'])

def test_iter(x):
    assert list(sorted(x)) == ['calque', 'chain', 'chainsaw', 'loanword']

def test_len(x):
    assert len(x) == 4

_cases = [
    ('key', 'value'),
    ('u', KeyNotFound),
    ('', 'value'),
]
@pytest.mark.parametrize('k, v', _cases)
def test_getitem_one(w, k, v):
    if isinstance(v, type) and issubclass(v, Exception):
        with pytest.raises(v):
            w[k]
    else:
        assert w[k] == v

def test_getitem_tuple(y):
    assert y[(10,)] == 'c'

def test_iter_tuple(y):
    assert list(sorted(y)) == [
        (1, 2),
        (1, 2, 3),
        (10, 11, 12, 13),
    ]
