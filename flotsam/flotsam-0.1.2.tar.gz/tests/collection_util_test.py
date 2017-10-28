import flotsam.collection_util as sut

import pytest


@pytest.fixture
def int_dict():
    return {3: 4, 1: 2}


@pytest.fixture
def str_dict():
    return {'three': 'four', 'one': 'two'}


class Dummy:

    """Dummy class to test dictionary of instances
    """

    def __init__(self, val):
        self._val = val

    def __repr__(self):
        return 'Dummy_{}'.format(self._val)


@pytest.fixture
def instance_dict():
    return {3: Dummy(1), 1: Dummy(2)}


@pytest.fixture
def dict_dict():
    return {3: {7: 8, 5: 6}, 1: {11: 12, 9: 10}}


def test_empty():
    assert sut.pretty_dict({}) == '{}'


def test_ints(int_dict):
    expected = "{1: 2, 3: 4}"
    assert sut.pretty_dict(int_dict) == expected


def test_strings(str_dict):
    expected = "{one: two, three: four}"
    assert sut.pretty_dict(str_dict) == expected


def test_instances(instance_dict):
    expected = "{1: Dummy_2, 3: Dummy_1}"
    assert sut.pretty_dict(instance_dict) == expected


def test_dict_dict(dict_dict):
    expected = "{1: {9: 10, 11: 12}, 3: {5: 6, 7: 8}}"
    assert sut.pretty_dict(dict_dict) == expected
