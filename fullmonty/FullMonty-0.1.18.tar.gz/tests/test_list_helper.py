# coding=utf-8

"""
test the list helper functions
"""
import collections

from fullmonty.list_helper import compress_list, unique_list, is_sequence, flatten


def test_compress_list():
    """
    compress_list removes empty or None elements from a list
    """

    # incompressible lists
    assert compress_list([]) == []
    assert compress_list([1]) == [1]
    assert compress_list([1, 2]) == [1, 2]

    # remove None element
    assert compress_list([None]) == []
    assert compress_list([None, 1]) == [1]
    assert compress_list([None, 1, 2]) == [1, 2]
    assert compress_list([1, None, 2]) == [1, 2]
    assert compress_list([1, 2, None]) == [1, 2]

    # remove empty strings
    assert compress_list(['']) == []
    assert compress_list(['', 1]) == [1]
    assert compress_list(['', 1, 2]) == [1, 2]
    assert compress_list([1, '', 2]) == [1, 2]
    assert compress_list([1, 2, '']) == [1, 2]

    # remove empty lists
    assert compress_list([[]]) == []
    assert compress_list([[], 1]) == [1]
    assert compress_list([[], 1, 2]) == [1, 2]
    assert compress_list([1, [], 2]) == [1, 2]
    assert compress_list([1, 2, []]) == [1, 2]


def test_unique_list():
    """removes duplicate entries in the list"""

    assert unique_list([]) == []
    assert unique_list([1]) == [1]
    assert unique_list([1, 2]) == [1, 2]

    assert unique_list([1, 1]) == [1]
    assert unique_list([1, 1, 1]) == [1]
    assert unique_list([1, 1, 2]) == [1, 2]
    assert unique_list([1, 2, 1]) == [1, 2]
    assert unique_list([2, 1, 1]) == [2, 1]


def test_is_sequence():
    """does the given object behave like a list but is not a string?"""

    # non-list-like objects
    assert not is_sequence(None)
    assert not is_sequence(1)
    assert not is_sequence('')
    assert not is_sequence('foo')

    # list-like objects

    # lists
    assert is_sequence([])
    assert is_sequence([1])
    assert is_sequence([1, 2])
    # tuples
    assert is_sequence(())
    assert is_sequence((1,))
    assert is_sequence((1, 2))


def test_flatten():

    assert isinstance(flatten([1]), collections.Iterable)
    assert isinstance(flatten([1, 2, 3]), collections.Iterable)
    assert isinstance(flatten([1, [2, 3]]), collections.Iterable)
    assert isinstance(flatten(["1"]), collections.Iterable)
    assert isinstance(flatten(["1", "2", "3"]), collections.Iterable)
    assert isinstance(flatten(["1", ["2", "3"]]), collections.Iterable)
    assert isinstance(flatten([u"1"]), collections.Iterable)
    assert isinstance(flatten([u"1", u"2", u"3"]), collections.Iterable)
    assert isinstance(flatten([u"1", [u"2", u"3"]]), collections.Iterable)
    assert isinstance(flatten([b"1"]), collections.Iterable)
    assert isinstance(flatten([b"1", b"2", b"3"]), collections.Iterable)
    assert isinstance(flatten([b"1", [b"2", b"3"]]), collections.Iterable)
    assert list(flatten([[b'user']])) == [b'user']
    assert list(flatten([[u'pass']])) == [u'pass']
    assert list(flatten([b'lab'])) == [b'lab']
    assert list(flatten([u'lab'])) == [u'lab']
