from cytoolz import first
from cytoolz import second
from merlin import functions as f
import pytest


def test_extract():
    inputs = [1, (2, 3, (4, 5)), 6]
    assert f.extract(inputs, [0]) == 1
    assert f.extract(inputs, [1]) == (2, 3, (4, 5))
    assert f.extract(inputs, [1, 0]) == 2
    assert f.extract(inputs, [1, 1]) == 3
    assert f.extract(inputs, [1, 2]) == (4, 5)
    assert f.extract(inputs, [1, 2, 0]) == 4


def test_flatten():
    result = [1, 2, 3, 4, 5, [6, 7]]
    assert list(f.flatten([[1, 2], [3, 4], [5, [6, 7]]])) == result


def test_intersection():
    items = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    assert f.intersection(items) == {3}


def test_minbox():
    one = {'ulx': 0, 'uly': 0, 'lrx': 0, 'lry': 0}
    assert f.minbox(((0,0),)) == one

    two = {'ulx': 0, 'uly': 10, 'lrx': 10, 'lry': 0}
    assert f.minbox(((0,0), (10, 10))) == two

    three = {'ulx': -50, 'uly': 3, 'lrx': 10, 'lry': -8}
    assert f.minbox(((-50,0), (10, 3), (5, -8))) == three

    four = {'ulx': -5, 'uly': 33, 'lrx': 111, 'lry': -66}
    assert f.minbox(((0, 11), (-5, -5), (3, 33), (111, -66))) == four

    five = {'ulx': -5 , 'uly': 5 , 'lrx': 4 , 'lry': -4 }
    assert f.minbox(((1, 1), (2, 2), (-3, -3), (4, -4), (-5, 5))) == five


def test_sha256():
    assert type(f.sha256('kowalski')) is str


def test_md5():
    assert type(f.md5('kowalski')) is str


def test_simplify_objects():
    assert 1 > 0


def test_sort():
    assert f.sort([2, 1, 3]) == [1, 2, 3]


def test_rsort():
    assert f.rsort([2, 1, 3]) == [3, 2, 1]


def test_serialization():

    def serialize_deserialize(t):
        assert f.deserialize(second(f.serialize(t))) == t

    targets = ['farva', 1, 2.0, True, None]

    all(map(serialize_deserialize, targets))


def test_flip_keys():
    dods = {'a': {1: 'a1', 2: 'a2'},
            'b': {1: 'b1', 2: 'b2'},
            'c': {1: 'c1', 2: 'c2'}}

    result = {1: {'a': 'a1', 'b': 'b1', 'c': 'c1'},
              2: {'a': 'a2', 'b': 'b2', 'c': 'c2'}}

    assert f.flip_keys(dods) == result


def test_cqlstr():
    assert f.cqlstr('-:.') == '___'


def test_represent():

    def ramrod():
        pass

    assert f.represent(ramrod) == "'ramrod'"
    assert f.represent('ramrod') == "'ramrod'"
    assert f.represent(1) == '1'
    assert f.represent(None) == 'None'


def test_isnumeric():
    good = ['1', '-1', '0', '1.0', '-1.0']
    assert all(map(f.isnumeric, good))

    bad = ['a', 'a1', '1a']
    assert not any(map(f.isnumeric, bad))


def test_seqeq():
    assert f.seqeq([1, 2, 3], [2, 3, 1]) is True
    assert f.seqeq({1, 2, 3}, [2, 3, 1]) is True
    assert f.seqeq(tuple([3, 2, 1]), [1, 2, 3]) is True
    assert f.seqeq([1,], [1, 2, 3]) is False
    assert f.seqeq([1, 2, 3], [1,]) is False


def test_issubset():
    assert f.issubset([1, 2], [3, 1, 2]) is True
    assert f.issubset(tuple([2, 1]), [3, 2, 1]) is True
    assert f.issubset({'a': 1, 'b': 2}, {'a': 1, 'c': 3, 'b': 2}) is True
    assert f.issubset([3, 2, 1], [3, 2]) is False


def test_difference():
    a = [1, 2, 3]
    b = [1, 2]
    assert f.difference(a, b) == {3}
    assert f.difference(b, a) == set()


def test_chexists():

    # simple check function that will return the first list
    def check_fn(dictionary):
        return dictionary[first(dictionary)]

    # simulate assymetric list values, telling chexists 'c' is supposed to be
    # bigger.
    d = {'a': [1, 2, 3], 'b': [1, 2, 3], 'c': [1, 2, 3, 4, 5]}
    assert f.chexists(d, ['c'], check_fn) == d['a']

    # make sure we throw an exception if c does not contain all values from
    # check_fn
    with pytest.raises(Exception):
        d = {'a': [1, 2, 3], 'b': [1, 2, 3], 'c': [1, 2, 4, 5]}
        assert f.chexists(d, ['c'], check_fn) == d['a']
